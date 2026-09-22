from pydantic import BaseModel


class PartnerStoreResponse(BaseModel):
    id: int
    nome: str
    estado: str
    cidade: str
    endereco: str
    cep: str

    class Config:
        from_attributes = True


class PartnerStoreSearchResponse(BaseModel):
    cep: str
    uf: str
    total: int
    lojas: list[PartnerStoreResponse]
