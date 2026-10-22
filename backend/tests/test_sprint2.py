import asyncio
import sys
from pathlib import Path
from pydantic import ValidationError
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.application import ApplicationCreate
from app.services.collaborator_service import autenticar_colaborador, gerar_token, validar_token
from app.middleware import rate_limit
from starlette.requests import Request
from starlette.responses import Response


def test_dto():
    dados = ApplicationCreate(nome="Pessoa Exemplo", cpf="123.456.789-01", email="teste@example.com", telefone="(12) 99999-9999", cep="12210-000", tipo_cartao="DM")
    assert dados.cpf == "12345678901"
    assert dados.cep == "12210000"
    with pytest.raises(ValidationError):
        ApplicationCreate(nome="Ex", cpf="123", email="invalido", telefone="123", cep="12", tipo_cartao="INVALIDO")


def test_colaborador(monkeypatch):
    monkeypatch.setenv("COLABORADORES_DM", '{"12345678901":"senha-exemplo"}')
    monkeypatch.setenv("AUTH_SECRET", "segredo-unicamente-para-testes-123456789012345678")
    assert autenticar_colaborador("12345678901", "senha-exemplo")
    assert not autenticar_colaborador("12345678901", "senha-incorreta")
    assert validar_token(gerar_token("12345678901")) == "12345678901"


def test_rate_limit():
    async def verificar():
        anterior = rate_limit.limite
        rate_limit.limite = 2
        rate_limit.requisicoes.clear()
        try:
            request = Request({"type": "http", "method": "GET", "path": "/", "raw_path": b"/", "query_string": b"", "headers": [], "client": ("127.0.0.1", 1111), "server": ("test", 80), "scheme": "http"})
            async def continuar(_):
                return Response("ok")
            assert (await rate_limit.limitar_requisicoes(request, continuar)).status_code == 200
            assert (await rate_limit.limitar_requisicoes(request, continuar)).status_code == 200
            assert (await rate_limit.limitar_requisicoes(request, continuar)).status_code == 429
        finally:
            rate_limit.limite = anterior
            rate_limit.requisicoes.clear()
    asyncio.run(verificar())
