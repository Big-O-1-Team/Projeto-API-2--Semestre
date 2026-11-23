import tempfile
import unittest
from pathlib import Path

from app import buscar_lojas, cadastrar_pedido, consultar_pedidos, cpf_valido, preparar_banco


class TesteCadastro(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.banco = Path(self.pasta.name) / "dados.db"
        preparar_banco(self.banco)
        self.dados = {
            "nome": "Cliente de Teste",
            "cpf": "52998224725",
            "email": "cliente@example.com",
            "telefone": "12999998888",
            "cep": "12210000",
            "cartao": "DM",
            "loja_id": None,
        }

    def tearDown(self):
        self.pasta.cleanup()

    def test_cpf(self):
        self.assertTrue(cpf_valido("529.982.247-25"))
        self.assertFalse(cpf_valido("111.111.111-11"))
        self.assertFalse(cpf_valido("52998224720"))

    def test_busca_de_lojas(self):
        lojas = buscar_lojas("12210-000", self.banco)
        self.assertEqual(lojas["uf"], "SP")
        self.assertGreaterEqual(lojas["total"], 3)
        self.assertTrue(all(loja["uf"] == "SP" for loja in lojas["lojas"]))

    def test_solicitar_e_acompanhar(self):
        pedido = cadastrar_pedido(self.dados, self.banco)
        self.assertEqual(pedido["status"], "EM_ANALISE")
        resultado = consultar_pedidos("529.982.247-25", self.banco)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id"], pedido["id"])
        self.assertEqual(resultado[0]["cartao"], "Cartão DM")

    def test_loja_de_outro_estado(self):
        self.dados["cartao"] = "LOJA_FISICA"
        loja_rj = buscar_lojas("20040020", self.banco)["lojas"][0]
        self.dados["loja_id"] = loja_rj["id"]
        with self.assertRaisesRegex(ValueError, "estado"):
            cadastrar_pedido(self.dados, self.banco)

    def test_cartao_loja_comparado_com_cep(self):
        self.dados["cartao"] = "LOJA_FISICA"
        self.dados["loja_id"] = buscar_lojas("12210000", self.banco)["lojas"][0]["id"]
        pedido = cadastrar_pedido(self.dados, self.banco)
        resultado = consultar_pedidos(self.dados["cpf"], self.banco)
        self.assertEqual(resultado[0]["id"], pedido["id"])
        self.assertIsNotNone(resultado[0]["loja"])

    def test_validacao_dados(self):
        self.dados["email"] = "sem-arroba"
        with self.assertRaisesRegex(ValueError, "e-mail"):
            cadastrar_pedido(self.dados, self.banco)
        self.assertEqual(consultar_pedidos("52998224725", self.banco), [])


if __name__ == "__main__":
    unittest.main()
