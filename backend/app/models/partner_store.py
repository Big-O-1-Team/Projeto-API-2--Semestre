from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.card_program import CardProgram


class PartnerStore(Base):
    __tablename__ = "estabelecimentos_parceiros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    estado = Column(String(2), nullable=False, index=True)
    cidade = Column(String(100), nullable=False)
    endereco = Column(String(180), nullable=False)
    cep = Column(String(8), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    emite_cartao_credito = Column(Boolean, nullable=False, default=False, server_default="0")

    programa_id = Column(Integer, ForeignKey("programas_cartao.id"), nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    programa = relationship(CardProgram)

    @property
    def rede_nome(self):
        return self.programa.rede.nome if self.programa else None

    @property
    def programa_nome(self):
        return self.programa.nome if self.programa else None

    @property
    def modalidade(self):
        return self.programa.modalidade if self.programa else "LOJA_FISICA"

    @property
    def role(self) -> str:
        return "LOJA_EMISSORA" if self.emite_cartao_credito else "LOJA_PARCEIRA"
