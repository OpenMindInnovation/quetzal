"""family model

Revision ID: 0002
Revises: 0001
Create Date: 2019-01-02 18:34:11.922873

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
    op.create_table('family',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('fk_workspace_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fk_workspace_id'], ['workspace.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'fk_workspace_id')
    )
    op.create_index(op.f('ix_family_name'), 'family', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_family_name'), table_name='family')
    op.drop_table('family')
    # ### end Alembic commands ###
