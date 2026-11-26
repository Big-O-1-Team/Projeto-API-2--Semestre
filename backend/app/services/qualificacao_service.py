import json
import os


def cpf_valido(cpf):
    if len(cpf) != 11 or not cpf.isascii() or not cpf.isdigit() or len(set(cpf)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if int(cpf[tamanho]) != (0 if digito == 10 else digito):
            return False
    return True


def pre_qualificado(cpf, modalidade):
    if os.getenv("DEMO_PRE_QUALIFICACAO", "0") != "1":
        return False
    try:
        dados = json.loads(os.getenv("PRE_QUALIFICADOS_FICTICIOS") or "{}")
    except ValueError:
        return False
    if not isinstance(dados, dict):
        return False
    modalidades = dados.get(cpf)
    return isinstance(modalidades, list) and modalidade in modalidades
