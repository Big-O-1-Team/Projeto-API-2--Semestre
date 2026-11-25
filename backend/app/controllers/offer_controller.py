import logging
import hashlib
import re
import smtplib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.rate_limit import verificar_limite_consulta
from app.models.application import Application
from app.models.offer_interest import OfferInterest
from app.models.user import User
from app.services.email_service import enviar_confirmacao, gerar_token_confirmacao, validar_token_confirmacao

router = APIRouter(prefix="/ofertas", tags=["Ofertas"])
logger = logging.getLogger(__name__)


class InteresseOferta(BaseModel):
    solicitacao_id: int = Field(gt=0)
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    aceitar: bool
    codigo: str = Field(min_length=20, max_length=120)

    model_config = ConfigDict(extra="forbid")


class ResultadoInteresse(BaseModel):
    situacao: str
    mensagem: str


@router.post("/interesse", response_model=ResultadoInteresse)
def registrar_interesse(
    dados: InteresseOferta,
    request: Request,
    db: Session = Depends(get_db),
):
    verificar_limite_consulta(request)
    if not dados.aceitar:
        raise HTTPException(status_code=400, detail="É necessário aceitar o recebimento de informações.")

    cpf = re.sub(r"\D", "", dados.cpf)
    if len(cpf) != 11:
        raise HTTPException(status_code=400, detail="Informe um CPF com 11 números.")

    registro = (
        db.query(Application, User)
        .join(User, Application.usuario_id == User.id)
        .filter(
            Application.id == dados.solicitacao_id,
            User.cpf == cpf,
            User.email == str(dados.email),
            Application.status == "REPROVADO",
            Application.codigo_consulta_hash == hashlib.sha256(dados.codigo.encode()).hexdigest(),
        )
        .first()
    )
    if registro is None:
        raise HTTPException(status_code=404, detail="Solicitação reprovada não encontrada para os dados informados.")

    interesse = db.query(OfferInterest).filter(
        OfferInterest.solicitacao_id == dados.solicitacao_id
    ).first()

    if interesse is None:
        interesse = OfferInterest(
            solicitacao_id=dados.solicitacao_id,
            email=str(dados.email),
        )
        db.add(interesse)
        try:
            db.commit()
            db.refresh(interesse)
        except IntegrityError:
            db.rollback()
            interesse = db.query(OfferInterest).filter(
                OfferInterest.solicitacao_id == dados.solicitacao_id
            ).first()
            if interesse is None:
                raise

    interesse = db.query(OfferInterest).filter(OfferInterest.solicitacao_id == dados.solicitacao_id).with_for_update().populate_existing().first()
    if interesse.confirmado_em is not None:
        return {"situacao": "CONFIRMADO", "mensagem": "Seu interesse já está confirmado."}
    if interesse.enviado_em is not None:
        return {"situacao": "AGUARDANDO_CONFIRMACAO", "mensagem": "Enviamos um link de confirmação para seu e-mail."}

    try:
        token = gerar_token_confirmacao(interesse.id)
        enviado = enviar_confirmacao(interesse.email, token)
    except (ValueError, OSError, smtplib.SMTPException):
        logger.warning("Falha ao preparar ou enviar confirmação de ofertas.", exc_info=True)
        return {"situacao": "PENDENTE_ENVIO", "mensagem": "Interesse registrado. O envio da confirmação está indisponível no momento."}

    if not enviado:
        return {"situacao": "PENDENTE_ENVIO", "mensagem": "Interesse registrado. O e-mail de confirmação ainda não está configurado."}

    interesse.enviado_em = datetime.utcnow()
    db.commit()
    return {"situacao": "AGUARDANDO_CONFIRMACAO", "mensagem": "Enviamos um link para confirmar seu interesse por e-mail."}


@router.get("/confirmar", response_class=HTMLResponse)
def confirmar_interesse(
    token: str = Query(min_length=20, max_length=1024),
    db: Session = Depends(get_db),
):
    try:
        interesse_id = validar_token_confirmacao(token)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

    interesse = db.get(OfferInterest, interesse_id)
    if interesse is None:
        raise HTTPException(status_code=404, detail="Interesse não encontrado.")

    if interesse.confirmado_em is None:
        interesse.confirmado_em = datetime.utcnow()
        db.commit()

    return HTMLResponse(
        content="""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Interesse confirmado | DM</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f4f6ff;color:#17204b;font:16px system-ui,Arial,sans-serif;padding:20px;box-sizing:border-box}main{max-width:520px;background:white;padding:40px;border-radius:20px;box-shadow:0 16px 45px #101b4720;text-align:center}h1{font-size:1.8rem}p{line-height:1.6}span{display:inline-grid;place-items:center;width:64px;height:64px;border-radius:50%;background:#e6f6ed;color:#146e3b;font-size:34px}a{color:#2329c5}</style></head><body><main><span aria-hidden="true">✓</span><h1>Interesse confirmado!</h1><p>Seu endereço foi confirmado para receber informações sobre outras opções. A disponibilidade dos produtos depende das condições de cada oferta.</p></main></body></html>""",
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
