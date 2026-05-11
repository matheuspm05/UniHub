from tests.base import TesteBase


class TesteUsuarios(TesteBase):
    def test_lista_usuarios(self):
        resposta = self.cliente.get("/usuarios")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 5)

    def test_retorna_usuario_mockado(self):
        resposta = self.cliente.get("/usuarios/me")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["nome"], "Lucas Almeida")

    def test_atualiza_usuario_mockado(self):
        resposta = self.cliente.patch("/usuarios/me", json={"bio": "Estudante da UVV"})

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["bio"], "Estudante da UVV")
