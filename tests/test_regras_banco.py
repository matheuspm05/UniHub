from sqlalchemy.exc import IntegrityError

from tests.base import TesteBase
from unihub.ext.db import db
from unihub.models import ForumTopico, Usuario


class TesteRegrasBanco(TesteBase):
    def test_banco_rejeita_role_invalida(self):
        usuario = Usuario(
            nome="Usuario Invalido",
            email="invalido@uvv.br",
            curso="Ciencia da Computacao",
            periodo="1 periodo",
            cidade="Vila Velha",
            role="superuser",
        )
        usuario.definir_senha("senha123")

        db.session.add(usuario)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_banco_rejeita_status_de_topico_invalido(self):
        topico = ForumTopico(
            titulo="Topico invalido",
            descricao="Descricao valida",
            curso="Ciencia da Computacao",
            disciplina="Banco de Dados",
            categoria="Duvida",
            status="publicado",
            tipo="topico",
            autor_id=1,
        )

        db.session.add(topico)

        with self.assertRaises(IntegrityError):
            db.session.commit()
