from tests.base import TesteBase


class TesteEventos(TesteBase):
    def test_lista_eventos(self):
        resposta = self.cliente.get("/eventos")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 4)

    def test_usuario_comum_nao_cria_evento(self):
        resposta = self.cliente.post(
            "/eventos",
            json={
                "titulo": "Evento teste",
                "descricao": "Descricao",
                "categoria": "Workshop",
                "data_evento": "2026-05-20",
                "horario": "19:00",
                "local": "UVV",
            },
        )

        self.assertEqual(resposta.status_code, 403)

    def test_moderador_cria_evento(self):
        resposta = self.cliente.post(
            "/eventos",
            headers=self.cabecalho_usuario(3),
            json={
                "titulo": "Aulao de Python",
                "descricao": "Encontro pratico",
                "categoria": "Workshop",
                "data_evento": "2026-05-20",
                "horario": "19:00",
                "local": "UVV",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["organizador"]["id"], 3)

    def test_salva_evento_na_agenda(self):
        resposta = self.cliente.post("/eventos/1/salvar")

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["usuario_id"], 1)

    def test_nao_duplica_evento_na_agenda(self):
        self.cliente.post("/eventos/1/salvar")
        resposta = self.cliente.post("/eventos/1/salvar")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("ja esta salvo", resposta.json["message"])
