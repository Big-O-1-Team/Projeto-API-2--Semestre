from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.database import Base, engine
from app.controllers.application_controller import router as application_router
from app.controllers.card_controller import router as card_router
from app.controllers.collaborator_controller import router as collaborator_router
from app.controllers.store_controller import router as store_router
from app.controllers.user_controller import router as user_router
from app.controllers.partner_controller import router as partner_router
from app.middleware.rate_limit import limitar_requisicoes
from app.models.application import Application
from app.models.card import Card
from app.models.collaborator import Collaborator
from app.models.partner_store import PartnerStore
from app.models.partner_contributor import PartnerContributor
from app.models.partner_account import PartnerAccount
from app.models.user import User
from app.seed import seed_database

Base.metadata.create_all(bind=engine)

colunas_lojas = {
    coluna["name"]
    for coluna in inspect(engine).get_columns("estabelecimentos_parceiros")
}

if "emite_cartao_credito" not in colunas_lojas:
    with engine.begin() as conexao:
        conexao.execute(text(
            "ALTER TABLE estabelecimentos_parceiros "
            "ADD COLUMN emite_cartao_credito BOOLEAN NOT NULL DEFAULT 0"
        ))

colunas_solicitacoes = {
    coluna["name"]
    for coluna in inspect(engine).get_columns("solicitacoes")
}

if "contribuidor_id" not in colunas_solicitacoes:
    if engine.dialect.name == "mysql":
        with engine.begin() as conexao:
            conexao.execute(text(
                "ALTER TABLE solicitacoes ADD COLUMN contribuidor_id INTEGER NULL"
            ))
            conexao.execute(text(
                """
                ALTER TABLE solicitacoes
                ADD CONSTRAINT fk_solicitacoes_contribuidor
                FOREIGN KEY (contribuidor_id)
                REFERENCES contribuidores_parceiros(id)
                """
            ))
    elif engine.dialect.name == "sqlite":
        with engine.begin() as conexao:
            conexao.execute(text(
                """
                ALTER TABLE solicitacoes
                ADD COLUMN contribuidor_id INTEGER
                REFERENCES contribuidores_parceiros(id)
                """
            ))
    else:
        raise RuntimeError("Banco de dados não suportado para esta migração.")

indices = inspect(engine).get_indexes("solicitacoes")

indice_existente = any(
    "contribuidor_id" in indice.get("column_names", [])
    for indice in indices
)

if not indice_existente:
    with engine.begin() as conexao:
        conexao.execute(text(
            """
            CREATE INDEX ix_solicitacoes_contribuidor_id
            ON solicitacoes (contribuidor_id)
            """
        ))

seed_database()

app = FastAPI(title="DM Card API", version="2.0.0")
app.middleware("http")(limitar_requisicoes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(card_router)
app.include_router(store_router)
app.include_router(application_router)
app.include_router(collaborator_router)
app.include_router(partner_router)

@app.get("/")
def home():
    return {"message": "DM Card API funcionando"}

@app.get("/health")
def health():
    return {"status": "ok"}
