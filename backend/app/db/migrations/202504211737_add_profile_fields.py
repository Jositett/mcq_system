"""
Add phone, department, and bio fields to users table
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('users', 'bio')
    op.drop_column('users', 'department')
    op.drop_column('users', 'phone')
