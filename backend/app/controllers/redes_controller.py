from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db   # ajuste ao nome real da sua dependência
from app.cep import CepInvalido
from app.services.rede_service import RedeService
from app.schemas.rede import BuscaLojasOut

router = APIRouter(prefix="/lojas", tags=["lojas"])

@router.get("/busca", response_model=BuscaLojasOut)
def buscar_lojas_por_cep(
    cep: str = Query(..., min_length=8, max_length=9, description="CEP com ou sem hífen"),
    db: Session = Depends(get_db),
):
    try:
        uf, redes = RedeService(db).buscar_por_cep(cep)
    except CepInvalido:
        raise HTTPException(status_code=422, detail="CEP inválido")
    return BuscaLojasOut(uf=uf, redes=redes)