from tests.base import TesteBase


class TesteUsuarios(TesteBase):
    def test_renderiza_lista_html_de_usuarios(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/usuarios", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Usuarios da comunidade", resposta.data)
        self.assertIn(b"Lucas Almeida", resposta.data)
        self.assertNotIn(b"Rafael Souza", resposta.data)

    def test_atualiza_usuario_logado_com_redes_sociais(self):
        self.login_usuario(1)
        resposta = self.cliente.patch(
            "/usuarios/me",
            json={
                "bio": "Estudante da UVV",
                "instagram": "@lucasdev",
                "linkedin": "linkedin.com/in/lucasdev",
                "whatsapp": "(27) 99999-0000",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["bio"], "Estudante da UVV")
        self.assertEqual(resposta.json["data"]["instagram"], "@lucasdev")
