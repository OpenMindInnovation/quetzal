"""workspace model

Revision ID: 0002
Revises: 0001
Create Date: 2019-01-03 15:46:20.390897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workspace',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('_state',
              sa.Enum('INITIALIZING', 'READY', 'SCANNING', 'UPDATING',
                      'COMMITTING', 'DELETING', 'INVALID', 'CONFLICT',
                      'DELETED', name='workspacestate'),
              nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('temporary', sa.Boolean(), nullable=False),
    sa.Column('data_url', sa.String(length=2048), nullable=True),
    sa.Column('fk_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fk_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'fk_user_id')
    )
    op.create_index('ix_workspace_name_user', 'workspace', ['name', 'fk_user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_workspace_name_user', table_name='workspace')
    op.drop_table('workspace')
    # ### end Alembic commands ###
