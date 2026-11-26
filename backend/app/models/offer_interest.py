from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.database import Base


class OfferInterest(Base):
    __tablename__ = "interesses_ofertas"

    id = Column(Integer, primary_key=True, index=True)
    solicitacao_id = Column(Integer, ForeignKey("solicitacoes.id"), nullable=False, unique=True)
    email = Column(String(150), nullable=False)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    enviado_em = Column(DateTime, nullable=True)
    confirmado_em = Column(DateTime, nullable=True)
