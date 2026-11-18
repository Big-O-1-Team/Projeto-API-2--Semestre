import base64
import hashlib
import hmac
import os
import smtplib
import ssl
import time
from email.message import EmailMessage
from urllib.parse import quote


def segredo_email():
    segredo = os.getenv("AUTH_SECRET", "")
    if len(segredo) < 32:
        raise ValueError("Confirmação por e-mail não configurada.")
    return segredo


def gerar_token_confirmacao(interesse_id: int):
    validade = int(time.time()) + 86400
    conteudo = f"{interesse_id}:{validade}"
    assinatura = hmac.new(segredo_email().encode(), conteudo.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{conteudo}:{assinatura}".encode()).decode()


def validar_token_confirmacao(token: str):
    try:
        texto = base64.urlsafe_b64decode(token.encode()).decode()
        id_texto, validade_texto, assinatura = texto.split(":")
        interesse_id = int(id_texto)
        validade = int(validade_texto)
        conteudo = f"{interesse_id}:{validade}"
        esperada = hmac.new(segredo_email().encode(), conteudo.encode(), hashlib.sha256).hexdigest()
        if interesse_id <= 0 or validade <= time.time():
            raise ValueError
        if not hmac.compare_digest(assinatura, esperada):
            raise ValueError
        return interesse_id
    except (ValueError, TypeError, UnicodeError, base64.binascii.Error) as erro:
        raise ValueError("Link de confirmação inválido ou expirado.") from erro


def enviar_confirmacao(email: str, token: str):
    host = os.getenv("SMTP_HOST", "")
    remetente = os.getenv("SMTP_FROM", "")
    usuario = os.getenv("SMTP_USER", "")
    senha = os.getenv("SMTP_PASSWORD", "")
    if not all([host, remetente, usuario, senha]):
        return False

    porta = int(os.getenv("SMTP_PORT", "587"))
    base = os.getenv("PUBLIC_API_URL", "").rstrip("/")
    if not (base.startswith("https://") or base.startswith("http://localhost:") or base.startswith("http://127.0.0.1:")):
        raise ValueError("Configure PUBLIC_API_URL com um endereço HTTPS.")

    link = f"{base}/ofertas/confirmar?token={quote(token)}"
    mensagem = EmailMessage()
    mensagem["Subject"] = "Confirme seu interesse em ofertas"
    mensagem["From"] = remetente
    mensagem["To"] = email
    mensagem.set_content(
        "Você solicitou receber informações sobre outras opções da DM.\n\n"
        f"Confirme seu interesse acessando este link, válido por 24 horas:\n{link}\n\n"
        "Se não fez a solicitação, desconsidere esta mensagem."
    )
    if porta == 465:
        with smtplib.SMTP_SSL(host, porta, timeout=10, context=ssl.create_default_context()) as servidor:
            servidor.login(usuario, senha)
            servidor.send_message(mensagem)
    else:
        with smtplib.SMTP(host, porta, timeout=10) as servidor:
            servidor.starttls(context=ssl.create_default_context())
            servidor.login(usuario, senha)
            servidor.send_message(mensagem)
    return True
