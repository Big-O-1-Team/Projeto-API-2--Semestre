from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix='/usuarios',
    tags=['Usuários']
)

@router.post(
    '/',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)

def criar_usuario(
    usuario: UserCreate,
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(User).filter(
        (User.cpf == usuario.cpf) |
        (User.email == usuario.email)
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='CPF ou email já cadastrado.'
        )
    novo_usuario = User(
        nome=usuario.nome,
        cpf=usuario.cpf,
        email=usuario.email,
        telefone=usuario.telefone,
        cep=usuario.cep,
        colaborador_dm=usuario.colaborador_dm
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@router.get(
    '/{usuario_id}',
    response_model=UserResponse
)

def buscar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario = db.query(User).filter(
        User.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado.'
        )

    return usuario

@router.get(
    '/',
    response_model=list[UserResponse]
)

def listar_usuarios(
    db: Session = Depends(get_db)
):
    return db.query(User).all()