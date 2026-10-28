import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers import application_controller
from app.database import Base, get_db
from app.models.application import Application
from app.models.card import Card
from app.models.collaborator import Collaborator
from app.models.partner_store import PartnerStore
from app.models.user import User
from app import seed


@pytest.fixture
def ambiente(monkeypatch):
    monkeypatch.setenv("COLABORADORES_DM", "{}")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)
    monkeypatch.setattr(seed, "SessionLocal", sessao)
    monkeypatch.setattr(application_controller, "obter_uf_por_cep", lambda cep: "SP")
    seed.seed_database()
    app = FastAPI()
    app.include_router(application_controller.router)

    def banco_teste():
        with sessao() as db:
            yield db

    app.dependency_overrides[get_db] = banco_teste
    with TestClient(app) as cliente:
        yield cliente, sessao
    engine.dispose()


def solicitar(cliente, cpf, tipo="DM", loja_id=None):
    return cliente.post("/solicitacoes/", json={
        "nome": "Pessoa Fictícia",
        "cpf": cpf,
        "email": f"cliente{cpf}@example.com",
        "telefone": "12999998888",
        "cep": "12210000",
        "tipo_cartao": tipo,
        "loja_id": loja_id,
    })


def test_quatro_colaboradores_aprovados_no_dm(ambiente):
    cliente, sessao = ambiente
    cpfs = ["32376226643", "33143237945", "21953320694", "63380575747"]
    with sessao() as db:
        cadastrados = db.query(Collaborator).all()
        assert len(cadastrados) == 4
        assert {c.cpf for c in cadastrados} == set(cpfs)
        assert all(c.ativo and c.modalidade_autorizada == "DM" for c in cadastrados)
    for cpf in cpfs:
        resposta = solicitar(cliente, cpf)
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["status"] == "APROVADO"


def test_colaborador_recusado_em_loja(ambiente):
    cliente, sessao = ambiente
    digital = solicitar(cliente, "32376226643", "LOJA_DIGITAL")
    assert digital.status_code == 201, digital.text
    assert digital.json()["status"] == "REPROVADO"

    with sessao() as db:
        loja = db.query(PartnerStore).filter(PartnerStore.estado == "SP").first()
        assert loja is not None
        loja_id = loja.id
    fisico = solicitar(cliente, "33143237945", "LOJA_FISICA", loja_id)
    assert fisico.status_code == 201, fisico.text
    assert fisico.json()["status"] == "REPROVADO"


def test_cliente_comum_e_seed_idempotente(ambiente):
    cliente, sessao = ambiente
    normal = solicitar(cliente, "98765432100")
    assert normal.status_code == 201, normal.text
    assert normal.json()["status"] == "EM_ANALISE"
    seed.seed_database()
    seed.seed_database()
    with sessao() as db:
        assert db.query(Collaborator).count() == 4
        assert db.query(User).filter(User.cpf == "32376226643").count() == 0


def test_colaborador_inativo_nao_recebe_aprovacao(ambiente):
    cliente, sessao = ambiente
    with sessao() as db:
        cadastro = db.get(Collaborator, "63380575747")
        cadastro.ativo = False
        db.commit()
    resposta = solicitar(cliente, "63380575747")
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["status"] == "EM_ANALISE"


def test_solicitacao_repetida_nao_duplicar_usuario(ambiente):
    cliente, sessao = ambiente
    for _ in range(2):
        resposta = solicitar(cliente, "21953320694")
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["status"] == "APROVADO"
    with sessao() as db:
        assert db.query(User).filter(User.cpf == "21953320694").count() == 1
        assert db.query(Application).count() == 2
