import httpx

def consultar_cep(cep):
    r = httpx.get(url=f'https://viacep.com.br/ws/{cep}/json/')
    return r.text
