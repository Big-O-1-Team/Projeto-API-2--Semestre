import hmac
import os
from fastapi import (APIRouter, Depends, Header, HTTPException, Response, status)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.partner_account import PartnerAccount
from app.models.partner_contributor import PartnerContributor
from app.models.partner_store import PartnerStore
from app.schemas.partner import (PartnerAccountCreate, PartnerAccountResponse, PartnerLogin, PartnerTokenResponse, PartnerContributorCreate, PartnerContributorResponse)
from app.services.partner_auth_service import (gerar_hash_senha, verificar_senha, gerar_token_parceiro, validar_token_parceiro)


router = APIRouter(prefix="/parceiros", tags=["Parceiros"])
security = HTTPBearer(auto_error=False)


def obter_parceiro(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    return validar_token_parceiro(credentials.credentials, db)


def verificar_administrador(token_recebido):
    token = os.getenv("ADMIN_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(status_code=503, detail="Acesso administrativo não configurado.")
    if not hmac.compare_digest(token_recebido, token):
        raise HTTPException(status_code=403, detail="Acesso não autorizado.")

@router.post("/contas", response_model=PartnerAccountResponse, status_code=status.HTTP_201_CREATED)

def criar_conta_parceiro(dados: PartnerAccountCreate, x_admin_token: str = Header(default=""), db: Session = Depends(get_db)):
    verificar_administrador(x_admin_token)
    loja = db.query(PartnerStore).filter(PartnerStore.id == dados.loja_id, PartnerStore.ativo.is_(True)).first()

    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")

    existente = db.query(PartnerAccount).filter(
        (PartnerAccount.loja_id == dados.loja_id) |
        (PartnerAccount.email == str(dados.email))).first()

    if existente:
        raise HTTPException(status_code=409, detail="Essa loja ou esse e-mail já possui uma conta.")

    conta = PartnerAccount(loja_id=dados.loja_id, email=str(dados.email).lower(), senha_hash=gerar_hash_senha(dados.senha))

    db.add(conta)
    db.commit()
    db.refresh(conta)

    return conta


@router.post("/autenticar", response_model=PartnerTokenResponse)
def autenticar_parceiro(
    dados: PartnerLogin,
    db: Session = Depends(get_db)
):
    conta = db.query(PartnerAccount).filter(
        PartnerAccount.email == str(dados.email).lower(),
        PartnerAccount.ativo.is_(True)
    ).first()

    if not conta or not verificar_senha(dados.senha, conta.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos."
        )

    return {
        "access_token": gerar_token_parceiro(conta)
    }


@router.get("/eu", response_model=PartnerAccountResponse)
def parceiro_logado(
    conta: PartnerAccount = Depends(obter_parceiro)
):
    return conta


@router.get(
    "/eu/contribuidores",
    response_model=list[PartnerContributorResponse]
)
def listar_contribuidores(
    conta: PartnerAccount = Depends(obter_parceiro),
    db: Session = Depends(get_db)
):
    return db.query(PartnerContributor).filter(
        PartnerContributor.loja_id == conta.loja_id
    ).order_by(PartnerContributor.nome).all()


@router.post(
    "/eu/contribuidores",
    response_model=PartnerContributorResponse,
    status_code=status.HTTP_201_CREATED
)
def cadastrar_contribuidor(
    dados: PartnerContributorCreate,
    conta: PartnerAccount = Depends(obter_parceiro),
    db: Session = Depends(get_db)
):
    existente = db.query(PartnerContributor).filter(
        PartnerContributor.loja_id == conta.loja_id,
        PartnerContributor.nome == dados.nome
    ).first()

    if existente:
        if existente.ativo:
            raise HTTPException(
                status_code=409,
                detail="Esse contribuidor já está cadastrado."
            )

        existente.ativo = True
        db.commit()
        db.refresh(existente)
        return existente

    novo = PartnerContributor(
        loja_id=conta.loja_id,
        nome=dados.nome,
        ativo=True
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


@router.delete(
    "/eu/contribuidores/{contribuidor_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def desativar_contribuidor(
    contribuidor_id: int,
    conta: PartnerAccount = Depends(obter_parceiro),
    db: Session = Depends(get_db)
):
    contribuidor = db.query(PartnerContributor).filter(
        PartnerContributor.id == contribuidor_id,
        PartnerContributor.loja_id == conta.loja_id
    ).first()

    if not contribuidor:
        raise HTTPException(
            status_code=404,
            detail="Contribuidor não encontrado."
        )

    contribuidor.ativo = False
    db.commit()
    return Response(status_code=204)
