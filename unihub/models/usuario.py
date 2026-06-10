from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from unihub.ext.db import db

if TYPE_CHECKING:
    from unihub.models.evento import AgendaEvento, Evento
    from unihub.models.forum import ForumResposta, ForumTopico
    from unihub.models.moradia import Moradia
    from unihub.models.notificacao import Notificacao


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    __table_args__ = (
        db.CheckConstraint(
            "role in ('usuario', 'moderador', 'admin')",
            name="ck_usuarios_role_valido",
        ),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(120), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    senha_hash: Mapped[str | None] = mapped_column(db.String(255))
    curso: Mapped[str] = mapped_column(db.String(120), nullable=False)
    periodo: Mapped[str] = mapped_column(db.String(50), nullable=False)
    cidade: Mapped[str] = mapped_column(db.String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(db.Text)
    instagram: Mapped[str | None] = mapped_column(db.String(160))
    linkedin: Mapped[str | None] = mapped_column(db.String(160))
    whatsapp: Mapped[str | None] = mapped_column(db.String(160))
    role: Mapped[str] = mapped_column(db.String(30), default="usuario", nullable=False)
    selo: Mapped[str | None] = mapped_column(db.String(80))
    ativo: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    topicos: Mapped[list["ForumTopico"]] = relationship(
        "ForumTopico",
        back_populates="autor",
        lazy=True,
    )
    respostas: Mapped[list["ForumResposta"]] = relationship(
        "ForumResposta",
        back_populates="autor",
        lazy=True,
    )
    eventos_criados: Mapped[list["Evento"]] = relationship(
        "Evento",
        back_populates="organizador",
        lazy=True,
    )
    moradias_anunciadas: Mapped[list["Moradia"]] = relationship(
        "Moradia",
        back_populates="anunciante",
        lazy=True,
    )
    notificacoes: Mapped[list["Notificacao"]] = relationship(
        "Notificacao",
        back_populates="usuario",
        lazy=True,
    )
    agenda_eventos: Mapped[list["AgendaEvento"]] = relationship(
        "AgendaEvento",
        back_populates="usuario",
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
            "instagram": self.instagram,
            "linkedin": self.linkedin,
            "whatsapp": self.whatsapp,
            "role": self.role,
            "selo": self.selo,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

    def to_public_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "curso": self.curso,
            "periodo": self.periodo,
            "cidade": self.cidade,
            "bio": self.bio,
            "instagram": self.instagram,
            "linkedin": self.linkedin,
            "whatsapp": self.whatsapp,
            "role": self.role,
            "selo": self.selo,
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
