from datetime import datetime
from pydantic import BaseModel, EmailStr


class ApplicationCreate(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    cep: str
    tipo_cartao: str
    loja_id: int | None = None


class ApplicationResponse(BaseModel):
    id: int
    usuario_id: int
    tipo_cartao: str
    loja_id: int | None
    status: str
    criado_em: datetime

    class Config:
        from_attributes = True
