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

    def test_admin_lista_usuarios(self):
        self.login_usuario(5)
        resposta = self.cliente.get("/admin/usuarios")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 5)

    def test_admin_altera_role_usuario(self):
        self.login_usuario(5)
        resposta = self.cliente.patch(
            "/admin/usuarios/2/role",
            json={"role": "moderador"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["role"], "moderador")

    def test_admin_desativa_usuario(self):
        self.login_usuario(5)
        resposta = self.cliente.patch(
            "/admin/usuarios/2/desativar",
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(resposta.json["data"]["ativo"])

    def test_admin_renderiza_telas_de_forum(self):
        self.login_usuario(5)

        topicos = self.cliente.get("/admin/forum/topicos", headers={"Accept": "text/html"})
        respostas = self.cliente.get("/admin/forum/respostas", headers={"Accept": "text/html"})

        self.assertEqual(topicos.status_code, 200)
        self.assertIn(b"Gerenciar forum", topicos.data)
        self.assertIn(b"Gerenciar respostas", topicos.data)
        self.assertEqual(respostas.status_code, 200)
        self.assertIn(b"Gerenciar respostas", respostas.data)
        self.assertIn(b"Desativar", respostas.data)

    def test_admin_renderiza_tela_de_eventos(self):
        self.login_usuario(5)
        resposta = self.cliente.get("/admin/eventos", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Gerenciar eventos", resposta.data)
        self.assertIn(b"Criar evento", resposta.data)

    def test_admin_altera_status_de_topico_pelo_html(self):
        self.login_usuario(5)
        resposta = self.cliente.post(
            "/admin/forum/topicos/1/status",
            data={"status": "desativado"},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        detalhe = self.cliente.get("/forum/topicos/1")
        self.assertEqual(detalhe.json["data"]["status"], "desativado")

    def test_admin_restaura_resposta(self):
        self.login_usuario(5)
        self.cliente.patch("/admin/forum/respostas/1/desativar")
        resposta = self.cliente.patch("/admin/forum/respostas/1/restaurar")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["status"], "ativo")
