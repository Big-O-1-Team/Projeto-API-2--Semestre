from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserEntity(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    cpf = Column(int(11), unique=True, nullabre=False)
    is_active = Column(Boolean, default=True)