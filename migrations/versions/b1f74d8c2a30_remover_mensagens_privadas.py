"""remover mensagens privadas

Revision ID: b1f74d8c2a30
Revises: c3f2a8d9b4e1
Create Date: 2026-06-10 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b1f74d8c2a30"
down_revision = "c3f2a8d9b4e1"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tabelas = set(inspector.get_table_names())

    if "notificacoes" in tabelas:
        op.execute(
            sa.text(
                "DELETE FROM notificacoes WHERE tipo = 'mensagem' OR link LIKE '/mensagens/%'"
            )
        )

    if "mensagens" in tabelas:
        op.drop_table("mensagens")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "mensagens" in tabelas:
        return

    op.create_table(
        "mensagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("remetente_id", sa.Integer(), nullable=False),
        sa.Column("destinatario_id", sa.Integer(), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("lida", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("removida_pelo_remetente", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("removida_pelo_destinatario", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["destinatario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["remetente_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
