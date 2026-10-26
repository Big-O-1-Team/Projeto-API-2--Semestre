import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def somente_numeros(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UserCreate, db: Session = Depends(get_db)):
    cpf = somente_numeros(usuario.cpf)
    telefone = somente_numeros(usuario.telefone)
    cep = somente_numeros(usuario.cep)

    if len(cpf) != 11:
        raise HTTPException(status_code=400, detail="CPF deve conter 11 números.")
    if len(telefone) < 10 or len(telefone) > 11:
        raise HTTPException(status_code=400, detail="Telefone inválido.")
    if len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP deve conter 8 números.")

    usuario_existente = db.query(User).filter(
        (User.cpf == cpf) | (User.email == str(usuario.email))
    ).first()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="CPF ou e-mail já cadastrado.")

    novo_usuario = User(
        nome=usuario.nome.strip(),
        cpf=cpf,
        email=str(usuario.email),
        telefone=telefone,
        cep=cep,
        colaborador_dm=False,
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.get("/{usuario_id}", response_model=UserResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario


@router.get("/", response_model=list[UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()
