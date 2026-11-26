import hmac
import os
import math
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload, joinedload
from app.database import get_db
from app.models.partner_store import PartnerStore
from app.models.card_program import PartnerNetwork, CardProgram, programa_unidades
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.schemas.partner_store import PartnerStoreResponse, PartnerStoreSearchResponse, StoreEmissionUpdate, PartnerStoreCreate, NetworkCreate, ProgramCreate, StoreProgramUpdate, StoreSearch
from app.services.cep_service import limpar_cep, obter_uf_por_cep
from app.models.partner_contributor import PartnerContributor
from app.schemas.partner import PartnerContributorPublic

router = APIRouter(prefix="/lojas", tags=["Lojas parceiras"])

@router.get("/parceiras/{loja_id}/contribuidores", response_model=list[PartnerContributorPublic])
def listar_contribuidores_da_loja(
    loja_id: int,
    db: Session = Depends(get_db)):
    loja = db.query(PartnerStore).filter(PartnerStore.id == loja_id, PartnerStore.ativo.is_(True)).first()
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")
    return db.query(PartnerContributor).filter(PartnerContributor.loja_id == loja_id, PartnerContributor.ativo.is_(True)).order_by(PartnerContributor.nome).all()

def distancia_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    valor = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return round(6371 * 2 * math.asin(min(1, math.sqrt(valor))), 2)


