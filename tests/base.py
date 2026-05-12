import unittest

from app import create_app
from unihub.ext.db import db
from unihub.services.seed import seed_database


class TesteBase(unittest.TestCase):
    EMAILS_USUARIOS = {
        1: "lucas.almeida@uvv.br",
        2: "joao.pedro@uvv.br",
        3: "mariana.costa@uvv.br",
        4: "ana.beatriz@uvv.br",
        5: "rafael.souza@uvv.br",
    }
    SENHA_PADRAO = "senha123"

    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        self.contexto = self.app.app_context()
        self.contexto.push()
        db.drop_all()
        seed_database()
        self.cliente = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.contexto.pop()

    def login_usuario(self, usuario_id):
        return self.cliente.post(
            "/auth/login",
            json={
                "email": self.EMAILS_USUARIOS[usuario_id],
                "senha": self.SENHA_PADRAO,
            },
        )

    def logout_usuario(self):
        return self.cliente.post("/auth/logout")
