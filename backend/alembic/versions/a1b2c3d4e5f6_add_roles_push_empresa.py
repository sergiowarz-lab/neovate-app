"""add roles analista/empresa, estado Procesando, nit_empresa usuario, push_subscription

Revision ID: a1b2c3d4e5f6
Revises: 575836567e28
Create Date: 2026-06-05 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "575836567e28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE requiere estar fuera de una transacción en PostgreSQL
    # Los valores deben coincidir con los NOMBRES de los miembros Python (en mayúsculas)
    # SQLAlchemy 2.x serializa los enums Python por su .name, no por su .value
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE rol_usuario ADD VALUE IF NOT EXISTS 'ANALISTA'")
        op.execute("ALTER TYPE rol_usuario ADD VALUE IF NOT EXISTS 'EMPRESA'")
        op.execute("ALTER TYPE estado_reporte ADD VALUE IF NOT EXISTS 'PROCESANDO'")

    # Columna nit_empresa en usuario (vincula rol=empresa a su empresa)
    op.add_column(
        "usuario",
        sa.Column(
            "nit_empresa",
            sa.CHAR(9),
            sa.ForeignKey("empresa_aliada.nit9"),
            nullable=True,
        ),
    )

    # Tabla de suscripciones push (Web Push / VAPID)
    op.create_table(
        "push_subscription",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("subscription_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["username"], ["usuario.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_push_subscription_username", "push_subscription", ["username"])


def downgrade() -> None:
    op.drop_index("ix_push_subscription_username", table_name="push_subscription")
    op.drop_table("push_subscription")
    op.drop_column("usuario", "nit_empresa")
    # No se pueden eliminar valores de enums en PostgreSQL sin recrearlos
