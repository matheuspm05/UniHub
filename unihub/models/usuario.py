from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from unihub.ext.db import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    __table_args__ = (
        db.CheckConstraint(
            "role in ('usuario', 'moderador', 'admin')",
            name="ck_usuarios_role_valido",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=True)
    curso = db.Column(db.String(120), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)
    cidade = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(30), default="usuario", nullable=False)
    selo = db.Column(db.String(80), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    topicos = db.relationship("ForumTopico", back_populates="autor", lazy=True)
    respostas = db.relationship("ForumResposta", back_populates="autor", lazy=True)
    eventos_criados = db.relationship("Evento", back_populates="organizador", lazy=True)
    moradias_anunciadas = db.relationship("Moradia", back_populates="anunciante", lazy=True)
    notificacoes = db.relationship("Notificacao", back_populates="usuario", lazy=True)
    agenda_eventos = db.relationship("AgendaEvento", back_populates="usuario", lazy=True)
    mensagens_enviadas = db.relationship(
        "Mensagem",
        foreign_keys="Mensagem.remetente_id",
        back_populates="remetente",
        lazy=True,
    )
    mensagens_recebidas = db.relationship(
        "Mensagem",
        foreign_keys="Mensagem.destinatario_id",
        back_populates="destinatario",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "curso": self.curso,
            "periodo": self.periodo,
            "cidade": self.cidade,
            "bio": self.bio,
            "role": self.role,
            "selo": self.selo,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

    @property
    def is_active(self):
        return self.ativo

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.email}>"
