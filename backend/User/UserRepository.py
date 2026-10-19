from sqlalchemy.orm import Session
from .User import User
from .UserEntity import UserEntity

class UserRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def buscar_por_email(self, email: str):
        return self.session.query(UserEntity).filter(UserEntity.email == email).first()

    def buscar_por_cpf(self, cpf: str):
        return self.session.query(UserEntity).filter(UserEntity.cpf == cpf).first()

    def salvar(self, usuario: User) -> User:
        nova_entidade = UserEntity(
            id=usuario.id,
            name=usuario.name,
            email=usuario.email,
            cpf=usuario.cpf,
            is_active=usuario.is_active
        )
        
        self.session.add(nova_entidade)
        self.session.commit()
        
        return usuario
