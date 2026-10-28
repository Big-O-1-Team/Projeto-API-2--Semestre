import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.middleware import rate_limit


def test_limite_consultas_por_ip(monkeypatch):
    monkeypatch.setattr(rate_limit, "limite_consulta", 2)
    rate_limit.consultas_por_ip.clear()
    request = Request({
        "type": "http",
        "method": "POST",
        "path": "/solicitacoes/consultar",
        "raw_path": b"/solicitacoes/consultar",
        "headers": [],
        "query_string": b"",
        "client": ("127.0.0.1", 1111),
        "server": ("test", 80),
        "scheme": "http",
    })
    try:
        rate_limit.verificar_limite_consulta(request)
        rate_limit.verificar_limite_consulta(request)
        with pytest.raises(HTTPException) as erro:
            rate_limit.verificar_limite_consulta(request)
        assert erro.value.status_code == 429
        assert "Retry-After" in erro.value.headers
    finally:
        rate_limit.consultas_por_ip.clear()
