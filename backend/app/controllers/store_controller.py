import hmac
import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.partner_store import PartnerStore
from app.schemas.partner_store import PartnerStoreResponse, PartnerStoreSearchResponse, StoreEmissionUpdate, PartnerStoreCreate
from app.services.cep_service import limpar_cep, obter_uf_por_cep
from app.models.partner_contributor import PartnerContributor
from app.schemas.partner import PartnerContributorPublic

router = APIRouter(prefix="/lojas", tags=["Lojas parceiras"])

@router.get("/parceiras/{loja_id}/contribuidores", response_model=list[PartnerContributorPublic])
def listar_contribuidores_da_loja(
    loja_id: int,
    db: Session = Depends(get_db)):
    loja = db.query(PartnerStore).filter(PartnerStore.id == loja_id, PartnerStore.ativo.is_(True)).first()
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")
    return db.query(PartnerContributor).filter(PartnerContributor.loja_id == loja_id, PartnerContributor.ativo.is_(True)).order_by(PartnerContributor.nome).all()

@router.get("/parceiras", response_model=PartnerStoreSearchResponse)
def buscar_lojas_parceiras(cep: str, db: Session = Depends(get_db)):
    try:
        cep_limpo = limpar_cep(cep)
        uf = obter_uf_por_cep(cep_limpo)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    lojas = (
        db.query(PartnerStore)
        .filter(
            PartnerStore.ativo.is_(True),
            PartnerStore.estado == uf,
        )
        .order_by(PartnerStore.cidade, PartnerStore.nome)
        .all()
    )

    return {
        "cep": cep_limpo,
        "uf": uf,
        "total": len(lojas),
        "lojas": lojas,
    }


def validar_administrador(token_recebido: str):
    token = os.getenv("ADMIN_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(status_code=503, detail="Acesso administrativo não configurado.")
    if not hmac.compare_digest(token_recebido, token):
        raise HTTPException(status_code=403, detail="Acesso não autorizado.")


@router.post("/parceiras", response_model=PartnerStoreResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_loja_parceira(
    dados: PartnerStoreCreate,
    x_admin_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    validar_administrador(x_admin_token)
    existente = db.query(PartnerStore).filter(
        PartnerStore.nome == dados.nome,
        PartnerStore.cep == dados.cep,
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Esta loja já está cadastrada.")
    loja = PartnerStore(**dados.model_dump(), ativo=True)
    db.add(loja)
    db.commit()
    db.refresh(loja)
    return loja


@router.put("/parceiras/{loja_id}/emissao", response_model=PartnerStoreResponse)
def atualizar_emissao(
    loja_id: int,
    dados: StoreEmissionUpdate,
    x_admin_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    validar_administrador(x_admin_token)

    loja = db.query(PartnerStore).filter(PartnerStore.id == loja_id).first()
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")
    loja.emite_cartao_credito = dados.emite_cartao_credito
    db.commit()
    db.refresh(loja)
    return loja
