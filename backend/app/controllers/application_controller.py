import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import Application
from app.models.partner_store import PartnerStore
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.cep_service import limpar_cep, obter_uf_por_cep

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
    tipo_cartao = solicitacao.tipo_cartao.strip().upper()

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

    usuario_cpf = db.query(User).filter(User.cpf == cpf).first()
    usuario_email = db.query(User).filter(User.email == str(solicitacao.email)).first()

    if usuario_cpf and usuario_email and usuario_cpf.id != usuario_email.id:
        raise HTTPException(status_code=400, detail="CPF e e-mail pertencem a cadastros diferentes.")

    usuario = usuario_cpf or usuario_email
    if usuario:
        usuario.nome = nome
        usuario.email = str(solicitacao.email)
        usuario.cpf = cpf
        usuario.telefone = telefone
        usuario.cep = cep
    else:
        usuario = User(
            nome=nome,
            cpf=cpf,
            email=str(solicitacao.email),
            telefone=telefone,
            cep=cep,
            colaborador_dm=False,
        )
        db.add(usuario)
        db.flush()

    nova_solicitacao = Application(
        usuario_id=usuario.id,
        tipo_cartao=tipo_cartao,
        loja_id=loja.id if loja else None,
        status="EM_ANALISE",
    )

    db.add(nova_solicitacao)
    db.commit()
    db.refresh(nova_solicitacao)
    return nova_solicitacao


@router.get("/{solicitacao_id}", response_model=ApplicationResponse)
def buscar_solicitacao(solicitacao_id: int, db: Session = Depends(get_db)):
    solicitacao = db.query(Application).filter(Application.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return solicitacao
