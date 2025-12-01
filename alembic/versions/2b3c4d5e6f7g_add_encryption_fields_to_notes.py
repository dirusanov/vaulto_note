"""add encryption fields to notes

Revision ID: 2b3c4d5e6f7g
Revises: 1a2b3c4d5e6f
Create Date: 2025-11-25 15:08:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7g'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add encrypted_title column (nullable)
    op.add_column('notes', sa.Column('encrypted_title', sa.String(), nullable=True))
    
    # Add encrypted_content column with empty string default
    op.add_column('notes', sa.Column('encrypted_content', sa.Text(), server_default='', nullable=False))


def downgrade() -> None:
    # Remove encryption columns
    op.drop_column('notes', 'encrypted_content')
    op.drop_column('notes', 'encrypted_title')
