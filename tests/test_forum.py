from tests.base import TesteBase


class TesteForum(TesteBase):
    def test_lista_topicos(self):
        resposta = self.cliente.get("/forum/topicos")

        self.assertEqual(resposta.status_code, 200)
        self.assertGreaterEqual(len(resposta.json["data"]), 5)

    def test_cria_topico_com_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Como estudar Flask?",
                "descricao": "Quero dicas para organizar o backend.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Desenvolvimento Web",
                "categoria": "Duvida",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["data"]["autor"]["id"], 1)

    def test_renderiza_forum_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Forum academico", resposta.data)
        self.assertIn(b"Novo topico", resposta.data)
        self.assertIn(b"Ver topico", resposta.data)

    def test_renderiza_criar_topico_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum/criar", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Criar topico", resposta.data)
        self.assertIn(b"Publicar topico", resposta.data)

    def test_usuario_cria_topico_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/criar",
            data={
                "titulo": "Duvida sobre testes",
                "descricao": "Como organizar testes do projeto?",
                "curso": "Ciencia da Computacao",
                "disciplina": "Desenvolvimento Web",
                "categoria": "Duvida",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/", resposta.headers["Location"])

    def test_renderiza_detalhes_do_topico_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum/topicos/1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Voltar para o forum", resposta.data)
        self.assertIn(b"Respostas", resposta.data)
        self.assertIn(b"Escreva sua resposta", resposta.data)

    def test_renderiza_acoes_de_resposta_do_proprio_usuario(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum/topicos/2", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Editar resposta", resposta.data)
        self.assertIn(b"Remover", resposta.data)

    def test_usuario_responde_topico_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos/1/respostas",
            data={"conteudo": "Resposta pelo formulario."},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/1", resposta.headers["Location"])

    def test_usuario_edita_resposta_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/respostas/2/editar",
            data={"conteudo": "Resposta editada pelo formulario."},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/2", resposta.headers["Location"])

    def test_usuario_remove_resposta_pelo_formulario(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/respostas/2/remover",
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/2", resposta.headers["Location"])

    def test_renderiza_meus_posts_para_usuario_logado(self):
        self.login_usuario(1)
        resposta = self.cliente.get("/forum/meus-posts", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Meus posts", resposta.data)
        self.assertIn(b"Meus topicos", resposta.data)
        self.assertIn(b"Minhas respostas", resposta.data)

    def test_renderiza_edicao_de_topico_para_autor(self):
        self.login_usuario(1)
        resposta = self.cliente.get(
            "/forum/topicos/1/editar",
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Editar topico", resposta.data)
        self.assertIn(b"Salvar alteracoes", resposta.data)

    def test_autor_edita_topico_pelo_formulario_sem_alterar_status(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos/1/editar",
            data={
                "titulo": "Duvida sobre algoritmo atualizada",
                "descricao": "Atualizando o texto do topico.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Estrutura de Dados",
                "categoria": "Duvida",
                "status": "fechado",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        detalhes = self.cliente.get("/forum/topicos/1")
        self.assertEqual(detalhes.json["data"]["status"], "aberto")
        self.assertEqual(detalhes.json["data"]["titulo"], "Duvida sobre algoritmo atualizada")

    def test_usuario_nao_edita_topico_de_outra_pessoa_pelo_html(self):
        self.login_usuario(2)
        resposta = self.cliente.get(
            "/forum/topicos/1/editar",
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 403)

    def test_usuario_comum_nao_cria_aviso(self):
        self.login_usuario(1)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Aviso teste",
                "descricao": "Aviso oficial",
                "curso": "Ciencia da Computacao",
                "disciplina": "Geral",
                "categoria": "Aviso",
                "tipo": "aviso",
            },
        )

        self.assertEqual(resposta.status_code, 403)

    def test_moderador_cria_aviso(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/forum/topicos",
            json={
                "titulo": "Aviso de monitoria",
                "descricao": "Monitoria extra nesta semana.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Calculo I",
                "categoria": "Aviso",
                "tipo": "aviso",
            },
        )

        self.assertEqual(resposta.status_code, 201)
        self.assertTrue(resposta.json["data"]["aviso_oficial"])

    def test_moderador_ve_identificacao_e_acoes_no_forum(self):
        self.login_usuario(3)
        resposta = self.cliente.get("/forum", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Moderador", resposta.data)
        self.assertIn(b"Criar aviso", resposta.data)
        self.assertIn(b"Avisos oficiais em destaque", resposta.data)

    def test_moderador_cria_aviso_pelo_formulario(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/forum/criar",
            data={
                "tipo": "aviso",
                "titulo": "Aviso de monitoria extra",
                "descricao": "Monitoria extra nesta semana.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Banco de Dados",
                "categoria": "Aviso",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/forum/topicos/", resposta.headers["Location"])

    def test_moderador_renderiza_detalhe_com_acoes_de_status(self):
        self.login_usuario(3)
        resposta = self.cliente.get("/forum/topicos/1", headers={"Accept": "text/html"})

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Marcar como resolvido", resposta.data)
        self.assertIn(b"Fechar topico", resposta.data)

    def test_moderador_edita_status_pelo_formulario(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/forum/topicos/1/editar",
            data={
                "tipo": "topico",
                "titulo": "Topico revisado pelo moderador",
                "descricao": "Descricao revisada.",
                "curso": "Ciencia da Computacao",
                "disciplina": "Estrutura de Dados",
                "categoria": "Duvida",
                "status": "resolvido",
            },
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        detalhes = self.cliente.get("/forum/topicos/1")
        self.assertEqual(detalhes.json["data"]["status"], "resolvido")

    def test_moderador_altera_status_por_acao_html(self):
        self.login_usuario(3)
        resposta = self.cliente.post(
            "/forum/topicos/1/status",
            data={"status": "fechado"},
            headers={"Accept": "text/html"},
        )

        self.assertEqual(resposta.status_code, 302)
        detalhes = self.cliente.get("/forum/topicos/1")
        self.assertEqual(detalhes.json["data"]["status"], "fechado")

    def test_nao_responde_topico_fechado(self):
        self.login_usuario(3)
        self.cliente.patch("/forum/topicos/1/fechar")
        self.logout_usuario()
        self.login_usuario(1)

        resposta = self.cliente.post(
            "/forum/topicos/1/respostas",
            json={"conteudo": "Tentando responder."},
        )

        self.assertEqual(resposta.status_code, 400)

    def test_usuario_comum_nao_promove_topico_para_aviso_oficial(self):
        self.login_usuario(1)
        resposta = self.cliente.put(
            "/forum/topicos/1",
            json={
                "tipo": "aviso",
                "status": "fechado",
                "aviso_oficial": True,
            },
        )

        self.assertEqual(resposta.status_code, 403)
