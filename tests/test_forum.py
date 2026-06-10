from tests.base import TesteBase


class TesteForum(TesteBase):
    def test_renderiza_forum_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Forum academico", resposta.data)
        self.assertIn(b"Novo topico", resposta.data)
        self.assertIn(b"Ver topico", resposta.data)

    def test_usuario_cria_topico_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/criar",
            data={
                "titulo": "Duvida sobre testes",
                "descricao": "Como organizar testes do projeto?",
                "curso": "Ciencia da Computacao",
                "categoria": "Duvida",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/", resposta.headers["Location"])

    def test_moderador_cria_aviso(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Aviso de monitoria",
                "descricao": "Monitoria extra nesta semana.",
                "curso": "Ciencia da Computacao",
                "categoria": "Aviso",
                "tipo": "aviso",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertTrue(resposta.json["data"]["aviso_oficial"])
