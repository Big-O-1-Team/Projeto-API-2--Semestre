from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.database import Base

class PartnerAccount(Base):
    __tablename__ = "contas_parceiros"

    id = Column(Integer, primary_key=True, index=True)

    loja_id = Column(
        Integer,
        ForeignKey("estabelecimentos_parceiros.id"),
        nullable=False,
        unique=True
    )

    email = Column(String(150), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
