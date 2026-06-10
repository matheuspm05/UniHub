from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from unihub.ext.db import db

if TYPE_CHECKING:
    from unihub.models.usuario import Usuario


class ForumTopico(db.Model):
    __tablename__ = "forum_topicos"
    __table_args__ = (
        db.CheckConstraint(
            "status in ('aberto', 'resolvido', 'fechado', 'desativado')",
            name="ck_forum_topicos_status_valido",
        ),
        db.CheckConstraint(
            "tipo in ('topico', 'aviso')",
            name="ck_forum_topicos_tipo_valido",
        ),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(180), nullable=False)
    descricao: Mapped[str] = mapped_column(db.Text, nullable=False)
    curso: Mapped[str] = mapped_column(db.String(120), nullable=False)
    disciplina: Mapped[str | None] = mapped_column(db.String(120))
    categoria: Mapped[str] = mapped_column(db.String(80), nullable=False)
    status: Mapped[str] = mapped_column(db.String(30), default="aberto", nullable=False)
    tipo: Mapped[str] = mapped_column(db.String(30), default="topico", nullable=False)
    aviso_oficial: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    autor_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    visualizacoes: Mapped[int] = mapped_column(db.Integer, default=0, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    autor: Mapped["Usuario"] = relationship("Usuario", back_populates="topicos")
    respostas: Mapped[list["ForumResposta"]] = relationship(
        "ForumResposta",
        back_populates="topico",
        lazy=True,
    )

    def to_dict(self, include_respostas=False):
        data = {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "curso": self.curso,
            "disciplina": self.disciplina,
            "categoria": self.categoria,
            "status": self.status,
            "tipo": self.tipo,
            "aviso_oficial": self.aviso_oficial,
            "autor_id": self.autor_id,
            "autor": self.autor.to_public_dict() if self.autor else None,
            "visualizacoes": self.visualizacoes,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

        if include_respostas:
            data["respostas"] = [
                resposta.to_dict()
                for resposta in self.respostas
                if resposta.status != "desativado"
            ]

        return data


class ForumResposta(db.Model):
    __tablename__ = "forum_respostas"
    __table_args__ = (
        db.CheckConstraint(
            "status in ('ativo', 'editado', 'desativado')",
            name="ck_forum_respostas_status_valido",
        ),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    conteudo: Mapped[str] = mapped_column(db.Text, nullable=False)
    topico_id: Mapped[int] = mapped_column(db.ForeignKey("forum_topicos.id"), nullable=False)
    autor_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    status: Mapped[str] = mapped_column(db.String(30), default="ativo", nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    topico: Mapped["ForumTopico"] = relationship("ForumTopico", back_populates="respostas")
    autor: Mapped["Usuario"] = relationship("Usuario", back_populates="respostas")

    def to_dict(self):
        return {
            "id": self.id,
            "conteudo": self.conteudo,
            "topico_id": self.topico_id,
            "autor_id": self.autor_id,
            "autor": self.autor.to_public_dict() if self.autor else None,
            "status": self.status,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
