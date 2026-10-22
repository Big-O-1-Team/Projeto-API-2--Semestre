from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.database import Base, engine
from app.controllers.application_controller import router as application_router
from app.controllers.card_controller import router as card_router
from app.controllers.collaborator_controller import router as collaborator_router
from app.controllers.store_controller import router as store_router
from app.controllers.user_controller import router as user_router
from app.middleware.rate_limit import limitar_requisicoes
from app.models.application import Application
from app.models.card import Card
from app.models.partner_store import PartnerStore
from app.models.user import User
from app.seed import seed_database

Base.metadata.create_all(bind=engine)

if "emite_cartao_credito" not in {coluna["name"] for coluna in inspect(engine).get_columns("estabelecimentos_parceiros")}:
    with engine.begin() as conexao:
        conexao.execute(text("ALTER TABLE estabelecimentos_parceiros ADD COLUMN emite_cartao_credito BOOLEAN NOT NULL DEFAULT 0"))

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


@app.get("/")
def home():
    return {"message": "DM Card API funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}
