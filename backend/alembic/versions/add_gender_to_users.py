"""
Add gender field to users table.

Revision ID: add_gender_to_users
Revises: add_profile_fields_to_users
Create Date: 2025-04-21
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_gender_to_users'
down_revision = 'add_profile_fields_to_users'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('gender', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'gender')
