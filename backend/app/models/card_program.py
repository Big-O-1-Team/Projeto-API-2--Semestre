from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class PartnerNetwork(Base):
    __tablename__ = "redes_parceiras"
    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False, unique=True)
    ativo = Column(Boolean, nullable=False, default=True)


class CardProgram(Base):
    __tablename__ = "programas_cartao"
    __table_args__ = (UniqueConstraint("rede_id", "nome", "modalidade"),)
    id = Column(Integer, primary_key=True)
    rede_id = Column(Integer, ForeignKey("redes_parceiras.id"), nullable=False)
    nome = Column(String(120), nullable=False)
    modalidade = Column(String(30), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    rede = relationship(PartnerNetwork)
