from app.database import SessionLocal
from app.models.card import Card
from app.models.card_program import PartnerNetwork, CardProgram
from app.models.collaborator import Collaborator
from app.models.partner_store import PartnerStore


CARTOES = [
    {
        "nome": "Cartão DM",
        "tipo": "DM",
        "descricao": "Cartão DM para iniciar sua solicitação de crédito.",
        "fisico": True,
        "restricao_geografica": False,
    },
    {
        "nome": "Cartão Loja Física",
        "tipo": "LOJA_FISICA",
        "descricao": "Cartão vinculado a uma loja parceira disponível no seu estado.",
        "fisico": True,
        "restricao_geografica": True,
    },
    {
        "nome": "Cartão Loja Digital",
        "tipo": "LOJA_DIGITAL",
        "descricao": "Cartão Loja Digital sem via física e sem restrição de estado.",
        "fisico": False,
        "restricao_geografica": False,
    },
]

LOJAS = [
    ("Loja Parceira Centro SJC", "SP", "São José dos Campos", "Rua Central, 120", "12210000"),
    ("Loja Parceira Jardim Aquarius", "SP", "São José dos Campos", "Avenida Principal, 850", "12246000"),
    ("Loja Parceira Centro SP", "SP", "São Paulo", "Praça Central, 45", "01001000"),
    ("Loja Parceira Campinas", "SP", "Campinas", "Rua das Flores, 300", "13010000"),
    ("Loja Parceira Centro RJ", "RJ", "Rio de Janeiro", "Avenida Central, 400", "20040020"),
    ("Loja Parceira Centro BH", "MG", "Belo Horizonte", "Rua Minas, 210", "30110008"),
    ("Loja Parceira Centro Curitiba", "PR", "Curitiba", "Rua Paraná, 610", "80010000"),
    ("Loja Parceira Centro Salvador", "BA", "Salvador", "Avenida Bahia, 95", "40020000"),
]

COLABORADORES_FICTICIOS = [
    {"cpf": "32376226643", "nome": "Colaborador Fictício 01", "email": "colaborador01@example.com", "telefone": "12990000001", "cep": "12210000", "modalidade_autorizada": "DM", "ativo": True},
    {"cpf": "33143237945", "nome": "Colaborador Fictício 02", "email": "colaborador02@example.com", "telefone": "12990000002", "cep": "12210000", "modalidade_autorizada": "DM", "ativo": True},
    {"cpf": "21953320694", "nome": "Colaborador Fictício 03", "email": "colaborador03@example.com", "telefone": "12990000003", "cep": "12210000", "modalidade_autorizada": "DM", "ativo": True},
    {"cpf": "63380575747", "nome": "Colaborador Fictício 04", "email": "colaborador04@example.com", "telefone": "12990000004", "cep": "12210000", "modalidade_autorizada": "DM", "ativo": True},
]


def seed_database():
    db = SessionLocal()
    try:
        for cartao in CARTOES:
            existe = db.query(Card).filter(Card.tipo == cartao["tipo"]).first()
            if not existe:
                db.add(Card(**cartao))

        for nome, estado, cidade, endereco, cep in LOJAS:
            existe = db.query(PartnerStore).filter(PartnerStore.nome == nome).first()
            if not existe:
                db.add(
                    PartnerStore(
                        nome=nome,
                        estado=estado,
                        cidade=cidade,
                        endereco=endereco,
                        cep=cep,
                        ativo=True,
                    )
                )

        rede = db.query(PartnerNetwork).filter_by(nome="Rede Demonstração").first()
        if rede is None:
            rede = PartnerNetwork(nome="Rede Demonstração")
            db.add(rede)
            db.flush()
        programa = db.query(CardProgram).filter_by(rede_id=rede.id, nome="Cartão Rede Demonstração", modalidade="LOJA_FISICA").first()
        if programa is None:
            programa = CardProgram(rede_id=rede.id, nome="Cartão Rede Demonstração", modalidade="LOJA_FISICA")
            db.add(programa)
            db.flush()
            for loja in db.query(PartnerStore).filter(PartnerStore.nome.in_(["Loja Parceira Centro SJC", "Loja Parceira Jardim Aquarius"])).all():
                if not loja.programas:
                    loja.programas.append(programa)
            for nome, lat, lon in [("Loja Parceira Centro SJC", -23.186, -45.884), ("Loja Parceira Jardim Aquarius", -23.222, -45.913)]:
                db.query(PartnerStore).filter_by(nome=nome, latitude=None, longitude=None).update({"latitude": lat, "longitude": lon}, synchronize_session=False)
        digital = db.query(CardProgram).filter_by(rede_id=rede.id, nome="Cartão Digital Demonstração", modalidade="LOJA_DIGITAL").first()
        if digital is None:
            digital = CardProgram(rede_id=rede.id, nome="Cartão Digital Demonstração", modalidade="LOJA_DIGITAL")
            db.add(digital)
            db.flush()
            loja_digital = PartnerStore(nome="Parceiro Digital Demonstração", estado="SP", cidade="São José dos Campos", endereco="Canal digital", cep="12210000", ativo=True)
            loja_digital.programas.append(digital)
            db.add(loja_digital)

        for dados in COLABORADORES_FICTICIOS:
            existe = db.query(Collaborator).filter(Collaborator.cpf == dados["cpf"]).first()
            if not existe:
                db.add(Collaborator(**dados))

        db.commit()
    finally:
        db.close()
