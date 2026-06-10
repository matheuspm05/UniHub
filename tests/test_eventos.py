from tests.base import TesteBase


class TesteEventos(TesteBase):
    def test_renderiza_tela_de_eventos_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/eventos", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Eventos universitarios", resposta.data)
        self.assertIn(b"Salvar", resposta.data)
        self.assertIn(b"foto%20padrao%20evento.png", resposta.data)

    def test_renderiza_agenda_depois_de_salvar_evento(self):
        self.login_usuario(1)
        self.cliente.post("/eventos/1/salvar")
        resposta = self.cliente.get("/agenda", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Minha agenda", resposta.data)
        self.assertIn(b"Remover da agenda", resposta.data)
        self.assertIn("Maio 2026".encode(), resposta.data)

    def test_usuario_comum_nao_cria_evento(self):
        self.login_usuario(1)
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
