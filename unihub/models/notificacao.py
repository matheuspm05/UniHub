from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from unihub.ext.db import db

if TYPE_CHECKING:
    from unihub.models.usuario import Usuario


class Notificacao(db.Model):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(db.String(160), nullable=False)
    mensagem: Mapped[str] = mapped_column(db.Text, nullable=False)
    tipo: Mapped[str] = mapped_column(db.String(30), nullable=False)
    lida: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    link: Mapped[str | None] = mapped_column(db.String(255))
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="notificacoes")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "titulo": self.titulo,
            "mensagem": self.mensagem,
            "tipo": self.tipo,
            "lida": self.lida,
            "link": self.link,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
