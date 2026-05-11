from datetime import datetime

from unihub.ext.db import db


class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(180), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    data_evento = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(20), nullable=True)
    local = db.Column(db.String(180), nullable=False)
    status = db.Column(db.String(30), default="ativo", nullable=False)
    banner_url = db.Column(db.String(255), nullable=True)
    organizador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    visualizacoes = db.Column(db.Integer, default=0, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    organizador = db.relationship("Usuario", back_populates="eventos_criados")
    agenda_salvos = db.relationship("AgendaEvento", back_populates="evento", lazy=True)

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
            "organizador": self.organizador.to_dict() if self.organizador else None,
            "visualizacoes": self.visualizacoes,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }


class AgendaEvento(db.Model):
    __tablename__ = "agenda_eventos"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "evento_id", name="uq_agenda_usuario_evento"),
    )

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship("Usuario", back_populates="agenda_eventos")
    evento = db.relationship("Evento", back_populates="agenda_salvos")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "evento_id": self.evento_id,
            "evento": self.evento.to_dict() if self.evento else None,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }
