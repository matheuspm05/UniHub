from tests.base import TesteBase


class TesteMain(TesteBase):
    def test_index_renderiza_landing_page(self):
        resposta = self.cliente.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Menos grupo", resposta.data)
        self.assertIn(b"Comecar agora", resposta.data)

    def test_health_responde_ok(self):
        resposta = self.cliente.get("/health")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["status"], "ok")
