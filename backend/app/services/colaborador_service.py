from sqlalchemy.orm import Session
from app.models.colaborador import Colaborador

def verificar_colaborador(cpf: str, db: Session) -> bool:
    colaborador = db.query(Colaborador).filter(
        Colaborador.cpf == cpf,
        Colaborador.ativo.is_(True)
    ).first()
    return colaborador is not None
