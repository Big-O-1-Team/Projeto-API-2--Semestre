from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base

class Card(Base):
    __tablename__ = 'cartoes'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(30), nullable=False)
    descricao = Column(String(255), nullable=True)
    fisico = Column(Boolean, nullable=False, default=False)
    restricao_geografica = Column(Boolean, nullable=False, default=False)
    ativo = Column(Boolean, nullable=False, default=True)