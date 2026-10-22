from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from app.services.collaborator_service import autenticar_colaborador, gerar_token, limpar_cpf, validar_token

router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])
security = HTTPBearer()


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
def colaborador_logado(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    return {
        "cpf": validar_token(token),
        "colaborador_dm": True
    }
