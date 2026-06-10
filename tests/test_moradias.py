from tests.base import TesteBase


class TesteMoradias(TesteBase):
    def test_renderiza_tela_de_moradias_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Moradias estudantis", resposta.data)
        self.assertIn(b"Anunciar moradia", resposta.data)
        self.assertIn(b"Meus anuncios", resposta.data)
        self.assertIn(b"Usuario", resposta.data)
        self.assertNotIn(b"Matricula:", resposta.data)
        self.assertIn(b"imagem%20padrao%20moradia.png", resposta.data)

    def test_renderiza_detalhes_de_moradia_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias/1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Voltar para moradias", resposta.data)
        self.assertIn(b"Publicado por", resposta.data)
        self.assertIn(b"Ver perfil", resposta.data)
        self.assertIn(b"Contato externo", resposta.data)
        self.assertIn(b"imagem%20padrao%20moradia.png", resposta.data)

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
                "contato_externo": "contato@moradia.com",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["anunciante"]["id"], 1)

    def test_filtro_preco_invalido_retorna_400(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias?preco_min=abc")

        self.assertEqual(resposta.status_code, 400)
