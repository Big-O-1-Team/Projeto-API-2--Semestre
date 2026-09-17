from fastapi import FastAPI
from app.database import Base, engine
from app.controllers.user_controller import router as user_router
from app.models.user import User
from app.models.card import Card


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="DM Card API",
    version="1.0.0"
)


app.include_router(user_router)


@app.get("/")
def home():
    return {
        "message": "DM Card API funcionando"
    }