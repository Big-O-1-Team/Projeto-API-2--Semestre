import os
import time
from collections import defaultdict, deque
from threading import Lock
from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

limite = max(1, int(os.getenv("RATE_LIMIT_POR_MINUTO", "120")))
requisicoes = defaultdict(deque)
bloqueio = Lock()


async def limitar_requisicoes(request: Request, call_next):
    if request.url.path in {"/health", "/openapi.json", "/docs", "/redoc"}:
        return await call_next(request)

    ip = request.client.host if request.client else "desconhecido"
    agora = time.monotonic()
    with bloqueio:
        historico = requisicoes[ip]
        while historico and agora - historico[0] >= 60:
            historico.popleft()
        if len(historico) >= limite:
            espera = max(1, int(61 - (agora - historico[0])))
            return JSONResponse(
                status_code=429,
                content={"detail": "Muitas solicitações. Tente novamente em instantes."},
                headers={"Retry-After": str(espera)},
            )
        historico.append(agora)
        if len(requisicoes) > 10000:
            for chave, valores in list(requisicoes.items()):
                if not valores or agora - valores[-1] >= 60:
                    del requisicoes[chave]

    return await call_next(request)


limite_consulta = max(1, int(os.getenv("RATE_LIMIT_CONSULTAS", "10")))
consultas_por_ip = defaultdict(deque)


def verificar_limite_consulta(request: Request):
    ip = request.client.host if request.client else "desconhecido"
    agora = time.monotonic()
    with bloqueio:
        historico = consultas_por_ip[ip]
        while historico and agora - historico[0] >= 60:
            historico.popleft()
        if len(historico) >= limite_consulta:
            espera = max(1, int(61 - (agora - historico[0])))
            raise HTTPException(
                status_code=429,
                detail="Muitas consultas. Tente novamente em instantes.",
                headers={"Retry-After": str(espera)},
            )
        historico.append(agora)
        if len(consultas_por_ip) > 10000:
            for chave, valores in list(consultas_por_ip.items()):
                if not valores or agora - valores[-1] >= 60:
                    del consultas_por_ip[chave]
