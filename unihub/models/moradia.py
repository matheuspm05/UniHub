from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from unihub.ext.db import db

if TYPE_CHECKING:
    from unihub.models.usuario import Usuario


class Moradia(db.Model):
    __tablename__ = "moradias"
    __table_args__ = (
        db.CheckConstraint(
            "status in ('disponivel', 'pausado', 'preenchido', 'desativado')",
            name="ck_moradias_status_valido",
        ),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(db.String(180), nullable=False)
    descricao: Mapped[str] = mapped_column(db.Text, nullable=False)
    bairro: Mapped[str] = mapped_column(db.String(120), nullable=False)
    preco_mensal: Mapped[Decimal] = mapped_column(db.Numeric(10, 2), nullable=False)
    numero_vagas: Mapped[int] = mapped_column(db.Integer, nullable=False)
    perto_uvv: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    aceita_dividir_quarto: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(db.String(30), default="disponivel", nullable=False)
    imagem_url: Mapped[str | None] = mapped_column(db.String(255))
    anunciante_id: Mapped[int] = mapped_column(db.ForeignKey("usuarios.id"), nullable=False)
    visualizacoes: Mapped[int] = mapped_column(db.Integer, default=0, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    anunciante: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="moradias_anunciadas",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "bairro": self.bairro,
            "preco_mensal": float(self.preco_mensal),
            "numero_vagas": self.numero_vagas,
            "perto_uvv": self.perto_uvv,
            "aceita_dividir_quarto": self.aceita_dividir_quarto,
            "status": self.status,
            "imagem_url": self.imagem_url,
            "anunciante_id": self.anunciante_id,
            "anunciante": self.anunciante.to_public_dict() if self.anunciante else None,
            "visualizacoes": self.visualizacoes,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
