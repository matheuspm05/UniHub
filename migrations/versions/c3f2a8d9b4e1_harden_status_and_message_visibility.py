"""harden status fields and message visibility

Revision ID: c3f2a8d9b4e1
Revises: a460bfd3e910
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c3f2a8d9b4e1"
down_revision = "a460bfd3e910"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.create_check_constraint(
            "ck_usuarios_role_valido",
            "role in ('usuario', 'moderador', 'admin')",
        )

    with op.batch_alter_table("eventos") as batch_op:
        batch_op.create_check_constraint(
            "ck_eventos_status_valido",
            "status in ('ativo', 'cancelado', 'encerrado', 'desativado')",
        )

    with op.batch_alter_table("forum_topicos") as batch_op:
        batch_op.create_check_constraint(
            "ck_forum_topicos_status_valido",
            "status in ('aberto', 'resolvido', 'fechado', 'desativado')",
        )
        batch_op.create_check_constraint(
            "ck_forum_topicos_tipo_valido",
            "tipo in ('topico', 'aviso')",
        )

    with op.batch_alter_table("forum_respostas") as batch_op:
        batch_op.create_check_constraint(
            "ck_forum_respostas_status_valido",
            "status in ('ativo', 'editado', 'desativado')",
        )

    with op.batch_alter_table("moradias") as batch_op:
        batch_op.create_check_constraint(
            "ck_moradias_status_valido",
            "status in ('disponivel', 'pausado', 'preenchido', 'desativado')",
        )

    with op.batch_alter_table("mensagens") as batch_op:
        batch_op.add_column(
            sa.Column(
                "removida_pelo_remetente",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "removida_pelo_destinatario",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade():
    with op.batch_alter_table("mensagens") as batch_op:
        batch_op.drop_column("removida_pelo_destinatario")
        batch_op.drop_column("removida_pelo_remetente")

    with op.batch_alter_table("moradias") as batch_op:
        batch_op.drop_constraint("ck_moradias_status_valido", type_="check")

    with op.batch_alter_table("forum_respostas") as batch_op:
        batch_op.drop_constraint("ck_forum_respostas_status_valido", type_="check")

    with op.batch_alter_table("forum_topicos") as batch_op:
        batch_op.drop_constraint("ck_forum_topicos_tipo_valido", type_="check")
        batch_op.drop_constraint("ck_forum_topicos_status_valido", type_="check")

    with op.batch_alter_table("eventos") as batch_op:
        batch_op.drop_constraint("ck_eventos_status_valido", type_="check")

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_constraint("ck_usuarios_role_valido", type_="check")
