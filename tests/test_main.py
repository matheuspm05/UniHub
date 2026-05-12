from tests.base import TesteBase


class TesteMain(TesteBase):
    def test_index_renderiza_landing_page(self):
        resposta = self.cliente.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Centralize sua vida universitaria", resposta.data)

    def test_api_responde_com_api_funcionando(self):
        resposta = self.cliente.get("/api")

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.json["success"])
        self.assertEqual(resposta.json["data"]["message"], "API UniHub funcionando")

    def test_health_responde_ok(self):
        resposta = self.cliente.get("/health")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["status"], "ok")

    def test_swagger_json_lista_rotas(self):
        resposta = self.cliente.get("/swagger.json")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("/forum/topicos", resposta.json["paths"])
