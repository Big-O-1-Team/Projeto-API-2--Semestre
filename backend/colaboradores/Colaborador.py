from sqlalchemy import String, Float, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class Colaborador(Base):
    __tablename__ = "colaboradores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Colaborador(id='{self.id}', nome='{self.nome}', email='{self.email}',cpf='{self.cpf}', is_active='{self.is_active}')>"

engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)

with Session(engine) as session:
    colab1 = Colaborador(
        id="12345678900",
        nome="Exemplo 1",
        email="exemplo1@gmail.com",
        cpf="12345678900",
        is_active=True,
    )
    colab2 = Colaborador(
        id="98765432100",
        nome="Exemplo 2",
        email="exemplo2@gmail.com",
        cpf="98765432100",
        is_active=False,
    )

    session.add_all([colab1, colab2])
    session.commit()

    cpf_busca = "12345678900"
    colaborador = session.get(Colaborador, cpf_busca)

    if colaborador:
        print(f"Encontrado via session.get(): {colaborador.nome} - {colaborador.cargo}")

    stmt = select(Colaborador).where(Colaborador.cpf == "98765432100")
    resultado = session.scalars(stmt).first()

    if resultado:
        print(f"Encontrado via select(): {resultado.nome} - {resultado.departamento}")
