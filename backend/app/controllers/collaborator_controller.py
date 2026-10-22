from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.services.collaborator_service import autenticar_colaborador, gerar_token, limpar_cpf, validar_token

router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])


class LoginColaborador(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    senha: str = Field(min_length=1)


class SessaoColaborador(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@router.post("/autenticar", response_model=SessaoColaborador)
def login(dados: LoginColaborador):
    cpf = limpar_cpf(dados.cpf)
    if len(cpf) != 11 or not autenticar_colaborador(cpf, dados.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    return {"access_token": gerar_token(cpf)}


@router.get("/eu")
def colaborador_logado(authorization: str = Header(default="")):
    tipo, _, token = authorization.partition(" ")
    if tipo.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Informe o token de acesso.")
    return {"cpf": validar_token(token), "colaborador_dm": True}
