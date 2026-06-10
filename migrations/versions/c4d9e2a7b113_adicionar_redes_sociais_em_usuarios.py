"""adicionar redes sociais em usuarios

Revision ID: c4d9e2a7b113
Revises: f2a6c4d8e901
Create Date: 2026-06-10 02:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4d9e2a7b113"
down_revision = "f2a6c4d8e901"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(sa.Column("instagram", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("linkedin", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("whatsapp", sa.String(length=160), nullable=True))


def downgrade():
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("whatsapp")
        batch_op.drop_column("linkedin")
        batch_op.drop_column("instagram")
