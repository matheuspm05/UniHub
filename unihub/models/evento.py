from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from unihub.ext.db import db

if TYPE_CHECKING:
    from unihub.models.usuario import Usuario


class Evento(db.Model):
    __tablename__ = "eventos"
    __table_args__ = (
        db.CheckConstraint(
            "status in ('ativo', 'cancelado', 'encerrado', 'desativado')",
            name="ck_eventos_status_valido",
        ),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(180), nullable=False)
    descricao: Mapped[str] = mapped_column(db.Text, nullable=False)
    categoria: Mapped[str] = mapped_column(db.String(80), nullable=False)
    data_evento: Mapped[date] = mapped_column(db.Date, nullable=False)
    horario: Mapped[str | None] = mapped_column(db.String(20))
    local: Mapped[str] = mapped_column(db.String(180), nullable=False)
    status: Mapped[str] = mapped_column(db.String(30), default="ativo", nullable=False)
    banner_url: Mapped[str | None] = mapped_column(db.String(255))
    organizador_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    visualizacoes: Mapped[int] = mapped_column(db.Integer, default=0, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    organizador: Mapped["Usuario"] = relationship("Usuario", back_populates="eventos_criados")
    agenda_salvos: Mapped[list["AgendaEvento"]] = relationship(
        "AgendaEvento",
        back_populates="evento",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "data_evento": self.data_evento.isoformat() if self.data_evento else None,
            "horario": self.horario,
            "local": self.local,
            "status": self.status,
            "banner_url": self.banner_url,
            "organizador_id": self.organizador_id,
            "organizador": self.organizador.to_public_dict() if self.organizador else None,
            "visualizacoes": self.visualizacoes,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }


class AgendaEvento(db.Model):
    __tablename__ = "agenda_eventos"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "evento_id", name="uq_agenda_usuario_evento"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    evento_id: Mapped[int] = mapped_column(db.ForeignKey("eventos.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="agenda_eventos")
    evento: Mapped["Evento"] = relationship("Evento", back_populates="agenda_salvos")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "evento_id": self.evento_id,
            "evento": self.evento.to_dict() if self.evento else None,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
