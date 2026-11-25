import json
import re
from urllib.error import URLError
from urllib.request import urlopen


def limpar_cep(cep: str) -> str:
    return re.sub(r"\D", "", cep or "")


def obter_uf_por_cep(cep: str) -> str:
    cep_limpo = limpar_cep(cep)
    if len(cep_limpo) != 8:
        raise ValueError("CEP inválido. Informe 8 números.")

    try:
        with urlopen(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
    except (URLError, TimeoutError, ValueError) as erro:
        raise ValueError("Não foi possível validar o CEP. Tente novamente.") from erro
    if dados.get("erro") or not dados.get("uf"):
        raise ValueError("CEP não encontrado.")
    return dados["uf"].upper()
