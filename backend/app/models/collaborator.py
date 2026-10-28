from sqlalchemy import Boolean, Column, String
from app.database import Base


class Collaborator(Base):
    __tablename__ = "colaboradores_dm"

    cpf = Column(String(11), primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    telefone = Column(String(20), nullable=False)
    cep = Column(String(8), nullable=False)
    modalidade_autorizada = Column(String(30), nullable=False, default="DM")
    ativo = Column(Boolean, nullable=False, default=True)
