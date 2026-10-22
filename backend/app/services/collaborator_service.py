import base64
import hashlib
import hmac
import json
import os
import re
import time
from fastapi import HTTPException


def limpar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")


def credenciais_colaboradores() -> dict[str, str]:
    try:
        dados = json.loads(os.getenv("COLABORADORES_DM") or "{}")
    except json.JSONDecodeError as erro:
        raise RuntimeError("COLABORADORES_DM precisa ser um JSON válido.") from erro
    if not isinstance(dados, dict):
        raise RuntimeError("COLABORADORES_DM precisa ser um objeto JSON.")
    return {limpar_cpf(str(cpf)): str(senha) for cpf, senha in dados.items() if len(limpar_cpf(str(cpf))) == 11}


def eh_colaborador(cpf: str) -> bool:
    return limpar_cpf(cpf) in credenciais_colaboradores()


def autenticar_colaborador(cpf: str, senha: str) -> bool:
    senha_esperada = credenciais_colaboradores().get(limpar_cpf(cpf))
    if senha_esperada is None:
        return False
    esperada = hashlib.sha256(senha_esperada.encode()).digest()
    recebida = hashlib.sha256(senha.encode()).digest()
    return hmac.compare_digest(esperada, recebida)


def segredo_autenticacao() -> str:
    segredo = os.getenv("AUTH_SECRET", "")
    if len(segredo) < 32:
        raise HTTPException(status_code=503, detail="Autenticação ainda não foi configurada.")
    return segredo


def gerar_token(cpf: str) -> str:
    expiracao = int(time.time()) + 3600
    conteudo = f"{limpar_cpf(cpf)}:{expiracao}"
    assinatura = hmac.new(segredo_autenticacao().encode(), conteudo.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{conteudo}:{assinatura}".encode()).decode()


def validar_token(token: str) -> str:
    try:
        dados = base64.urlsafe_b64decode(token.encode()).decode()
        cpf, expiracao, assinatura = dados.split(":")
        conteudo = f"{cpf}:{expiracao}"
        esperada = hmac.new(segredo_autenticacao().encode(), conteudo.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(assinatura, esperada) or int(expiracao) <= time.time():
            raise ValueError
        if not eh_colaborador(cpf):
            raise ValueError
        return cpf
    except (ValueError, UnicodeError, base64.binascii.Error) as erro:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.") from erro
