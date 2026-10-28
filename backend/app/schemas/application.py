import re
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ApplicationCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    cpf: str = Field(min_length=11, max_length=11)
    email: EmailStr
    telefone: str = Field(min_length=10, max_length=11)
    cep: str = Field(min_length=8, max_length=8)
    tipo_cartao: Literal["DM", "LOJA_FISICA", "LOJA_DIGITAL"]
    loja_id: int | None = Field(default=None, gt=0)

    model_config = ConfigDict(extra="forbid")

    @field_validator("cpf", "telefone", "cep", mode="before")
    @classmethod
    def normalizar_numeros(cls, valor):
        return re.sub(r"\D", "", valor) if isinstance(valor, str) else valor

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, valor: str) -> str:
        return valor.strip()


class ApplicationResponse(BaseModel):
    id: int
    usuario_id: int
    tipo_cartao: str
    loja_id: int | None
    status: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsultaCpf(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)

    model_config = ConfigDict(extra="forbid")


class ApplicationSummary(BaseModel):
    id: int
    tipo_cartao: str
    status: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    total: int
    solicitacoes: list[ApplicationSummary]
