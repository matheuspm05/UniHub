from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from unihub.ext.db import db

if TYPE_CHECKING:
    from unihub.models.usuario import Usuario


class Mensagem(db.Model):
    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    remetente_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    destinatario_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    conteudo: Mapped[str] = mapped_column(db.Text, nullable=False)
    lida: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    removida_pelo_remetente: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    removida_pelo_destinatario: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)

    remetente: Mapped["Usuario"] = relationship(
        "Usuario",
        foreign_keys=[remetente_id],
        back_populates="mensagens_enviadas",
    )
    destinatario: Mapped["Usuario"] = relationship(
        "Usuario",
        foreign_keys=[destinatario_id],
        back_populates="mensagens_recebidas",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "remetente_id": self.remetente_id,
            "remetente": self.remetente.to_public_dict() if self.remetente else None,
            "destinatario_id": self.destinatario_id,
            "destinatario": self.destinatario.to_public_dict() if self.destinatario else None,
            "conteudo": self.conteudo,
            "lida": self.lida,
            "removida_pelo_remetente": self.removida_pelo_remetente,
            "removida_pelo_destinatario": self.removida_pelo_destinatario,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
