from tests.base import TesteBase


class TesteForum(TesteBase):
    def test_lista_topicos(self):
        resposta = self.cliente.get("/forum/topicos")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 5)

    def test_cria_topico_com_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Como estudar Flask?",
                "descricao": "Quero dicas para organizar o backend.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Desenvolvimento Web",
                "categoria": "Duvida",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["autor"]["id"], 1)

    def test_renderiza_forum_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Forum academico", resposta.data)
        self.assertIn(b"Novo topico", resposta.data)
        self.assertIn(b"Ver topico", resposta.data)

    def test_renderiza_criar_topico_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum/criar", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Criar topico", resposta.data)
        self.assertIn(b"Publicar topico", resposta.data)

    def test_usuario_cria_topico_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/criar",
            data={
                "titulo": "Duvida sobre testes",
                "descricao": "Como organizar testes do projeto?",
                "curso": "Ciencia da Computacao",
                "disciplina": "Desenvolvimento Web",
                "categoria": "Duvida",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/", resposta.headers["Location"])

    def test_renderiza_detalhes_do_topico_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum/topicos/1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Voltar para o forum", resposta.data)
        self.assertIn(b"Respostas", resposta.data)
        self.assertIn(b"Escreva sua resposta", resposta.data)

    def test_usuario_responde_topico_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos/1/respostas",
            data={"conteudo": "Resposta pelo formulario."},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/1", resposta.headers["Location"])

    def test_usuario_comum_nao_cria_aviso(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Aviso teste",
                "descricao": "Aviso oficial",
                "curso": "Ciencia da Computacao",
                "disciplina": "Geral",
                "categoria": "Aviso",
                "tipo": "aviso",
            },
        )

        self.assertEqual(resposta.status_code, 403)

    def test_moderador_cria_aviso(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Aviso de monitoria",
                "descricao": "Monitoria extra nesta semana.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Calculo I",
                "categoria": "Aviso",
                "tipo": "aviso",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertTrue(resposta.json["data"]["aviso_oficial"])

    def test_nao_responde_topico_fechado(self):
        self.login_usuario(3)
        self.cliente.patch("/forum/topicos/1/fechar")
        self.logout_usuario()
        self.login_usuario(1)

        resposta = self.cliente.post(
            "/forum/topicos/1/respostas",
            json={"conteudo": "Tentando responder."},
        )

        self.assertEqual(resposta.status_code, 400)

    def test_usuario_comum_nao_promove_topico_para_aviso_oficial(self):
        self.login_usuario(1)
        resposta = self.cliente.put(
            "/forum/topicos/1",
            json={
                "tipo": "aviso",
                "status": "fechado",
                "aviso_oficial": True,
            },
        )

        self.assertEqual(resposta.status_code, 403)
