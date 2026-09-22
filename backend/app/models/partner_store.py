from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base


class PartnerStore(Base):
    __tablename__ = "estabelecimentos_parceiros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    estado = Column(String(2), nullable=False, index=True)
    cidade = Column(String(100), nullable=False)
    endereco = Column(String(180), nullable=False)
    cep = Column(String(8), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
