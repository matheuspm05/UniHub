from tests.base import TesteBase


class TesteMensagens(TesteBase):
    def test_usuario_lista_suas_conversas(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/mensagens")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 2)

    def test_destinatario_marca_mensagem_como_lida(self):
        self.login_usuario(1)
        resposta = self.cliente.patch("/mensagens/1/ler")

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.json["data"]["lida"])

    def test_usuario_nao_pode_marcar_mensagem_de_terceiro_como_lida(self):
        self.login_usuario(4)
        resposta = self.cliente.patch("/mensagens/1/ler")

        self.assertEqual(resposta.status_code, 403)

    def test_usuario_nao_pode_excluir_mensagem_de_terceiro(self):
        self.login_usuario(4)
        resposta = self.cliente.delete("/mensagens/1")

        self.assertEqual(resposta.status_code, 403)
