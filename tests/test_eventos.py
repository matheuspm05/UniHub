from tests.base import TesteBase


class TesteEventos(TesteBase):
    def test_lista_eventos(self):
        resposta = self.cliente.get("/eventos")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 4)

    def test_renderiza_tela_de_eventos_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/eventos", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Eventos universitarios", resposta.data)
        self.assertIn(b"Salvar", resposta.data)
        self.assertIn(b"foto%20padrao%20evento.png", resposta.data)

    def test_renderiza_detalhes_de_evento_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/eventos/1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Voltar para eventos", resposta.data)
        self.assertIn(b"Resumo do evento", resposta.data)
        self.assertIn(b"Salvar na agenda", resposta.data)

    def test_renderiza_agenda_depois_de_salvar_evento(self):
        self.login_usuario(1)
        self.cliente.post("/eventos/1/salvar")
        resposta = self.cliente.get("/agenda", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Minha agenda", resposta.data)
        self.assertIn(b"Remover da agenda", resposta.data)
        self.assertIn(b"Esta semana", resposta.data)

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

    def test_moderador_cria_evento(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/eventos",
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

    def test_moderador_acessa_telas_de_gestao_de_eventos(self):
        self.login_usuario(3)

        criar = self.cliente.get("/eventos/criar", headers={"Accept": "text/html"})
        meus_eventos = self.cliente.get("/eventos/meus-eventos", headers={"Accept": "text/html"})
        editar = self.cliente.get("/eventos/1/editar", headers={"Accept": "text/html"})
        detalhes = self.cliente.get("/eventos/1", headers={"Accept": "text/html"})

        self.assertEqual(criar.status_code, 200)
        self.assertIn(b"Criar evento", criar.data)
        self.assertEqual(meus_eventos.status_code, 200)
        self.assertIn(b"Meus eventos", meus_eventos.data)
        self.assertEqual(editar.status_code, 200)
        self.assertIn(b"Editar evento", editar.data)
        self.assertEqual(detalhes.status_code, 200)
        self.assertIn(b"Editar evento", detalhes.data)

    def test_usuario_comum_nao_acessa_tela_criar_evento(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/eventos/criar", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 403)

    def test_moderador_cria_evento_pelo_formulario(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/eventos/criar",
            data={
                "titulo": "Semana de Dados",
                "descricao": "Evento sobre dados e carreira.",
                "categoria": "Workshop",
                "data_evento": "2026-05-20",
                "horario": "19:00",
                "local": "Lab. de Informatica 2",
                "status": "ativo",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/eventos/", resposta.headers["Location"])

    def test_moderador_edita_evento_pelo_formulario(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/eventos/1/editar",
            data={
                "titulo": "Workshop: Git e GitHub atualizado",
                "descricao": "Conteudo atualizado.",
                "categoria": "Workshop",
                "data_evento": "2026-05-20",
                "horario": "15:00",
                "local": "Lab. de Informatica 2",
                "status": "ativo",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/eventos/1", resposta.headers["Location"])

    def test_salva_evento_na_agenda(self):
        self.login_usuario(1)
        resposta = self.cliente.post("/eventos/1/salvar")

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["usuario_id"], 1)

    def test_nao_duplica_evento_na_agenda(self):
        self.login_usuario(1)
        self.cliente.post("/eventos/1/salvar")
        resposta = self.cliente.post("/eventos/1/salvar")

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("ja esta salvo", resposta.json["message"])
