from tests.base import TesteBase


class TesteRoles(TesteBase):
    def test_usuario_comum_nao_acessa_admin(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/admin/dashboard")

        self.assertEqual(resposta.status_code, 403)

    def test_admin_acessa_dashboard(self):
        self.login_usuario(5)
        resposta = self.cliente.get("/admin/dashboard")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("total_usuarios", resposta.json["data"])

    def test_admin_altera_role_usuario(self):
        self.login_usuario(5)
        resposta = self.cliente.patch(
            "/admin/usuarios/2/role",
            json={"role": "moderador"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["role"], "moderador")
    def test_admin_renderiza_tela_de_forum_respostas(self):
        self.login_usuario(5)
        resposta = self.cliente.get("/admin/forum/respostas", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Gerenciar respostas", resposta.data)
