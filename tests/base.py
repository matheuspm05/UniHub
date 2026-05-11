import unittest

from app import create_app
from unihub.ext.db import db
from unihub.services.seed import seed_database


class TesteBase(unittest.TestCase):
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

    def cabecalho_usuario(self, usuario_id):
        return {"X-Mock-User-Id": str(usuario_id)}
