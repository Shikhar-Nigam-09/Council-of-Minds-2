"""extend document status values to support deletion_failed

Revision ID: 0004_extend_document_status
Revises: 0003_create_document_chunks
Create Date: 2026-07-05 11:20:00.000000

"""

from typing import Sequence, Union

revision: str = "0004_extend_document_status"
down_revision: Union[str, None] = "0003_create_document_chunks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The status column is already VARCHAR(50), which accommodates 'deletion_failed'.
    # This migration formally records the schema readiness for Phase 3 status extensions.
    pass


def downgrade() -> None:
    pass
