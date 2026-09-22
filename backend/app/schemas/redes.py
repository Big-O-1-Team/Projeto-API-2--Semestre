from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RedesParceirasResponse(BaseModel):
    id_rede: int
    nome: str
    tipo: str
    endereco: str
    cidade: str
    estado: str = Field(..., min_length=2, max_length=2, description="UF com 2 letras")
    cep: str = Field(..., min_length=8, max_length=8)
    telefone: str
    email: EmailStr
    responsavel: str
    descricao: str
    status: str
    
class BuscaLojasOut(BaseModel):
    uf: str
    redes: list[RedeParceiraOut]