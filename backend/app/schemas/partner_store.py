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
    programa_id: int | None = None
    rede_nome: str | None = None
    programa_nome: str | None = None
    modalidade: str = "LOJA_FISICA"
    latitude: float | None = None
    longitude: float | None = None
    distancia_km: float | None = None

    model_config = ConfigDict(from_attributes=True)


class PartnerStoreSearchResponse(BaseModel):
    cep: str
    uf: str
    total: int
    pagina: int = 1
    limite: int = 50
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
    programa_id: int | None = Field(default=None, gt=0)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("nome", "cidade", "endereco")
    @classmethod
    def limpar_texto(cls, valor: str) -> str:
        texto = valor.strip()
        if len(texto) < 2:
            raise ValueError("Informe um valor válido.")
        return texto

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

from typing import Literal


class NetworkCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)


class ProgramCreate(BaseModel):
    rede_id: int = Field(gt=0)
    nome: str = Field(min_length=2, max_length=120)
    modalidade: Literal["LOJA_FISICA", "LOJA_DIGITAL"]


class StoreProgramUpdate(BaseModel):
    programa_id: int | None = Field(default=None, gt=0)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class StoreSearch(BaseModel):
    cep: str = Field(default="", max_length=9)
    modalidade: Literal["LOJA_FISICA", "LOJA_DIGITAL"] = "LOJA_FISICA"
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    busca: str = Field(default="", max_length=120)
    pagina: int = Field(default=1, ge=1)
    limite: int = Field(default=50, ge=1, le=100)
