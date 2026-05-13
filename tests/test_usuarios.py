from tests.base import TesteBase


class TesteUsuarios(TesteBase):
    def test_lista_usuarios(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/usuarios")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 5)
        self.assertNotIn("email", resposta.json["data"][0])

    def test_lista_usuarios_exige_login(self):
        resposta = self.cliente.get("/usuarios")

        self.assertEqual(resposta.status_code, 401)

    def test_retorna_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/usuarios/me")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["nome"], "Lucas Almeida")

    def test_atualiza_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.patch(
            "/usuarios/me",
            json={"bio": "Estudante da UVV", "selo": "Moderador"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["bio"], "Estudante da UVV")
        self.assertNotEqual(resposta.json["data"]["selo"], "Moderador")

    def test_detalhe_usuario_retorna_perfil_publico(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/usuarios/2")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["nome"], "João Pedro")
        self.assertNotIn("email", resposta.json["data"])
