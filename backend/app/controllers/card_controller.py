from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.card import Card
from app.schemas.card import CardResponse

router = APIRouter(prefix="/cartoes", tags=["Cartões"])


@router.get("/", response_model=list[CardResponse])
def listar_cartoes(db: Session = Depends(get_db)):
    return db.query(Card).filter(Card.ativo.is_(True)).order_by(Card.id).all()
