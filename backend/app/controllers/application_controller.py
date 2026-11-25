
import re
import hashlib
import secrets
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import Application
from app.models.partner_store import PartnerStore
from app.models.partner_contributor import PartnerContributor
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationCreated, ApplicationListResponse, ConsultaCpf
from app.services.cep_service import limpar_cep, obter_uf_por_cep
from app.services.collaborator_service import modalidade_autorizada
from app.services.qualificacao_service import cpf_valido, pre_qualificado
from app.middleware.rate_limit import verificar_limite_consulta

router = APIRouter(prefix="/solicitacoes", tags=["Solicitações"])

TIPOS_CARTAO = {"DM", "LOJA_FISICA", "LOJA_DIGITAL"}


def somente_numeros(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


@router.post("/", response_model=ApplicationCreated, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(solicitacao: ApplicationCreate, db: Session = Depends(get_db)):
    nome = solicitacao.nome.strip()
    cpf = somente_numeros(solicitacao.cpf)
    telefone = somente_numeros(solicitacao.telefone)
    cep = limpar_cep(solicitacao.cep)
    tipo_cartao = solicitacao.tipo_cartao

    if len(nome) < 3:
        raise HTTPException(status_code=400, detail="Informe seu nome completo.")
    if not cpf_valido(cpf):
        raise HTTPException(status_code=400, detail="CPF inválido.")
    if len(telefone) < 10 or len(telefone) > 11:
        raise HTTPException(status_code=400, detail="Telefone deve conter 10 ou 11 números.")
    if len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP deve conter 8 números.")
    if tipo_cartao not in TIPOS_CARTAO:
        raise HTTPException(status_code=400, detail="Tipo de cartão inválido.")

    loja = None
    contribuidor = None

    if tipo_cartao == "LOJA_FISICA" or (tipo_cartao == "LOJA_DIGITAL" and solicitacao.loja_id):
        if not solicitacao.loja_id:
            raise HTTPException(status_code=400, detail="Escolha uma loja parceira.")

        loja = db.query(PartnerStore).filter(
            PartnerStore.id == solicitacao.loja_id,
            PartnerStore.ativo.is_(True)
        ).first()

        if not loja:
            raise HTTPException(status_code=404, detail="Loja parceira não encontrada.")

        if loja.modalidade != tipo_cartao or (loja.programa and (not loja.programa.ativo or not loja.programa.rede.ativo)):
            raise HTTPException(400, "Esta unidade não oferece a modalidade solicitada.")
        if tipo_cartao == "LOJA_FISICA":
            try:
                uf_cliente = obter_uf_por_cep(cep)
            except ValueError as erro:
                raise HTTPException(400, str(erro)) from erro
            if loja.estado != uf_cliente:
                raise HTTPException(400, "A loja escolhida não pertence ao estado do CEP informado.")

        if solicitacao.contribuidor_id is not None:
            contribuidor = db.query(PartnerContributor).filter(
                PartnerContributor.id == solicitacao.contribuidor_id,
                PartnerContributor.loja_id == loja.id,
                PartnerContributor.ativo.is_(True)
            ).first()

            if not contribuidor:
                raise HTTPException(status_code=400, detail="Contribuidor inválido, inativo ou pertencente a outra loja.")

    elif solicitacao.loja_id is not None or solicitacao.contribuidor_id is not None:
        raise HTTPException(status_code=400, detail="Esse cartão não permite selecionar loja ou contribuidor.")

    usuario_cpf = db.query(User).filter(User.cpf == cpf).with_for_update().first()
    usuario_email = db.query(User).filter(User.email == str(solicitacao.email)).first()
    if usuario_cpf or usuario_email:
        if not usuario_cpf or not usuario_email or usuario_cpf.id != usuario_email.id:
            raise HTTPException(409, "Não foi possível utilizar esses dados cadastrais.")
    usuario = usuario_cpf
    modalidade_permitida = modalidade_autorizada(cpf, db)
    colaborador = modalidade_permitida is not None

    try:
        if usuario is None:
            usuario = User(nome=nome, cpf=cpf, email=str(solicitacao.email), telefone=telefone, cep=cep, colaborador_dm=colaborador)
            db.add(usuario)
            db.flush()

        status_solicitacao = "EM_ANALISE"
        if colaborador:
            status_solicitacao = "APROVADO" if tipo_cartao == modalidade_permitida else "REPROVADO"
        elif pre_qualificado(cpf, tipo_cartao):
            status_solicitacao = "APROVADO"

        programa_id = loja.programa_id if loja else None
        chave = None
        if status_solicitacao != "REPROVADO":
            grupo = f"programa:{programa_id}" if programa_id else (f"loja:{loja.id}" if loja else tipo_cartao)
            chave = f"{usuario.id}:{tipo_cartao}:{grupo}"
            anteriores = db.query(Application).filter(Application.usuario_id == usuario.id, Application.tipo_cartao == tipo_cartao, Application.status.in_(["APROVADO", "EM_ANALISE"]))
            if programa_id:
                anteriores = anteriores.filter(or_(Application.programa_id == programa_id, Application.loja_id.in_(db.query(PartnerStore.id).filter(PartnerStore.programa_id == programa_id))))
            elif loja:
                anteriores = anteriores.filter(Application.loja_id == loja.id)
            else:
                anteriores = anteriores.filter(Application.loja_id.is_(None))
            if anteriores.first():
                raise HTTPException(409, "Já existe uma solicitação ativa para este cartão. Use seu código de acompanhamento.")

        codigo = secrets.token_urlsafe(24)
        nova_solicitacao = Application(
            usuario_id=usuario.id, tipo_cartao=tipo_cartao,
            loja_id=loja.id if loja else None,
            contribuidor_id=contribuidor.id if contribuidor else None,
            programa_id=programa_id, chave_ativa=chave,
            codigo_consulta_hash=hashlib.sha256(codigo.encode()).hexdigest(),
            status=status_solicitacao
        )
        db.add(nova_solicitacao)
        db.commit()
        db.refresh(nova_solicitacao)
        resposta = ApplicationResponse.model_validate(nova_solicitacao).model_dump()
        return {**resposta, "codigo_consulta": codigo}
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Cadastro ou solicitação já existente.") from erro


@router.get("/{solicitacao_id}", response_model=ApplicationResponse)
def buscar_solicitacao(solicitacao_id: int, request: Request, cpf: str = Query(min_length=11, max_length=14), codigo: str = Query(min_length=20, max_length=120), db: Session = Depends(get_db)):
    verificar_limite_consulta(request)
    pedido = db.query(Application).join(User).filter(Application.id == solicitacao_id, User.cpf == somente_numeros(cpf), Application.codigo_consulta_hash == hashlib.sha256(codigo.encode()).hexdigest()).first()
    if not pedido:
        raise HTTPException(404, "Solicitação não encontrada.")
    return pedido


@router.post("/consultar", response_model=ApplicationListResponse)
def consultar_solicitacoes_por_cpf(consulta: ConsultaCpf, request: Request, pagina: int = Query(default=1, ge=1, le=1000), db: Session = Depends(get_db)):
    verificar_limite_consulta(request)
    pedido = db.query(Application).join(User).filter(User.cpf == somente_numeros(consulta.cpf), Application.codigo_consulta_hash == hashlib.sha256(consulta.codigo.encode()).hexdigest()).first()
    return {"total": 1 if pedido else 0, "solicitacoes": [pedido] if pedido and pagina == 1 else []}
