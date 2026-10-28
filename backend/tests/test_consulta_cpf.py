from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers.application_controller import router
from app.database import Base, get_db
from app.middleware import rate_limit
from app.models.application import Application
from app.models.card import Card
from app.models.partner_store import PartnerStore
from app.models.user import User


def test_listar_solicitacoes_do_cpf():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        usuario = User(nome="Pessoa Teste", cpf="12345678901", email="teste@example.com", telefone="12999999999", cep="12210000", colaborador_dm=False)
        db.add(usuario)
        db.flush()
        db.add(Application(usuario_id=usuario.id, tipo_cartao="DM", status="EM_ANALISE", criado_em=datetime(2026, 10, 28)))
        db.add(Application(usuario_id=usuario.id, tipo_cartao="LOJA_DIGITAL", status="APROVADO", criado_em=datetime(2026, 10, 29)))
        db.commit()

    app = FastAPI()
    app.include_router(router)

    def usar_banco():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = usar_banco
    rate_limit.consultas_por_ip.clear()
    with TestClient(app) as client:
        res = client.post("/solicitacoes/consultar", json={"cpf": "123.456.789-01"})
        assert res.status_code == 200
        assert res.json()["total"] == 2
        assert len(res.json()["solicitacoes"]) == 2
        assert set(res.json()["solicitacoes"][0]) == {"id", "tipo_cartao", "status", "criado_em"}
        vazio = client.post("/solicitacoes/consultar", json={"cpf": "00000000000"})
        assert vazio.status_code == 200
        assert vazio.json()["total"] == 0
    rate_limit.consultas_por_ip.clear()
    engine.dispose()
