import json
import re
from urllib.error import URLError
from urllib.request import urlopen


def limpar_cep(cep: str) -> str:
    return re.sub(r"\D", "", cep or "")


def _uf_fallback(cep: str) -> str | None:
    prefixo2 = int(cep[:2])
    prefixo3 = int(cep[:3])

    if 1 <= prefixo2 <= 19:
        return "SP"
    if 20 <= prefixo2 <= 28:
        return "RJ"
    if prefixo2 == 29:
        return "ES"
    if 30 <= prefixo2 <= 39:
        return "MG"
    if 40 <= prefixo2 <= 48:
        return "BA"
    if prefixo2 == 49:
        return "SE"
    if 50 <= prefixo2 <= 56:
        return "PE"
    if prefixo2 == 57:
        return "AL"
    if prefixo2 == 58:
        return "PB"
    if prefixo2 == 59:
        return "RN"
    if 60 <= prefixo2 <= 63:
        return "CE"
    if prefixo2 == 64:
        return "PI"
    if prefixo2 == 65:
        return "MA"
    if 66 <= prefixo2 <= 68:
        if prefixo3 == 689:
            return "AP"
        return "PA"
    if prefixo2 == 69:
        if prefixo3 == 693:
            return "RR"
        if prefixo3 == 699:
            return "AC"
        return "AM"
    if 70 <= prefixo2 <= 72:
        return "DF"
    if 73 <= prefixo2 <= 76:
        return "GO"
    if prefixo2 == 77:
        return "TO"
    if prefixo2 == 78:
        return "MT"
    if prefixo2 == 79:
        return "MS"
    if 80 <= prefixo2 <= 87:
        return "PR"
    if 88 <= prefixo2 <= 89:
        return "SC"
    if 90 <= prefixo2 <= 99:
        return "RS"
    return None


def obter_uf_por_cep(cep: str) -> str:
    cep_limpo = limpar_cep(cep)
    if len(cep_limpo) != 8:
        raise ValueError("CEP inválido. Informe 8 números.")

    try:
        with urlopen(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=2) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
            if not dados.get("erro") and dados.get("uf"):
                return dados["uf"].upper()
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        pass

    uf = _uf_fallback(cep_limpo)
    if not uf:
        raise ValueError("Não foi possível identificar o estado do CEP informado.")
    return uf
