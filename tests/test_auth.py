from tests.base import TesteBase


class TesteAuth(TesteBase):
    def test_login_com_credenciais_validas(self):
        resposta = self.login_usuario(1)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["email"], "lucas.almeida@uvv.br")

    def test_login_html_redireciona_com_formulario_valido(self):
        resposta = self.cliente.post(
            "/auth/login",
            data={"email": "lucas.almeida@uvv.br", "senha": "senha123"},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/dashboard", resposta.headers["Location"])

    def test_cadastro_html_redireciona_com_formulario_valido(self):
        resposta = self.cliente.post(
            "/auth/cadastro",
            data={
                "nome": "Aluno Formulario",
                "email": "aluno.formulario@uvv.br",
                "curso": "Ciencia da Computacao",
                "periodo": "5 periodo",
                "cidade": "Vila Velha",
                "senha": "senha123",
                "confirmacao_senha": "senha123",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/dashboard", resposta.headers["Location"])

    def test_rota_html_protegida_redireciona_para_login(self):
        resposta = self.cliente.get("/forum/criar", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/auth/login", resposta.headers["Location"])
