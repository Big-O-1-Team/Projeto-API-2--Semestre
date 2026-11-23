import json
import re
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

BASE = Path(__file__).resolve().parent
DB_FILE = BASE / "dados.db"

CARTOES = {
    "DM": "Cartão DM",
    "LOJA_FISICA": "Cartão Loja Física",
    "LOJA_DIGITAL": "Cartão Loja Digital",
}

LOJAS = [
    ("Loja Parceira Centro", "São José dos Campos", "SP", "Rua Central, 120"),
    ("Loja Parceira Aquarius", "São José dos Campos", "SP", "Avenida Principal, 850"),
    ("Loja Parceira Campinas", "Campinas", "SP", "Rua das Flores, 300"),
    ("Loja Parceira São Paulo", "São Paulo", "SP", "Praça Central, 45"),
    ("Loja Parceira Carioca", "Rio de Janeiro", "RJ", "Avenida Central, 400"),
    ("Loja Parceira Mineira", "Belo Horizonte", "MG", "Rua Minas, 210"),
    ("Loja Parceira Curitiba", "Curitiba", "PR", "Rua Paraná, 610"),
    ("Loja Parceira Salvador", "Salvador", "BA", "Avenida Bahia, 95"),
]


def numeros(valor):
    return re.sub(r"\D", "", str(valor or ""))


def cpf_valido(valor):
    cpf = numeros(valor)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[indice]) * (tamanho + 1 - indice) for indice in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if int(cpf[tamanho]) != digito:
            return False
    return True


def uf_por_cep(valor):
    cep = numeros(valor)
    if len(cep) != 8 or cep == "00000000":
        raise ValueError("Informe um CEP com 8 números.")
    inicio = int(cep[:2])
    faixas = [
        (1, 19, "SP"), (20, 28, "RJ"), (29, 29, "ES"),
        (30, 39, "MG"), (40, 48, "BA"), (49, 49, "SE"),
        (50, 56, "PE"), (57, 57, "AL"), (58, 58, "PB"),
        (59, 59, "RN"), (60, 63, "CE"), (64, 64, "PI"),
        (65, 65, "MA"), (66, 68, "PA"), (69, 69, "AM"),
        (70, 72, "DF"), (73, 76, "GO"), (77, 77, "TO"),
        (78, 78, "MT"), (79, 79, "MS"), (80, 87, "PR"),
        (88, 89, "SC"), (90, 99, "RS"),
    ]
    excecoes = {"689": "AP", "693": "RR", "699": "AC"}
    if cep[:3] in excecoes:
        return excecoes[cep[:3]]
    for minimo, maximo, estado in faixas:
        if minimo <= inicio <= maximo:
            return estado
    raise ValueError("Não foi possível identificar o estado do CEP.")


def conectar(caminho=None):
    conexao = sqlite3.connect(str(caminho or DB_FILE))
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def preparar_banco(caminho=None):
    with conectar(caminho) as banco:
        banco.executescript("""
            CREATE TABLE IF NOT EXISTS lojas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cidade TEXT NOT NULL,
                uf TEXT NOT NULL,
                endereco TEXT NOT NULL,
                UNIQUE(nome, cidade, uf)
            );
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                cep TEXT NOT NULL,
                cartao TEXT NOT NULL,
                loja_id INTEGER REFERENCES lojas(id),
                status TEXT NOT NULL DEFAULT 'EM_ANALISE',
                criado_em TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_pedidos_cpf ON pedidos(cpf);
        """)
        banco.executemany(
            "INSERT OR IGNORE INTO lojas(nome, cidade, uf, endereco) VALUES (?, ?, ?, ?)",
            LOJAS,
        )


def buscar_lojas(cep, caminho=None):
    uf = uf_por_cep(cep)
    with conectar(caminho) as banco:
        lojas = banco.execute(
            "SELECT id, nome, cidade, uf, endereco FROM lojas WHERE uf = ? ORDER BY cidade, nome",
            (uf,),
        ).fetchall()
    return {"uf": uf, "total": len(lojas), "lojas": [dict(loja) for loja in lojas]}


