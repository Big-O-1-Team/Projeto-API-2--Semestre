from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    cep = Column(String(8), nullable=False)
    colaborador_dm = Column(Boolean, default=False, nullable=False)