@router.get("/parceiras", response_model=PartnerStoreSearchResponse)
def buscar_lojas_parceiras(
    cep: str = "",
    modalidade: str = "LOJA_FISICA",
    busca: str = Query(default="", max_length=120),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return pesquisar_lojas(cep, modalidade, None, None, busca, pagina, limite, db)


@router.post("/buscar", response_model=PartnerStoreSearchResponse)
def buscar_por_localizacao(dados: StoreSearch, db: Session = Depends(get_db)):
    return pesquisar_lojas(dados.cep, dados.modalidade, dados.latitude, dados.longitude, dados.busca, dados.pagina, dados.limite, db)


def pesquisar_lojas(cep, modalidade, latitude, longitude, busca, pagina, limite, db):
    if modalidade not in ("LOJA_FISICA", "LOJA_DIGITAL"):
        raise HTTPException(400, "Modalidade inválida.")
    if (latitude is None) != (longitude is None):
        raise HTTPException(400, "Informe latitude e longitude juntas.")
    cep_limpo = limpar_cep(cep)
    uf = ""
    consulta = db.query(PartnerStore, CardProgram).outerjoin(programa_unidades, programa_unidades.c.loja_id == PartnerStore.id).outerjoin(CardProgram, CardProgram.id == programa_unidades.c.programa_id).outerjoin(PartnerNetwork, PartnerNetwork.id == CardProgram.rede_id)
    consulta = consulta.options(selectinload(PartnerStore.programas).joinedload(CardProgram.rede), joinedload(CardProgram.rede))
    consulta = consulta.filter(PartnerStore.ativo.is_(True))
    programa_ativo = (CardProgram.ativo.is_(True) & PartnerNetwork.ativo.is_(True))
    if modalidade == "LOJA_FISICA":
        try:
            uf = obter_uf_por_cep(cep_limpo)
        except ValueError as erro:
            raise HTTPException(400, str(erro)) from erro
        consulta = consulta.filter(PartnerStore.estado == uf, or_(programa_unidades.c.programa_id.is_(None), programa_ativo & (CardProgram.modalidade == modalidade)))
    else:
        consulta = consulta.filter(programa_ativo, CardProgram.modalidade == modalidade)
    if busca.strip():
        termo = "%" + busca.strip() + "%"
        consulta = consulta.filter(or_(PartnerStore.nome.ilike(termo), PartnerStore.cidade.ilike(termo), PartnerNetwork.nome.ilike(termo), CardProgram.nome.ilike(termo)))
    consulta = consulta.order_by(PartnerStore.cidade, PartnerStore.nome, PartnerStore.id, CardProgram.id)
    total = consulta.count()
    inicio = (pagina - 1) * limite
    if latitude is None:
        lojas = consulta.offset(inicio).limit(limite).all()
        resposta = [resposta_loja(loja, programa) for loja, programa in lojas]
    else:
        resposta = []
        for loja, programa in consulta.all():
            item = resposta_loja(loja, programa)
            if loja.latitude is not None and loja.longitude is not None:
                item.distancia_km = distancia_km(latitude, longitude, loja.latitude, loja.longitude)
            resposta.append(item)
        resposta.sort(key=lambda loja: (loja.distancia_km is None, loja.distancia_km or 0, loja.id, loja.programa_id or 0))
        resposta = resposta[inicio:inicio + limite]
    return {"cep": cep_limpo, "uf": uf, "total": total, "pagina": pagina, "limite": limite, "lojas": resposta}


def resposta_loja(loja, programa=None):
    item = PartnerStoreResponse.model_validate(loja)
    if programa:
        item.programa_id = programa.id
        item.programa_nome = programa.nome
        item.rede_nome = programa.rede.nome
        item.modalidade = programa.modalidade
    return item


def validar_administrador(token_recebido: str):
    token = os.getenv("ADMIN_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(status_code=503, detail="Acesso administrativo não configurado.")
    if not hmac.compare_digest(token_recebido, token):
        raise HTTPException(status_code=403, detail="Acesso não autorizado.")


@router.post("/parceiras", response_model=PartnerStoreResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_loja_parceira(
    dados: PartnerStoreCreate,
    x_admin_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    validar_administrador(x_admin_token)
    existente = db.query(PartnerStore).filter(
        PartnerStore.nome == dados.nome,
        PartnerStore.cep == dados.cep,
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="Esta loja já está cadastrada.")
    try:
        uf = obter_uf_por_cep(dados.cep)
    except ValueError as erro:
        raise HTTPException(400, str(erro)) from erro
    if uf != dados.estado:
        raise HTTPException(400, "CEP não pertence ao estado informado.")
    if (dados.latitude is None) != (dados.longitude is None):
        raise HTTPException(400, "Informe latitude e longitude juntas.")
    programa = validar_programa(dados.programa_id, db)
    loja = PartnerStore(**dados.model_dump(exclude={"programa_id"}), ativo=True)
    if programa:
        loja.programas.append(programa)
    db.add(loja)
    db.commit()
    db.refresh(loja)
    return loja


@router.put("/parceiras/{loja_id}/emissao", response_model=PartnerStoreResponse)
def atualizar_emissao(
    loja_id: int,
    dados: StoreEmissionUpdate,
    x_admin_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    validar_administrador(x_admin_token)

    loja = db.query(PartnerStore).filter(PartnerStore.id == loja_id).first()
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")
    loja.emite_cartao_credito = dados.emite_cartao_credito
    db.commit()
    db.refresh(loja)
    return loja


def validar_programa(programa_id, db):
    if programa_id is None:
        return
    programa = db.get(CardProgram, programa_id)
    if not programa or not programa.ativo or not programa.rede.ativo:
        raise HTTPException(400, "Programa de cartão inválido ou inativo.")
    return programa


@router.get("/redes")
def listar_redes(db: Session = Depends(get_db)):
    redes = db.query(PartnerNetwork).filter(PartnerNetwork.ativo.is_(True)).order_by(PartnerNetwork.nome).all()
    return [{"id": rede.id, "nome": rede.nome} for rede in redes]


@router.post("/redes", status_code=201)
def cadastrar_rede(dados: NetworkCreate, x_admin_token: str = Header(default=""), db: Session = Depends(get_db)):
    validar_administrador(x_admin_token)
    nome = dados.nome.strip()
    if len(nome) < 2:
        raise HTTPException(400, "Informe o nome da rede.")
    if db.query(PartnerNetwork).filter(PartnerNetwork.nome == nome).first():
        raise HTTPException(409, "Rede já cadastrada.")
    rede = PartnerNetwork(nome=nome)
    db.add(rede)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Rede já cadastrada.") from erro
    db.refresh(rede)
    return {"id": rede.id, "nome": rede.nome}


@router.post("/programas", status_code=201)
def cadastrar_programa(dados: ProgramCreate, x_admin_token: str = Header(default=""), db: Session = Depends(get_db)):
    validar_administrador(x_admin_token)
    rede = db.get(PartnerNetwork, dados.rede_id)
    nome = dados.nome.strip()
    if not rede or not rede.ativo or len(nome) < 2:
        raise HTTPException(400, "Rede ou nome inválido.")
    if db.query(CardProgram).filter_by(rede_id=rede.id, nome=nome, modalidade=dados.modalidade).first():
        raise HTTPException(409, "Programa já cadastrado.")
    programa = CardProgram(rede_id=rede.id, nome=nome, modalidade=dados.modalidade)
    db.add(programa)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(409, "Programa já cadastrado.") from erro
    db.refresh(programa)
    return {"id": programa.id, "nome": programa.nome, "rede_id": rede.id, "modalidade": programa.modalidade}


@router.get("/programas")
def listar_programas(db: Session = Depends(get_db)):
    programas = db.query(CardProgram).join(PartnerNetwork).filter(CardProgram.ativo.is_(True), PartnerNetwork.ativo.is_(True)).order_by(PartnerNetwork.nome, CardProgram.nome).all()
    return [{"id": p.id, "nome": p.nome, "rede": p.rede.nome, "rede_id": p.rede_id, "modalidade": p.modalidade} for p in programas]


@router.put("/parceiras/{loja_id}/programa", response_model=PartnerStoreResponse)
def vincular_programa(loja_id: int, dados: StoreProgramUpdate, x_admin_token: str = Header(default=""), db: Session = Depends(get_db)):
    validar_administrador(x_admin_token)
    loja = db.get(PartnerStore, loja_id)
    if not loja:
        raise HTTPException(404, "Loja não encontrada.")
    programa = validar_programa(dados.programa_id, db)
    if (dados.latitude is None) != (dados.longitude is None):
        raise HTTPException(400, "Informe latitude e longitude juntas.")
    if programa and programa not in loja.programas:
        loja.programas.append(programa)
    if dados.latitude is not None:
        loja.latitude = dados.latitude
        loja.longitude = dados.longitude
    db.commit()
    db.refresh(loja)
    return resposta_loja(loja, programa)
