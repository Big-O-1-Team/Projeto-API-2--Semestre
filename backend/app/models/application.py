from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.database import Base
from app.models.card_program import CardProgram


class Application(Base):
    __tablename__ = "solicitacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo_cartao = Column(String(30), nullable=False)
    loja_id = Column(Integer, ForeignKey("estabelecimentos_parceiros.id"), nullable=True)
    contribuidor_id = Column(Integer, ForeignKey("contribuidores_parceiros.id"), nullable=True, index=True)
    programa_id = Column(Integer, ForeignKey("programas_cartao.id"), nullable=True, index=True)
    chave_ativa = Column(String(120), nullable=True, unique=True)
    codigo_consulta_hash = Column(String(64), nullable=True, unique=True)
    status = Column(String(30), nullable=False, default="EM_ANALISE")
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