def cadastrar_pedido(dados, caminho=None):
    if not isinstance(dados, dict):
        raise ValueError("Dados de solicitação inválidos.")
    nome = str(dados.get("nome") or "").strip()
    cpf = numeros(dados.get("cpf"))
    email = str(dados.get("email") or "").strip().lower()
    telefone = numeros(dados.get("telefone"))
    cep = numeros(dados.get("cep"))
    cartao = dados.get("cartao")
    loja_id = dados.get("loja_id")

    if len(nome) < 3 or len(nome) > 100:
        raise ValueError("Informe seu nome completo.")
    if not cpf_valido(cpf):
        raise ValueError("Informe um CPF válido.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 150:
        raise ValueError("Informe um e-mail válido.")
    if len(telefone) not in (10, 11):
        raise ValueError("Informe um telefone com DDD.")
    uf = uf_por_cep(cep)
    if cartao not in CARTOES:
        raise ValueError("Escolha um tipo de cartão.")

    with conectar(caminho) as banco:
        if cartao == "LOJA_FISICA":
            if not isinstance(loja_id, int) or isinstance(loja_id, bool) or loja_id < 1:
                raise ValueError("Selecione uma loja parceira.")
            loja = banco.execute("SELECT uf FROM lojas WHERE id = ?", (loja_id,)).fetchone()
            if loja is None or loja["uf"] != uf:
                raise ValueError("A loja precisa estar no estado do CEP informado.")
        elif loja_id is not None:
            raise ValueError("Esse cartão não permite selecionar uma loja física.")

        criado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cursor = banco.execute(
            "INSERT INTO pedidos(nome, cpf, email, telefone, cep, cartao, loja_id, status, criado_em) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, cpf, email, telefone, cep, cartao, loja_id, "EM_ANALISE", criado_em),
        )
        return {"id": cursor.lastrowid, "cartao": CARTOES[cartao], "status": "EM_ANALISE", "criado_em": criado_em}


def consultar_pedidos(cpf, caminho=None):
    if not cpf_valido(cpf):
        raise ValueError("Informe um CPF válido.")
    with conectar(caminho) as banco:
        resultados = banco.execute(
            "SELECT p.id, p.cartao, p.status, p.criado_em, l.nome AS loja "
            "FROM pedidos p LEFT JOIN lojas l ON l.id = p.loja_id "
            "WHERE p.cpf = ? ORDER BY p.id DESC LIMIT 50",
            (numeros(cpf),),
        ).fetchall()
    return [{**dict(registro), "cartao": CARTOES[registro["cartao"]]} for registro in resultados]


class Aplicacao(BaseHTTPRequestHandler):
    arquivos = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/index.html": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css; charset=utf-8"),
        "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    }

    def responder(self, codigo, dados):
        conteudo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(conteudo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(conteudo)

    def do_GET(self):
        rota = urlsplit(self.path)
        parametros = parse_qs(rota.query)
        try:
            if rota.path == "/api/cartoes":
                return self.responder(200, [{"codigo": codigo, "nome": nome} for codigo, nome in CARTOES.items()])
            if rota.path == "/api/lojas":
                return self.responder(200, buscar_lojas(parametros.get("cep", [""])[0]))
            if rota.path == "/api/pedidos":
                return self.responder(200, consultar_pedidos(parametros.get("cpf", [""])[0]))
            if rota.path == "/api/health":
                return self.responder(200, {"status": "ok"})
            arquivo = self.arquivos.get(rota.path)
            if arquivo is None:
                return self.responder(404, {"erro": "Página não encontrada."})
            conteudo = (BASE / arquivo[0]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", arquivo[1])
            self.send_header("Content-Length", str(len(conteudo)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(conteudo)
        except ValueError as erro:
            self.responder(422, {"erro": str(erro)})
        except OSError:
            self.responder(500, {"erro": "Não foi possível consultar os dados."})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/pedidos":
            return self.responder(404, {"erro": "Recurso não encontrado."})
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho <= 0 or tamanho > 16384:
                return self.responder(413, {"erro": "Tamanho da solicitação inválido."})
            dados = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            pedido = cadastrar_pedido(dados)
            self.responder(201, pedido)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.responder(400, {"erro": "Envie os dados em formato JSON."})
        except ValueError as erro:
            self.responder(422, {"erro": str(erro)})
        except sqlite3.Error:
            self.responder(500, {"erro": "Não foi possível salvar a solicitação."})

    def log_message(self, formato, *argumentos):
        pass


def iniciar():
    preparar_banco()
    servidor = ThreadingHTTPServer(("127.0.0.1", 8000), Aplicacao)
    print("Aplicação disponível em http://127.0.0.1:8000")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()


if __name__ == "__main__":
    iniciar()
