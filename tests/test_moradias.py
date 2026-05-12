from tests.base import TesteBase


class TesteMoradias(TesteBase):
    def test_lista_moradias(self):
        resposta = self.cliente.get("/moradias")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 3)

    def test_cria_moradia(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/moradias",
            json={
                "titulo": "Quarto perto da faculdade",
                "descricao": "Quarto mobiliado",
                "bairro": "Boa Vista",
                "preco_mensal": 950,
                "numero_vagas": 1,
                "perto_uvv": True,
                "aceita_dividir_quarto": False,
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["anunciante"]["id"], 1)

    def test_valida_preco_negativo(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/moradias",
            json={
                "titulo": "Moradia invalida",
                "descricao": "Preco errado",
                "bairro": "Centro",
                "preco_mensal": -10,
                "numero_vagas": 1,
            },
        )

        self.assertEqual(resposta.status_code, 400)

    def test_usuario_nao_edita_moradia_de_outro(self):
        self.login_usuario(1)
        resposta = self.cliente.put(
            "/moradias/1",
            json={"titulo": "Tentativa de edicao"},
        )

        self.assertEqual(resposta.status_code, 403)
