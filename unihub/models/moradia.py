from datetime import datetime

from unihub.ext.db import db


class Moradia(db.Model):
    __tablename__ = "moradias"
    __table_args__ = (
        db.CheckConstraint(
            "status in ('disponivel', 'pausado', 'preenchido', 'desativado')",
            name="ck_moradias_status_valido",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(180), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    bairro = db.Column(db.String(120), nullable=False)
    preco_mensal = db.Column(db.Numeric(10, 2), nullable=False)
    numero_vagas = db.Column(db.Integer, nullable=False)
    perto_uvv = db.Column(db.Boolean, default=False, nullable=False)
    aceita_dividir_quarto = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(30), default="disponivel", nullable=False)
    imagem_url = db.Column(db.String(255), nullable=True)
    anunciante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    visualizacoes = db.Column(db.Integer, default=0, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    anunciante = db.relationship("Usuario", back_populates="moradias_anunciadas")

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
