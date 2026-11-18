from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class PartnerAccountCreate(BaseModel):
    loja_id: int = Field(gt=0)
    email: EmailStr
    senha: str = Field(min_length=8)

class PartnerLogin(BaseModel):
    email: EmailStr
    senha: str

class PartnerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class PartnerAccountResponse(BaseModel):
    id: int
    loja_id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class PartnerContributorCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, valor):
        return valor.strip()

class PartnerContributorResponse(BaseModel):
    id: int
    loja_id: int
    nome: str
    ativo: bool
    model_config = ConfigDict(from_attributes=True)

class PartnerContributorPublic(BaseModel):
    id: int
    nome: str
    model_config = ConfigDict(from_attributes=True)
