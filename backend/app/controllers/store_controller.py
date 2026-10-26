import hmac
import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.partner_store import PartnerStore
from app.schemas.partner_store import PartnerStoreResponse, PartnerStoreSearchResponse, StoreEmissionUpdate
from app.services.cep_service import limpar_cep, obter_uf_por_cep

router = APIRouter(prefix="/lojas", tags=["Lojas parceiras"])


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


@router.put("/parceiras/{loja_id}/emissao", response_model=PartnerStoreResponse)
def atualizar_emissao(
    loja_id: int,
    dados: StoreEmissionUpdate,
    x_admin_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    token = os.getenv("ADMIN_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(status_code=503, detail="Acesso administrativo não configurado.")
    if not hmac.compare_digest(x_admin_token, token):
        raise HTTPException(status_code=403, detail="Acesso não autorizado.")

    loja = db.query(PartnerStore).filter(PartnerStore.id == loja_id).first()
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")
    loja.emite_cartao_credito = dados.emite_cartao_credito
    db.commit()
    db.refresh(loja)
    return loja
