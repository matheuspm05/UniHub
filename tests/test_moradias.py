from tests.base import TesteBase


class TesteMoradias(TesteBase):
    def test_lista_moradias(self):
        resposta = self.cliente.get("/moradias")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 3)

    def test_renderiza_tela_de_moradias_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Moradias estudantis", resposta.data)
        self.assertIn(b"Anunciar moradia", resposta.data)
        self.assertIn(b"Meus anuncios", resposta.data)
        self.assertIn(b"Usuario", resposta.data)
        self.assertIn(b"Matricula:", resposta.data)
        self.assertIn(b"imagem%20padrao%20moradia.png", resposta.data)

    def test_renderiza_detalhes_de_moradia_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias/1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Voltar para moradias", resposta.data)
        self.assertIn(b"Publicado por", resposta.data)
        self.assertIn(b"Enviar mensagem", resposta.data)
        self.assertIn(b"imagem%20padrao%20moradia.png", resposta.data)

    def test_renderiza_tela_de_anunciar_moradia_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias/anunciar", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Anunciar moradia", resposta.data)
        self.assertIn(b"Publicar anuncio", resposta.data)
        self.assertIn(b"Dicas para um bom anuncio", resposta.data)

    def test_publica_moradia_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/moradias/anunciar",
            data={
                "titulo": "Kitnet nova perto da UVV",
                "descricao": "Kitnet mobiliada com internet inclusa.",
                "bairro": "Boa Vista",
                "preco_mensal": "1.050,00",
                "numero_vagas": "1",
                "perto_uvv": "true",
                "aceita_dividir_quarto": "false",
                "status": "disponivel",
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/moradias/", resposta.headers["Location"])

    def test_renderiza_meus_anuncios_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias/meus-anuncios", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Meus anuncios", resposta.data)
        self.assertIn(b"Explorar moradias", resposta.data)
        self.assertIn(b"/moradias/3/editar", resposta.data)
        self.assertIn(b"confirm(", resposta.data)

    def test_renderiza_edicao_de_anuncio_do_usuario(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/moradias/3/editar", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Editar anuncio", resposta.data)
        self.assertIn(b"Salvar alteracoes", resposta.data)
        self.assertIn(b"Confirmar alteracao", resposta.data)

    def test_atualiza_moradia_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/moradias/3/editar",
            data={
                "titulo": "Apartamento atualizado",
                "descricao": "Apartamento atualizado para estudantes.",
                "bairro": "Praia da Costa",
                "preco_mensal": "1.250,00",
                "numero_vagas": "2",
                "perto_uvv": "false",
                "aceita_dividir_quarto": "true",
                "status": "disponivel",
            },
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/moradias/meus-anuncios", resposta.headers["Location"])

    def test_altera_status_pelo_html(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/moradias/3/status",
            data={"status": "pausado"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/moradias/meus-anuncios", resposta.headers["Location"])

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
