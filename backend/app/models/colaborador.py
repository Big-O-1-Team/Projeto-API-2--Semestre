from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base

class Colaborador(Base):
    __tablename__ = "colaboradores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    ativo = Column(Boolean, default=True, nullable=False)
