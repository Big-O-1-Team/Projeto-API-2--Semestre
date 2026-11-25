import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers import application_controller, partner_controller, store_controller
from app.database import Base, get_db
from app.models.application import Application
from app.models.partner_account import PartnerAccount
from app.models.partner_contributor import PartnerContributor
from app.models.partner_store import PartnerStore
from app.models.user import User


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "senha-de-administrador-apenas-para-testes-123456789")
    monkeypatch.setenv("AUTH_SECRET", "segredo-de-autenticacao-apenas-para-testes-12345")
    monkeypatch.setenv("COLABORADORES_DM", "{}")
    monkeypatch.setattr(application_controller, "obter_uf_por_cep", lambda cep: "SP")
    monkeypatch.setattr(store_controller, "obter_uf_por_cep", lambda cep: "SP")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)
    app = FastAPI()
    app.include_router(store_controller.router)
    app.include_router(partner_controller.router)
    app.include_router(application_controller.router)

    def obter_banco():
        with sessao() as db:
            yield db

    app.dependency_overrides[get_db] = obter_banco
    with TestClient(app) as client:
        yield client
    engine.dispose()


def cadastrar_loja(cliente, nome, token="senha-de-administrador-apenas-para-testes-123456789"):
    return cliente.post(
        "/lojas/parceiras",
        headers={"x-admin-token": token},
        json={
            "nome": nome,
            "estado": "sp",
            "cidade": "São José dos Campos",
            "endereco": "Rua Central, 250",
            "cep": "12210-000",
        },
    )


def test_cadastro_loja_exige_token_e_impede_duplicados(cliente):
    assert cadastrar_loja(cliente, "Loja Nova", "incorreto").status_code == 403
    resposta = cadastrar_loja(cliente, "Loja Nova")
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["estado"] == "SP"
    assert resposta.json()["cep"] == "12210000"
    assert resposta.json()["role"] == "LOJA_PARCEIRA"
    assert cadastrar_loja(cliente, "Loja Nova").status_code == 409
    busca = cliente.get("/lojas/parceiras", params={"cep": "12210000"})
    assert busca.status_code == 200
    assert any(loja["nome"] == "Loja Nova" for loja in busca.json()["lojas"])


def test_contribuidores_ficam_isolados_por_loja_e_sao_opcionais(cliente):
    primeira = cadastrar_loja(cliente, "Loja Alpha").json()["id"]
    segunda = cadastrar_loja(cliente, "Loja Beta").json()["id"]
    token_admin = {"x-admin-token": "senha-de-administrador-apenas-para-testes-123456789"}

    for loja_id, email in [(primeira, "alpha@example.com"), (segunda, "beta@example.com")]:
        conta = cliente.post(
            "/parceiros/contas",
            headers=token_admin,
            json={"loja_id": loja_id, "email": email, "senha": "senha-forte-123"},
        )
        assert conta.status_code == 201, conta.text

    login = cliente.post(
        "/parceiros/autenticar",
        json={"email": "alpha@example.com", "senha": "senha-forte-123"},
    )
    assert login.status_code == 200, login.text
    bearer = {"Authorization": "Bearer " + login.json()["access_token"]}
    resposta = cliente.post(
        "/parceiros/eu/contribuidores",
        headers=bearer,
        json={"nome": "Atendente Teste"},
    )
    assert resposta.status_code == 201, resposta.text
    id_contribuidor = resposta.json()["id"]
    disponiveis = cliente.get(f"/lojas/parceiras/{primeira}/contribuidores")
    assert len(disponiveis.json()) == 1
    outra_loja = cliente.get(f"/lojas/parceiras/{segunda}/contribuidores")
    assert outra_loja.json() == []

    payload = {
        "nome": "Pessoa Teste",
        "cpf": "98765432100",
        "email": "cliente@example.com",
        "telefone": "12999998888",
        "cep": "12210000",
        "tipo_cartao": "LOJA_FISICA",
        "loja_id": primeira,
    }
    sem_atendente = cliente.post("/solicitacoes/", json=payload)
    assert sem_atendente.status_code == 201, sem_atendente.text
    assert sem_atendente.json()["contribuidor_id"] is None

    com_atendente = cliente.post(
        "/solicitacoes/",
        json={**payload, "cpf": "52998224725", "email": "outro@example.com", "contribuidor_id": id_contribuidor},
    )
    assert com_atendente.status_code == 201, com_atendente.text
    assert com_atendente.json()["contribuidor_id"] == id_contribuidor

    loja_errada = cliente.post(
        "/solicitacoes/",
        json={**payload, "loja_id": segunda, "contribuidor_id": id_contribuidor},
    )
    assert loja_errada.status_code == 400


