"""adicionar contato externo em moradias

Revision ID: f2a6c4d8e901
Revises: b1f74d8c2a30
Create Date: 2026-06-10 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f2a6c4d8e901"
down_revision = "b1f74d8c2a30"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("moradias")}
    if "contato_externo" in columns:
        return

    with op.batch_alter_table("moradias") as batch_op:
        batch_op.add_column(sa.Column("contato_externo", sa.String(length=255), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("moradias")}
    if "contato_externo" not in columns:
        return

    with op.batch_alter_table("moradias") as batch_op:
        batch_op.drop_column("contato_externo")
