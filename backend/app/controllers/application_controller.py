import re
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import Application
from app.models.partner_store import PartnerStore
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationListResponse, ConsultaCpf
from app.services.cep_service import limpar_cep, obter_uf_por_cep
from app.services.collaborator_service import modalidade_autorizada
from app.middleware.rate_limit import verificar_limite_consulta

router = APIRouter(prefix="/solicitacoes", tags=["Solicitações"])

TIPOS_CARTAO = {"DM", "LOJA_FISICA", "LOJA_DIGITAL"}


def somente_numeros(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(solicitacao: ApplicationCreate, db: Session = Depends(get_db)):
    nome = solicitacao.nome.strip()
    cpf = somente_numeros(solicitacao.cpf)
    telefone = somente_numeros(solicitacao.telefone)
    cep = limpar_cep(solicitacao.cep)
    tipo_cartao = solicitacao.tipo_cartao

    if len(nome) < 3:
        raise HTTPException(status_code=400, detail="Informe seu nome completo.")
    if len(cpf) != 11:
        raise HTTPException(status_code=400, detail="CPF deve conter 11 números.")
    if len(telefone) < 10 or len(telefone) > 11:
        raise HTTPException(status_code=400, detail="Telefone deve conter 10 ou 11 números.")
    if len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP deve conter 8 números.")
    if tipo_cartao not in TIPOS_CARTAO:
        raise HTTPException(status_code=400, detail="Tipo de cartão inválido.")

    loja = None
    if tipo_cartao == "LOJA_FISICA":
        if not solicitacao.loja_id:
            raise HTTPException(status_code=400, detail="Escolha uma loja parceira.")

        loja = db.query(PartnerStore).filter(
            PartnerStore.id == solicitacao.loja_id,
            PartnerStore.ativo.is_(True),
        ).first()

        if not loja:
            raise HTTPException(status_code=404, detail="Loja parceira não encontrada.")

        try:
            uf_cliente = obter_uf_por_cep(cep)
        except ValueError as erro:
            raise HTTPException(status_code=400, detail=str(erro)) from erro

        if loja.estado != uf_cliente:
            raise HTTPException(
                status_code=400,
                detail="A loja escolhida não pertence ao estado do CEP informado.",
            )

    if tipo_cartao != "LOJA_FISICA" and solicitacao.loja_id is not None:
        raise HTTPException(status_code=400, detail="Esse cartão não permite selecionar loja física.")

    usuario_cpf = db.query(User).filter(User.cpf == cpf).first()
    usuario_email = db.query(User).filter(User.email == str(solicitacao.email)).first()

    if usuario_cpf and usuario_email and usuario_cpf.id != usuario_email.id:
        raise HTTPException(status_code=400, detail="CPF e e-mail pertencem a cadastros diferentes.")

    usuario = usuario_cpf or usuario_email
    modalidade_permitida = modalidade_autorizada(cpf, db)
    colaborador = modalidade_permitida is not None
    if usuario:
        usuario.nome = nome
        usuario.email = str(solicitacao.email)
        usuario.cpf = cpf
        usuario.telefone = telefone
        usuario.cep = cep
        usuario.colaborador_dm = colaborador
    else:
        usuario = User(
            nome=nome,
            cpf=cpf,
            email=str(solicitacao.email),
            telefone=telefone,
            cep=cep,
            colaborador_dm=colaborador,
        )
        db.add(usuario)
        db.flush()

    status_solicitacao = "EM_ANALISE"
    if colaborador:
        status_solicitacao = "APROVADO" if tipo_cartao == modalidade_permitida else "REPROVADO"

    nova_solicitacao = Application(
        usuario_id=usuario.id,
        tipo_cartao=tipo_cartao,
        loja_id=loja.id if loja else None,
        status=status_solicitacao,
    )

    db.add(nova_solicitacao)
    db.commit()
    db.refresh(nova_solicitacao)
    return nova_solicitacao


@router.get("/{solicitacao_id}", response_model=ApplicationResponse)
def buscar_solicitacao(
    solicitacao_id: int,
    cpf: str = Query(min_length=11, max_length=14),
    db: Session = Depends(get_db),
):
    cpf_limpo = somente_numeros(cpf)
    if len(cpf_limpo) != 11:
        raise HTTPException(status_code=400, detail="Informe um CPF válido.")

    solicitacao = (
        db.query(Application)
        .join(User, Application.usuario_id == User.id)
        .filter(Application.id == solicitacao_id, User.cpf == cpf_limpo)
        .first()
    )
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada para esse CPF.")
    return solicitacao


@router.post("/consultar", response_model=ApplicationListResponse)
def consultar_solicitacoes_por_cpf(
    consulta: ConsultaCpf,
    request: Request,
    pagina: int = Query(default=1, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    verificar_limite_consulta(request)
    cpf = somente_numeros(consulta.cpf)
    if len(cpf) != 11:
        raise HTTPException(status_code=400, detail="Informe um CPF com 11 números.")

    pedidos = (
        db.query(Application)
        .join(User, Application.usuario_id == User.id)
        .filter(User.cpf == cpf)
    )
    total = pedidos.count()
    solicitacoes = (
        pedidos.order_by(Application.criado_em.desc(), Application.id.desc())
        .offset((pagina - 1) * 20)
        .limit(20)
        .all()
    )
    return {"total": total, "solicitacoes": solicitacoes}
