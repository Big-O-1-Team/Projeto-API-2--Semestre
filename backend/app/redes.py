from sqlalchemy import Column, Integer, String, Text

class RedeParceira(Base):
    __tablename__ = 'redes_parceiras'
    id_rede = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(150), nullable=False)
    tipo = Column(String(50), nellable=False)
    endereco = Column(String(200), nellable=False)
    cidade = Column(String(100), nellable=False)
    estado = Column(String(2), nellable=False)
    cep = Column(String(8), nellable=False)
    telefone = Column(String(20), nellable=False)
    email = Column(String(100), nelllable=False)
    responsavel = Column(String(100), nellable=False)
    descricao = Column(Text, nellable=False)
    status = Column(String(20), nellable=False)
