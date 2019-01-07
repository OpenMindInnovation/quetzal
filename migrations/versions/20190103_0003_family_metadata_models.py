"""family metadata models

Revision ID: 0003
Revises: 0002
Create Date: 2019-01-03 15:48:20.455473

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('fk_workspace_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('version IS NOT NULL OR fk_workspace_id IS NOT NULL', name='simul_null_check'),
    sa.ForeignKeyConstraint(['fk_workspace_id'], ['workspace.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'fk_workspace_id')
    )
    op.create_index(op.f('ix_family_name'), 'family', ['name'], unique=False)
    op.create_table('metadata',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_file', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('fk_family_id', sa.Integer(), nullable=False),
    sa.CheckConstraint("json ? 'id'", name='check_id'),
    sa.ForeignKeyConstraint(['fk_family_id'], ['family.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metadata_id_file'), 'metadata', ['id_file'], unique=False)
    op.add_column('workspace', sa.Column('fk_last_metadata_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'workspace', 'metadata', ['fk_last_metadata_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'workspace', type_='foreignkey')
    op.drop_column('workspace', 'fk_last_metadata_id')
    op.drop_index(op.f('ix_metadata_id_file'), table_name='metadata')
    op.drop_table('metadata')
    op.drop_index(op.f('ix_family_name'), table_name='family')
    op.drop_table('family')
    # ### end Alembic commands ###