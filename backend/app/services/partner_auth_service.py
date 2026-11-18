import base64
import hashlib
import hmac
import os
import secrets
import time
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.partner_account import PartnerAccount

def segredo_autenticacao():
    segredo = os.getenv("AUTH_SECRET", "")
    if len(segredo) < 32:
        raise HTTPException(
            status_code=503,
            detail="Autenticação não configurada.")
    return segredo

def gerar_hash_senha(senha):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode(),
        salt.encode(),
        260000
    ).hex()
    return f"{salt}${digest}"

def verificar_senha(senha, senha_hash):
    try:
        salt, esperado = senha_hash.split("$", 1)
        recebido = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode(),
            salt.encode(),
            260000
        ).hex()
        return hmac.compare_digest(recebido, esperado)

    except ValueError:
        return False

def gerar_token_parceiro(conta):
    expiracao = int(time.time()) + 3600
    conteudo = f"{conta.id}:{conta.loja_id}:{expiracao}"
    assinatura = hmac.new(
        segredo_autenticacao().encode(),
        conteudo.encode(),
        hashlib.sha256
    ).hexdigest()
    token = f"{conteudo}:{assinatura}"
    return base64.urlsafe_b64encode(token.encode()).decode()

def validar_token_parceiro(token, db: Session):
    try:
        dados = base64.urlsafe_b64decode(token.encode()).decode()
        conta_id, loja_id, expiracao, assinatura = dados.split(":")
        conteudo = f"{conta_id}:{loja_id}:{expiracao}"
        esperada = hmac.new(
            segredo_autenticacao().encode(),
            conteudo.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(assinatura, esperada):
            raise ValueError
        if int(expiracao) <= time.time():
            raise ValueError

        conta = db.query(PartnerAccount).filter(
            PartnerAccount.id == int(conta_id),
            PartnerAccount.loja_id == int(loja_id),
            PartnerAccount.ativo.is_(True)
        ).first()

        if not conta:
            raise ValueError
        return conta

    except (ValueError, UnicodeError, TypeError) as erro:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada."
        ) from erro
