"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create request_type enum
    request_type_enum = postgresql.ENUM(
        "GDPR_DATA_REQUEST",
        name="requesttype",
        create_type=True,
    )
    request_type_enum.create(op.get_bind())

    # Create request_status enum
    request_status_enum = postgresql.ENUM(
        "PENDING",
        "IN_PROGRESS",
        "AWAITING_RESPONSE",
        "COMPLETED",
        "CANCELLED",
        name="requeststatus",
        create_type=True,
    )
    request_status_enum.create(op.get_bind())

    # Create clients table
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create requests table
    op.create_table(
        "requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column(
            "type",
            request_type_enum,
            nullable=False,
        ),
        sa.Column(
            "status",
            request_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("target_name", sa.String(255), nullable=False),
        sa.Column("target_email", sa.String(255), nullable=False),
        sa.Column("target_responsible_name", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_requests_client_id", "requests", ["client_id"])
    op.create_index("ix_requests_status", "requests", ["status"])

    # Create request_state_history table
    op.create_table(
        "request_state_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("request_state_data", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_request_state_history_request_id", "request_state_history", ["request_id"])

    # Create request_email_log table
    op.create_table(
        "request_email_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("is_outgoing", sa.Boolean(), nullable=False),
        sa.Column("email_subject", sa.String(500), nullable=False),
        sa.Column("email_body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_request_email_log_request_id", "request_email_log", ["request_id"])


def downgrade() -> None:
    op.drop_table("request_email_log")
    op.drop_table("request_state_history")
    op.drop_table("requests")
    op.drop_table("clients")

    op.execute("DROP TYPE requeststatus")
    op.execute("DROP TYPE requesttype")
