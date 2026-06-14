from datetime import date

import click

from unihub.ext.db import db
from unihub.models import (
    Evento,
    ForumResposta,
    ForumTopico,
    Moradia,
    Notificacao,
    Usuario,
)

SENHA_PADRAO = "senha123"


def _get_or_create(model, defaults=None, **filters):
    instance = model.query.filter_by(**filters).first()
    if instance:
        return instance, False

    params = {**filters, **(defaults or {})}
    instance = model(**params)
    db.session.add(instance)
    return instance, True


def seed_database():
    db.create_all()

    usuarios_data = [
        {
            "nome": "Lucas Almeida",
            "email": "lucas.almeida@uvv.br",
            "curso": "Ciencia da Computacao",
            "periodo": "3 periodo",
            "cidade": "Vila Velha",
            "instagram": "@lucasalmeida",
            "linkedin": "linkedin.com/in/lucasalmeida",
            "whatsapp": "(27) 99999-1001",
            "role": "usuario",
            "selo": "Aluno",
        },
        {
            "nome": "João Pedro",
            "email": "joao.pedro@uvv.br",
            "curso": "Ciencia da Computacao",
            "periodo": "3 periodo",
            "cidade": "Vila Velha",
            "instagram": "@joaopedro",
            "linkedin": "linkedin.com/in/joaopedro",
            "whatsapp": "(27) 99999-1002",
            "role": "usuario",
            "selo": "Aluno",
        },
        {
            "nome": "Mariana Costa",
            "email": "mariana.costa@uvv.br",
            "curso": "Engenharia de Software",
            "periodo": "5 periodo",
            "cidade": "Vila Velha",
            "instagram": "@maricosta",
            "linkedin": "linkedin.com/in/marianacosta",
            "whatsapp": "(27) 99999-1003",
            "role": "moderador",
            "selo": "Representante",
        },
        {
            "nome": "Ana Beatriz",
            "email": "ana.beatriz@uvv.br",
            "curso": "Administracao",
            "periodo": "2 periodo",
            "cidade": "Vitoria",
            "instagram": "@anabeatriz",
            "linkedin": "linkedin.com/in/anabeatriz",
            "whatsapp": "(27) 99999-1004",
            "role": "usuario",
            "selo": "Aluno",
        },
        {
            "nome": "Rafael Souza",
            "email": "rafael.souza@uvv.br",
            "curso": "Equipe UniHub",
            "periodo": "Conta administrativa",
            "cidade": "Plataforma UniHub",
            "bio": "Conta administrativa criada pelo proprietario da plataforma para moderacao e gestao geral do UniHub.",
            "instagram": None,
            "linkedin": None,
            "whatsapp": None,
            "role": "admin",
            "selo": "Admin",
        },
    ]

    usuarios = {}
    for item in usuarios_data:
        usuario, _ = _get_or_create(
            Usuario,
            email=item["email"],
            defaults={key: value for key, value in item.items() if key != "email"},
        )
        for key, value in item.items():
            if key != "email":
                setattr(usuario, key, value)
        if not usuario.senha_hash:
            usuario.definir_senha(SENHA_PADRAO)
        usuarios[item["nome"]] = usuario

    db.session.flush()

    topicos_data = [
        {
            "titulo": "Dúvida sobre algoritmo de ordenação",
            "descricao": "Estou comparando bubble sort, merge sort e quicksort. Quando faz sentido usar cada um?",
            "curso": "Ciencia da Computacao",
            "disciplina": "Estrutura de Dados",
            "categoria": "Duvida",
            "autor": "Lucas Almeida",
        },
        {
            "titulo": "Resumo para prova de Banco de Dados",
            "descricao": "Compartilhei um resumo com normalização, SQL e modelagem relacional.",
            "curso": "Ciencia da Computacao",
            "disciplina": "Banco de Dados",
            "categoria": "Material de estudo",
            "autor": "Mariana Costa",
        },
        {
            "titulo": "Grupo para Projeto Integrador",
            "descricao": "Procuro pessoas para formar grupo do Projeto Integrador deste semestre.",
            "curso": "Engenharia de Software",
            "disciplina": "Projeto Integrador",
            "categoria": "Grupo de trabalho",
            "autor": "João Pedro",
        },
        {
            "titulo": "Monitoria de Cálculo I nesta semana",
            "descricao": "A monitoria vai acontecer na quarta-feira, no bloco de exatas.",
            "curso": "Engenharia de Software",
            "disciplina": "Cálculo I",
            "categoria": "Monitoria",
            "tipo": "aviso",
            "aviso_oficial": True,
            "autor": "Mariana Costa",
        },
        {
            "titulo": "Vaga de estágio em desenvolvimento",
            "descricao": "Empresa parceira abriu vaga para backend Python e SQL.",
            "curso": "Analise e Desenvolvimento de Sistemas",
            "disciplina": "Carreira",
            "categoria": "Estagio",
            "autor": "Rafael Souza",
        },
    ]

    topicos = {}
    for item in topicos_data:
        autor = usuarios[item.pop("autor")]
        topico, _ = _get_or_create(
            ForumTopico,
            titulo=item["titulo"],
            defaults={**item, "autor_id": autor.id},
        )
        topicos[topico.titulo] = topico

    db.session.flush()

    respostas_data = [
        {
            "topico": "Dúvida sobre algoritmo de ordenação",
            "autor": "João Pedro",
            "conteudo": "Para trabalho acadêmico, compara complexidade e estabilidade. Merge sort costuma ser bom exemplo.",
        },
        {
            "topico": "Resumo para prova de Banco de Dados",
            "autor": "Lucas Almeida",
            "conteudo": "Valeu! A parte de normalização ajudou bastante.",
        },
        {
            "topico": "Grupo para Projeto Integrador",
            "autor": "Ana Beatriz",
            "conteudo": "Tenho interesse em participar se ainda tiver vaga.",
        },
    ]

    for item in respostas_data:
        _get_or_create(
            ForumResposta,
            topico_id=topicos[item["topico"]].id,
            autor_id=usuarios[item["autor"]].id,
            conteudo=item["conteudo"],
        )

    eventos_data = [
        {
            "titulo": "Palestra de Carreiras em Tecnologia",
            "descricao": "Conversa com profissionais sobre mercado, carreira e primeiras oportunidades.",
            "categoria": "Palestra",
            "data_evento": date(2026, 5, 20),
            "horario": "19:00",
            "local": "Auditório UVV",
            "organizador": "Mariana Costa",
        },
        {
            "titulo": "Workshop de Git e GitHub",
            "descricao": "Workshop prático para aprender fluxo básico com Git e GitHub.",
            "categoria": "Workshop",
            "data_evento": date(2026, 5, 24),
            "horario": "14:00",
            "local": "Laboratório de Informática",
            "organizador": "Rafael Souza",
        },
        {
            "titulo": "Festa da Atlética",
            "descricao": "Evento social organizado pela atlética.",
            "categoria": "Festa",
            "data_evento": date(2026, 6, 1),
            "horario": "22:00",
            "local": "Vila Velha",
            "organizador": "Mariana Costa",
        },
        {
            "titulo": "Monitoria de Banco de Dados",
            "descricao": "Revisão de SQL, joins e normalização.",
            "categoria": "Monitoria",
            "data_evento": date(2026, 5, 18),
            "horario": "17:00",
            "local": "Sala 204",
            "organizador": "Mariana Costa",
        },
    ]

    for item in eventos_data:
        organizador = usuarios[item.pop("organizador")]
        _get_or_create(
            Evento,
            titulo=item["titulo"],
            defaults={**item, "organizador_id": organizador.id},
        )

    moradias_data = [
        {
            "titulo": "República próxima à UVV",
            "descricao": "Casa compartilhada com estudantes, internet inclusa e ambiente tranquilo.",
            "bairro": "Boa Vista",
            "preco_mensal": 850.00,
            "numero_vagas": 2,
            "perto_uvv": True,
            "aceita_dividir_quarto": True,
            "contato_externo": "WhatsApp: (27) 99999-1111",
            "anunciante": "João Pedro",
        },
        {
            "titulo": "Quarto individual em Itapuã",
            "descricao": "Quarto mobiliado em apartamento perto de mercado e ônibus.",
            "bairro": "Itapuã",
            "preco_mensal": 1200.00,
            "numero_vagas": 1,
            "perto_uvv": False,
            "aceita_dividir_quarto": False,
            "contato_externo": "Instagram: @quartoitapua",
            "anunciante": "Ana Beatriz",
        },
        {
            "titulo": "Apartamento compartilhado em Vila Velha",
            "descricao": "Apartamento com duas vagas para estudantes, próximo à praia.",
            "bairro": "Praia da Costa",
            "preco_mensal": 1000.00,
            "numero_vagas": 2,
            "perto_uvv": False,
            "aceita_dividir_quarto": True,
            "contato_externo": "lucas.moradia@uvv.br",
            "anunciante": "Lucas Almeida",
        },
    ]

    for item in moradias_data:
        anunciante = usuarios[item.pop("anunciante")]
        _get_or_create(
            Moradia,
            titulo=item["titulo"],
            defaults={**item, "anunciante_id": anunciante.id},
        )

    notificacoes_data = [
        {
            "titulo": "João respondeu seu tópico",
            "mensagem": "João Pedro respondeu sua dúvida sobre algoritmo de ordenação.",
            "tipo": "forum",
            "link": "/forum/topicos/1",
        },
        {
            "titulo": "Novo evento publicado",
            "mensagem": "Workshop de Git e GitHub foi publicado.",
            "tipo": "evento",
            "link": "/eventos/2",
        },
    ]

    for item in notificacoes_data:
        _get_or_create(
            Notificacao,
            usuario_id=usuarios["Lucas Almeida"].id,
            titulo=item["titulo"],
            defaults=item,
        )

    db.session.commit()


def register_seed_command(app):
    @app.cli.command("seed")
    def seed_command():
        seed_database()
        click.echo("Banco populado com dados iniciais do UniHub.")
