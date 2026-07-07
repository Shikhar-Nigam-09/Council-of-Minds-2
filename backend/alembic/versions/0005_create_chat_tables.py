"""create chat tables

Revision ID: 0005_create_chat_tables
Revises: 0004_extend_document_status
Create Date: 2026-07-05 15:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0005_create_chat_tables"
down_revision: Union[str, None] = "0004_extend_document_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create chats table
    op.create_table(
        "chats",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chats_id"), "chats", ["id"], unique=False)
    op.create_index(op.f("ix_chats_user_id"), "chats", ["user_id"], unique=False)

    # 2. Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chat_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="success"
        ),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("retrieval_quality", sa.Float(), nullable=True),
        sa.Column("evidence_coverage", sa.Float(), nullable=True),
        sa.Column("agent_agreement", sa.Float(), nullable=True),
        sa.Column("weights_used", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)
    op.create_index(op.f("ix_messages_chat_id"), "messages", ["chat_id"], unique=False)

    # 3. Create agent_responses table
    op.create_table(
        "agent_responses",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("message_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("key_points", sa.JSON(), nullable=False),
        sa.Column("self_reported_confidence", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_agent_responses_id"), "agent_responses", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_agent_responses_message_id"),
        "agent_responses",
        ["message_id"],
        unique=False,
    )

    # 4. Create message_evidence table
    op.create_table(
        "message_evidence",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("message_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chunk_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["chunk_id"], ["document_chunks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_message_evidence_id"), "message_evidence", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_message_evidence_message_id"),
        "message_evidence",
        ["message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_message_evidence_chunk_id"),
        "message_evidence",
        ["chunk_id"],
        unique=False,
    )


def downgrade() -> None:
    # 4. Drop message_evidence
    op.drop_index(op.f("ix_message_evidence_chunk_id"), table_name="message_evidence")
    op.drop_index(op.f("ix_message_evidence_message_id"), table_name="message_evidence")
    op.drop_index(op.f("ix_message_evidence_id"), table_name="message_evidence")
    op.drop_table("message_evidence")

    # 3. Drop agent_responses
    op.drop_index(op.f("ix_agent_responses_message_id"), table_name="agent_responses")
    op.drop_index(op.f("ix_agent_responses_id"), table_name="agent_responses")
    op.drop_table("agent_responses")

    # 2. Drop messages
    op.drop_index(op.f("ix_messages_chat_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")

    # 1. Drop chats
    op.drop_index(op.f("ix_chats_user_id"), table_name="chats")
    op.drop_index(op.f("ix_chats_id"), table_name="chats")
    op.drop_table("chats")
