from app.cep import normalizar_cep, uf_do_cep, CepInvalido

class CepService:
    @staticmethod
    def resolver_uf(cep: str) -> str:
        uf = uf_do_cep(normalizar_cep(cep))
        if uf is None:
            raise CepInvalido(cep)
        return uf