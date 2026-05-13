from tests.base import TesteBase


class TesteNotificacoes(TesteBase):
    def test_renderiza_notificacoes_reais_sem_demo(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/notificacoes", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("João respondeu seu tópico".encode(), resposta.data)
        self.assertIn(b"Novo evento publicado", resposta.data)
        self.assertNotIn(b"Voce foi mencionado por Mariana Santos", resposta.data)
