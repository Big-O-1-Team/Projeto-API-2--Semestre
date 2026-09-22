from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.partner_store import PartnerStore
from app.schemas.partner_store import PartnerStoreSearchResponse
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
