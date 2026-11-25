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
    modo = os.getenv("SMTP_MODE", "smtp").lower()
    if modo == "mailpit":
        host = "mailpit"
        porta = 1025
        remetente = "DM <ofertas@dm.example>"
        base = os.getenv("PUBLIC_API_URL") or "http://localhost:5173/api"
    elif modo == "smtp":
        host = os.getenv("SMTP_HOST", "")
        remetente = os.getenv("SMTP_FROM", "")
        usuario = os.getenv("SMTP_USER", "")
        senha = os.getenv("SMTP_PASSWORD", "")
        if not all([host, remetente, usuario, senha]):
            return False
        porta = int(os.getenv("SMTP_PORT", "587"))
        base = os.getenv("PUBLIC_API_URL", "")
    else:
        return False

    base = base.rstrip("/")
    if not (base.startswith("https://") or base.startswith("http://localhost:") or base.startswith("http://127.0.0.1:")):
        raise ValueError("Configure PUBLIC_API_URL com um endereço HTTPS.")

    link = f"{base}/ofertas/confirmar?token={quote(token)}"
    mensagem = EmailMessage()
    mensagem["Subject"] = "Conheça outras opções da DM"
    mensagem["From"] = remetente
    mensagem["To"] = email
    mensagem.set_content(
        "Olá!\n\n"
        "Não foi possível aprovar a modalidade de cartão solicitada neste momento. "
        "Conheça outras opções da DM:\n\n"
        "• Empréstimo pessoal (EP): crédito para suas necessidades pessoais.\n"
        "• DMCred: outras soluções de crédito conforme seu perfil.\n\n"
        "A disponibilidade e as condições dependem de análise. Nenhuma oferta representa aprovação automática.\n\n"
        f"Se tiver interesse, confirme pelo link válido por 24 horas:\n{link}\n\n"
        "Se não fez a solicitação ou não deseja receber informações, desconsidere este e-mail."
    )
    mensagem.add_alternative(f"""<!doctype html>
<html lang="pt-BR"><body style="margin:0;background:#f4f6ff;font-family:Arial,sans-serif;color:#182546">
<div style="max-width:540px;margin:24px auto;background:#fff;border-radius:12px;padding:28px">
<div style="font-size:30px;font-weight:bold;color:#2329c5">dm.</div>
<h1 style="font-size:24px">Outras opções para você</h1>
<p>Não foi possível aprovar a modalidade de cartão solicitada neste momento.</p>
<div style="border:1px solid #dce1ec;padding:16px;margin:16px 0;border-radius:8px">
<strong>Empréstimo pessoal (EP)</strong><p>Crédito para suas necessidades pessoais.</p>
</div>
<div style="border:1px solid #dce1ec;padding:16px;margin:16px 0;border-radius:8px">
<strong>DMCred</strong><p>Outras soluções de crédito conforme seu perfil.</p>
</div>
<p>A disponibilidade e as condições dependem de análise. Nenhuma oferta representa aprovação automática.</p>
<p><a href="{link}" style="display:inline-block;background:#2329c5;color:#fff;padding:14px 20px;border-radius:8px;text-decoration:none">Confirmar interesse</a></p>
<p style="font-size:13px;color:#606987">Link válido por 24 horas. Se não fez a solicitação ou não deseja receber informações, desconsidere este e-mail.</p>
</div></body></html>""", subtype="html")

    if modo == "mailpit":
        with smtplib.SMTP(host, porta, timeout=5) as servidor:
            servidor.send_message(mensagem)
    elif porta == 465:
        with smtplib.SMTP_SSL(host, porta, timeout=10, context=ssl.create_default_context()) as servidor:
            servidor.login(usuario, senha)
            servidor.send_message(mensagem)
    else:
        with smtplib.SMTP(host, porta, timeout=10) as servidor:
            servidor.starttls(context=ssl.create_default_context())
            servidor.login(usuario, senha)
            servidor.send_message(mensagem)
    return True
