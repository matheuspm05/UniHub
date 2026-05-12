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
