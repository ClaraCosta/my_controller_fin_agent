"""add documents table

Revision ID: 0002_add_documents_table
Revises: 0001_initial_schema
Create Date: 2026-03-14 00:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_documents_table"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("document_type", sa.String(length=20), nullable=False),
        sa.Column("entry_mode", sa.String(length=20), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("json_nfe", sa.JSON(), nullable=True),
        sa.Column("json_rec", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_client_id", "documents", ["client_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_documents_client_id", table_name="documents")
    op.drop_table("documents")
