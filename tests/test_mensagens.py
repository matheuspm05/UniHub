from tests.base import TesteBase
from unihub.ext.db import db
from unihub.models import Mensagem


class TesteMensagens(TesteBase):
    def test_usuario_lista_suas_conversas(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/mensagens")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 2)

    def test_renderiza_tela_de_mensagens(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/mensagens", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Mensagens", resposta.data)
        self.assertIn(b"Nova mensagem", resposta.data)
        self.assertIn(b"Digite sua mensagem", resposta.data)

    def test_renderiza_conversa_com_usuario(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/mensagens/3", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Mariana Costa", resposta.data)
        self.assertIn(b"Sobre", resposta.data)

    def test_envia_mensagem_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/mensagens",
            data={"destinatario_id": "3", "conteudo": "Mensagem pelo formulario."},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/mensagens/3", resposta.headers["Location"])

    def test_renderiza_formulario_de_nova_mensagem(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/mensagens?nova=1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Destinatario", resposta.data)
        self.assertIn(b"Enviar", resposta.data)

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

    def test_excluir_mensagem_remove_apenas_para_usuario_atual(self):
        self.login_usuario(1)
        resposta = self.cliente.delete("/mensagens/1")
        mensagem = db.session.get(Mensagem, 1)

        self.assertEqual(resposta.status_code, 200)
        self.assertIsNotNone(mensagem)
        self.assertTrue(mensagem.removida_pelo_destinatario)
        self.assertFalse(mensagem.removida_pelo_remetente)

        conversa_lucas = self.cliente.get("/mensagens/3")
        self.assertNotIn("Lucas, confirma", str(conversa_lucas.json["data"]))

        self.logout_usuario()
        self.login_usuario(3)
        conversa_mariana = self.cliente.get("/mensagens/1")
        self.assertIn("Lucas, confirma", str(conversa_mariana.json["data"]))
