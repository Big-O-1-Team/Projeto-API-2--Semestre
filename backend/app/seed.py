from app.database import SessionLocal
from app.models.card import Card
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
        "descricao": "Opção digital do Cartão Loja.",
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

        db.commit()
    finally:
        db.close()
