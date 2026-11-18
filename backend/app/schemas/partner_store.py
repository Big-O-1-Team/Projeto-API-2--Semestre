from pydantic import BaseModel, ConfigDict


class PartnerStoreResponse(BaseModel):
    id: int
    nome: str
    estado: str
    cidade: str
    endereco: str
    cep: str
    emite_cartao_credito: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class PartnerStoreSearchResponse(BaseModel):
    cep: str
    uf: str
    total: int
    lojas: list[PartnerStoreResponse]


class StoreEmissionUpdate(BaseModel):
    emite_cartao_credito: bool

from pydantic import Field, field_validator
import re


class PartnerStoreCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    estado: str = Field(min_length=2, max_length=2)
    cidade: str = Field(min_length=2, max_length=100)
    endereco: str = Field(min_length=5, max_length=180)
    cep: str = Field(min_length=8, max_length=9)
    emite_cartao_credito: bool = False

    @field_validator("nome", "cidade", "endereco")
    @classmethod
    def limpar_texto(cls, valor: str) -> str:
        return valor.strip()

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor: str) -> str:
        uf = valor.strip().upper()
        if uf not in {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}:
            raise ValueError("Estado inválido.")
        return uf

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, valor: str) -> str:
        cep = re.sub(r"\D", "", valor)
        if len(cep) != 8:
            raise ValueError("Informe um CEP com 8 números.")
        return cep
