"""
Add phone, department, and bio fields to users table.

Revision ID: add_profile_fields_to_users
Revises: 11939a664949
Create Date: 2025-04-21
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_profile_fields_to_users'
down_revision = '11939a664949'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users', sa.Column('bio', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'bio')
    op.drop_column('users', 'department')
    op.drop_column('users', 'phone')
