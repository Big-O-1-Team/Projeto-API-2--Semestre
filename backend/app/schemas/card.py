from pydantic import BaseModel


class CardResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    descricao: str | None
    fisico: bool
    restricao_geografica: bool
    ativo: bool

    class Config:
        from_attributes = True