def test_rede_distancia_paginacao_e_bloqueio(cliente):
    admin = {"x-admin-token": "senha-de-administrador-apenas-para-testes-123456789"}
    rede = cliente.post("/lojas/redes", headers=admin, json={"nome": "Rede Teste"}).json()
    programa = cliente.post("/lojas/programas", headers=admin, json={"rede_id": rede["id"], "nome": "Cartão Rede", "modalidade": "LOJA_FISICA"}).json()
    ids = []
    for nome, latitude in [("Unidade distante", -23.4), ("Unidade próxima", -23.18)]:
        resposta = cliente.post("/lojas/parceiras", headers=admin, json={"nome": nome, "estado": "SP", "cidade": "São José dos Campos", "endereco": "Rua Exemplo, 1", "cep": "12210000", "programa_id": programa["id"], "latitude": latitude, "longitude": -45.88})
        assert resposta.status_code == 201, resposta.text
        ids.append(resposta.json()["id"])
    busca = cliente.get("/lojas/parceiras", params={"cep": "12210000", "latitude": -23.18, "longitude": -45.88, "limite": 1})
    assert busca.status_code == 200, busca.text
    assert busca.json()["total"] == 2
    assert busca.json()["lojas"][0]["id"] == ids[1]
    assert busca.json()["lojas"][0]["distancia_km"] == 0
    payload = {"nome": "Pessoa Teste", "cpf": "98765432100", "email": "teste@example.com", "telefone": "12999998888", "cep": "12210000", "tipo_cartao": "LOJA_FISICA", "loja_id": ids[0]}
    primeira = cliente.post("/solicitacoes/", json=payload)
    assert primeira.status_code == 201, primeira.text
    assert primeira.json()["programa_id"] == programa["id"]
    assert cliente.post("/solicitacoes/", json={**payload, "loja_id": ids[1]}).status_code == 409
    assert cliente.post("/solicitacoes/", json={**payload, "cpf": "52998224725"}).status_code == 409
    assert cliente.get("/lojas/parceiras", params={"cep": "12210000", "latitude": 1}).status_code == 400


def test_pre_qualificacao_ficticia(cliente, monkeypatch):
    monkeypatch.setenv("DEMO_PRE_QUALIFICACAO", "1")
    monkeypatch.setenv("PRE_QUALIFICADOS_FICTICIOS", '{"98765432100":["DM"]}')
    payload = {"nome": "Pessoa Teste", "cpf": "98765432100", "email": "teste@example.com", "telefone": "12999998888", "cep": "12210000", "tipo_cartao": "DM"}
    resposta = cliente.post("/solicitacoes/", json=payload)
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["status"] == "APROVADO"
    assert cliente.post("/solicitacoes/", json={**payload, "cpf": "11111111111"}).status_code == 400


def test_programa_digital_sem_restricao_de_uf(cliente):
    admin = {"x-admin-token": "senha-de-administrador-apenas-para-testes-123456789"}
    rede = cliente.post("/lojas/redes", headers=admin, json={"nome": "Rede Digital"}).json()
    programa = cliente.post("/lojas/programas", headers=admin, json={"rede_id": rede["id"], "nome": "Cartão Digital", "modalidade": "LOJA_DIGITAL"}).json()
    loja = cliente.post("/lojas/parceiras", headers=admin, json={"nome": "Canal Digital", "estado": "SP", "cidade": "São José dos Campos", "endereco": "Canal digital", "cep": "12210000", "programa_id": programa["id"]}).json()
    busca = cliente.get("/lojas/parceiras", params={"cep": "20040020", "modalidade": "LOJA_DIGITAL"})
    assert busca.json()["lojas"][0]["id"] == loja["id"]
    payload = {"nome": "Pessoa Teste", "cpf": "98765432100", "email": "teste@example.com", "telefone": "12999998888", "cep": "20040020", "tipo_cartao": "LOJA_DIGITAL", "loja_id": loja["id"]}
    assert cliente.post("/solicitacoes/", json=payload).status_code == 201
