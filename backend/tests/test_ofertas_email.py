import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers import application_controller, offer_controller
from app.database import Base, get_db
from app.models.application import Application
from app.models.offer_interest import OfferInterest
from app.models.partner_store import PartnerStore
from app.models.user import User
from app.services.email_service import validar_token_confirmacao


@pytest.fixture
def ambiente(monkeypatch):
    monkeypatch.setenv("COLABORADORES_DM", '{"12345678901":"senha-de-teste"}')
    monkeypatch.setenv("AUTH_SECRET", "segredo-para-testar-confirmacao-de-ofertas-123456789")
    monkeypatch.setattr(offer_controller, "verificar_limite_consulta", lambda request: None)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)
    app = FastAPI()
    app.include_router(application_controller.router)
    app.include_router(offer_controller.router)

    def banco_teste():
        with sessao() as banco:
            yield banco

    app.dependency_overrides[get_db] = banco_teste
    with TestClient(app) as cliente:
        yield cliente, sessao
    engine.dispose()


def solicitar(cliente, cpf="12345678901", tipo="LOJA_DIGITAL"):
    resposta = cliente.post("/solicitacoes/", json={
        "nome": "Pessoa de Teste",
        "cpf": cpf,
        "email": "pessoa@example.com",
        "telefone": "12999998888",
        "cep": "12210000",
        "tipo_cartao": tipo,
    })
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def interesse(cliente, solicitacao_id, email="pessoa@example.com", cpf="12345678901", aceitar=True):
    return cliente.post("/ofertas/interesse", json={
        "solicitacao_id": solicitacao_id,
        "cpf": cpf,
        "email": email,
        "aceitar": aceitar,
    })


def test_reprovado_pode_pedir_confirmacao_e_nao_recebe_email_duplicado(ambiente, monkeypatch):
    cliente, sessao = ambiente
    pedido = solicitar(cliente)
    assert pedido["status"] == "REPROVADO"
    enviados = []

    def enviar(email, token):
        enviados.append((email, token))
        return True

    monkeypatch.setattr(offer_controller, "enviar_confirmacao", enviar)
    resposta = interesse(cliente, pedido["id"])
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["situacao"] == "AGUARDANDO_CONFIRMACAO"
    assert len(enviados) == 1
    assert interesse(cliente, pedido["id"]).json()["situacao"] == "AGUARDANDO_CONFIRMACAO"
    assert len(enviados) == 1
    assert interesse(cliente, pedido["id"], aceitar=False).status_code == 400
    assert interesse(cliente, pedido["id"], cpf="98765432100").status_code == 404
    assert interesse(cliente, pedido["id"], email="outro@example.com").status_code == 404

    confirmacao = cliente.get("/ofertas/confirmar", params={"token": enviados[0][1]})
    assert confirmacao.status_code == 200
    assert "Interesse confirmado" in confirmacao.text
    assert interesse(cliente, pedido["id"]).json()["situacao"] == "CONFIRMADO"
    assert len(enviados) == 1

    with sessao() as db:
        registros = db.query(OfferInterest).all()
        assert len(registros) == 1
        assert registros[0].confirmado_em is not None


def test_nao_registrar_interesse_de_cliente_que_nao_foi_reprovado(ambiente):
    cliente, _ = ambiente
    pedido = solicitar(cliente, cpf="98765432100", tipo="DM")
    assert pedido["status"] == "EM_ANALISE"
    assert interesse(cliente, pedido["id"], cpf="98765432100").status_code == 404
    assert cliente.get("/ofertas/confirmar", params={"token": "token-que-nao-e-valido-12345"}).status_code == 400


def test_sem_smtp_nao_simula_email_enviado(ambiente, monkeypatch):
    cliente, sessao = ambiente
    pedido = solicitar(cliente)
    monkeypatch.setattr(offer_controller, "enviar_confirmacao", lambda email, token: False)
    resposta = interesse(cliente, pedido["id"])
    assert resposta.status_code == 200
    assert resposta.json()["situacao"] == "PENDENTE_ENVIO"
    with sessao() as db:
        registro = db.query(OfferInterest).one()
        assert registro.enviado_em is None
        assert registro.confirmado_em is None
