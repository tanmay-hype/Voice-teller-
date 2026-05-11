"""Add user profile fields and status

Revision ID: 9a7b2f1d8c44
Revises: add_location_verification
Create Date: 2026-05-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a7b2f1d8c44'
down_revision: Union[str, Sequence[str], None] = 'add_location_verification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('contact_no', sa.String(length=30), nullable=True))
    op.add_column('users', sa.Column('profile_picture_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('status', sa.String(length=20), nullable=False, server_default='active'))


def downgrade() -> None:
    op.drop_column('users', 'status')
    op.drop_column('users', 'profile_picture_url')
    op.drop_column('users', 'contact_no')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
