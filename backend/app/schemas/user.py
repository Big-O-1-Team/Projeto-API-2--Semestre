from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    cep: str
    colaborador_dm: bool = False

class UserResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    email: EmailStr
    telefone: str
    cep: str
    colaborador_dm: bool

    class Config:
        from_attributes = True