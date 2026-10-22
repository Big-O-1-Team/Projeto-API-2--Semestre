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
