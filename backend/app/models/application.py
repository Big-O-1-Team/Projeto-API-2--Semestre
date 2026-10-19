from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.database import Base


class Application(Base):
    __tablename__ = "solicitacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo_cartao = Column(String(30), nullable=False)
    loja_id = Column(Integer, ForeignKey("estabelecimentos_parceiros.id"), nullable=True)
    status = Column(String(30), nullable=False, default="EM_ANALISE")
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
