from datetime import datetime

from unihub.ext.db import db


class Mensagem(db.Model):
    __tablename__ = "mensagens"

    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False, nullable=False)
    removida_pelo_remetente = db.Column(db.Boolean, default=False, nullable=False)
    removida_pelo_destinatario = db.Column(db.Boolean, default=False, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    remetente = db.relationship(
        "Usuario",
        foreign_keys=[remetente_id],
        back_populates="mensagens_enviadas",
    )
    destinatario = db.relationship(
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
