from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.database import Base

class PartnerContributor(Base):
    __tablename__ = "contribuidores_parceiros"

    id = Column(Integer, primary_key=True, index=True)

    loja_id = Column(
        Integer,
        ForeignKey("estabelecimentos_parceiros.id"),
        nullable=False,
        index=True
    )

    nome = Column(String(100), nullable=False)

    ativo = Column(Boolean, nullable=False, default=True)
