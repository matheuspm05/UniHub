from tests.base import TesteBase


class TesteAuth(TesteBase):
    def test_login_com_credenciais_validas(self):
        resposta = self.login_usuario(1)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["email"], "lucas.almeida@uvv.br")

    def test_login_com_senha_invalida(self):
        resposta = self.cliente.post(
            "/auth/login",
            json={"email": "lucas.almeida@uvv.br", "senha": "errada"},
        )

        self.assertEqual(resposta.status_code, 401)

    def test_rota_me_exige_login(self):
        resposta = self.cliente.get("/auth/me")

        self.assertEqual(resposta.status_code, 401)

    def test_logout_encerra_sessao(self):
        self.login_usuario(1)
        resposta = self.logout_usuario()
        depois_logout = self.cliente.get("/auth/me")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(depois_logout.status_code, 401)
