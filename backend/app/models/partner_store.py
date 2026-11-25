from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.card_program import CardProgram, programa_unidades


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

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    programas = relationship(CardProgram, secondary=programa_unidades, order_by=CardProgram.id)

    @property
    def programa(self):
        return self.programas[0] if len(self.programas) == 1 else None

    @property
    def programa_id(self):
        return self.programa.id if self.programa else None

    @property
    def programas_ids(self):
        return [programa.id for programa in self.programas]

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
