from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


programa_unidades = Table(
    "programa_unidades", Base.metadata,
    Column("loja_id", Integer, ForeignKey("estabelecimentos_parceiros.id"), primary_key=True),
    Column("programa_id", Integer, ForeignKey("programas_cartao.id"), primary_key=True, index=True),
)


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
