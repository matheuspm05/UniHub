try:
    from flasgger import Swagger
except ImportError:
    Swagger = None


CORPOS_ESPERADOS = {
    ("POST", "/auth/login"): {
        "email": "lucas.almeida@uvv.br",
        "senha": "senha123",
        "lembrar": False,
    },
    ("POST", "/auth/cadastro"): {
        "nome": "Novo Aluno",
        "email": "novo.aluno@uvv.br",
        "senha": "senha123",
        "curso": "Ciencia da Computacao",
        "periodo": "1o periodo",
        "cidade": "Vila Velha",
    },
    ("PATCH", "/usuarios/me"): {
        "nome": "Lucas Almeida",
        "curso": "Ciencia da Computacao",
        "periodo": "3o periodo",
        "cidade": "Vila Velha",
        "bio": "Estudante da UVV",
        "selo": "calouro",
    },
    ("POST", "/forum/topicos"): {
        "titulo": "Duvida sobre algoritmo",
        "descricao": "Como funciona quicksort?",
        "curso": "Ciencia da Computacao",
        "disciplina": "Algoritmos",
        "categoria": "Duvida",
        "tipo": "topico",
        "aviso_oficial": False,
        "autor_id": 1,
    },
    ("PUT", "/forum/topicos/{topico_id}"): {
        "titulo": "Duvida atualizada",
        "descricao": "Descricao atualizada",
        "curso": "Ciencia da Computacao",
        "disciplina": "Algoritmos",
        "categoria": "Duvida",
        "status": "aberto",
    },
    ("POST", "/forum/topicos/{topico_id}/respostas"): {
        "conteudo": "Minha resposta para o topico.",
        "autor_id": 1,
    },
    ("PUT", "/forum/respostas/{resposta_id}"): {
        "conteudo": "Resposta editada.",
    },
    ("POST", "/eventos"): {
        "titulo": "Workshop de Git",
        "descricao": "Evento pratico para estudantes",
        "categoria": "Workshop",
        "data_evento": "2026-05-20",
        "horario": "19:00",
        "local": "UVV",
        "banner_url": None,
        "organizador_id": 1,
    },
    ("PUT", "/eventos/{evento_id}"): {
        "titulo": "Workshop de Git atualizado",
        "descricao": "Descricao atualizada",
        "categoria": "Workshop",
        "data_evento": "2026-05-20",
        "horario": "19:00",
        "local": "UVV",
        "banner_url": None,
    },
    ("POST", "/moradias"): {
        "titulo": "Republica perto da UVV",
        "descricao": "Quarto compartilhado",
        "bairro": "Praia da Costa",
        "preco_mensal": 900,
        "numero_vagas": 2,
        "perto_uvv": True,
        "aceita_dividir_quarto": True,
        "imagem_url": None,
        "anunciante_id": 1,
    },
    ("PUT", "/moradias/{moradia_id}"): {
        "titulo": "Republica atualizada",
        "descricao": "Descricao atualizada",
        "bairro": "Itapua",
        "preco_mensal": 1000,
        "numero_vagas": 1,
        "perto_uvv": True,
        "aceita_dividir_quarto": False,
    },
    ("POST", "/mensagens"): {
        "destinatario_id": 2,
        "conteudo": "Ola!",
    },
    ("PATCH", "/admin/usuarios/{usuario_id}/role"): {
        "role": "moderador",
    },
}


def _tipo_swagger(valor):
    if isinstance(valor, bool):
        return "boolean"
    if isinstance(valor, int):
        return "integer"
    if isinstance(valor, float):
        return "number"
    return "string"


def _schema_corpo(caminho, metodo):
    exemplo = CORPOS_ESPERADOS.get((metodo, caminho))
    if not exemplo:
        return {"type": "object"}

    propriedades = {
        chave: {"type": _tipo_swagger(valor)}
        for chave, valor in exemplo.items()
        if valor is not None
    }
    return {
        "type": "object",
        "properties": propriedades,
        "example": exemplo,
    }


def _formatar_caminho(rule):
    caminho = rule.rule
    for argumento in rule.arguments:
        conversor = rule._converters.get(argumento)
        nome_conversor = conversor.__class__.__name__.replace("Converter", "").lower() if conversor else ""
        tokens = [
            f"<{argumento}>",
            f"<int:{argumento}>",
            f"<string:{argumento}>",
            f"<float:{argumento}>",
            f"<path:{argumento}>",
            f"<uuid:{argumento}>",
        ]
        if nome_conversor:
            tokens.append(f"<{nome_conversor}:{argumento}>")

        for token in tokens:
            caminho = caminho.replace(token, f"{{{argumento}}}")
    return caminho


def _parametros_caminho(rule):
    parametros = []
    for argumento in sorted(rule.arguments):
        conversor = rule._converters.get(argumento)
        nome_conversor = conversor.__class__.__name__.lower() if conversor else ""
        tipo_parametro = "integer" if "integer" in nome_conversor else "string"
        parametros.append(
            {
                "name": argumento,
                "in": "path",
                "required": True,
                "type": tipo_parametro,
            }
        )
    return parametros


def _tag_da_rota(rule):
    if rule.rule == "/":
        return "main"
    return rule.rule.strip("/").split("/")[0]


def _operacao_da_rota(rule, metodo, caminho):
    parametros = _parametros_caminho(rule)
    if metodo.lower() in ["post", "put", "patch"]:
        parametros.append(
            {
                "name": "body",
                "in": "body",
                "required": False,
                "schema": _schema_corpo(caminho, metodo),
            }
        )

    return {
        "tags": [_tag_da_rota(rule)],
        "summary": rule.endpoint,
        "parameters": parametros,
        "responses": {
            "200": {"description": "Operacao realizada com sucesso"},
            "201": {"description": "Recurso criado com sucesso"},
            "403": {"description": "Permissao negada"},
            "400": {"description": "Dados invalidos"},
            "404": {"description": "Recurso nao encontrado"},
            "500": {"description": "Erro interno"},
        },
    }


def _montar_template(app):
    caminhos = {}
    prefixos_ignorados = ["/static/", "/flasgger_static/"]
    rotas_ignoradas = {"/swagger/", "/swagger.json", "/apidocs/index.html", "/oauth2-redirect.html"}

    for rule in app.url_map.iter_rules():
        if rule.rule in rotas_ignoradas or any(rule.rule.startswith(prefix) for prefix in prefixos_ignorados):
            continue

        caminho = _formatar_caminho(rule)
        caminhos.setdefault(caminho, {})

        for metodo in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            caminhos[caminho][metodo.lower()] = _operacao_da_rota(rule, metodo, caminho)

    return {
        "swagger": "2.0",
        "info": {
            "title": "UniHub API",
            "version": "0.1.0",
            "description": "Documentacao automatica inicial das rotas JSON do UniHub.",
        },
        "basePath": "/",
        "schemes": ["http"],
        "paths": caminhos,
    }


def init_app(app):
    app.config["SWAGGER"] = {
        "title": "UniHub API",
        "uiversion": 3,
    }
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/swagger.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger/",
    }

    if Swagger:
        Swagger(app, config=swagger_config, template=_montar_template(app))
