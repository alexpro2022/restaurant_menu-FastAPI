"""First migration

Revision ID: 31438175f0bd
Revises:
Create Date: 2023-08-02 22:01:54.818151

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '31438175f0bd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('menu',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=256), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_menu'))
                    )
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_menu_title'), ['title'], unique=True)

    op.create_table('submenu',
                    sa.Column('menu_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=256), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(['menu_id'], ['menu.id'], name=op.f('fk_submenu_menu_id_menu')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_submenu'))
                    )
    with op.batch_alter_table('submenu', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_submenu_title'), ['title'], unique=True)

    op.create_table('dish',
                    sa.Column('price', sa.Float(), nullable=False),
                    sa.Column('submenu_id', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=256), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(['submenu_id'], ['submenu.id'], name=op.f('fk_dish_submenu_id_submenu')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_dish'))
                    )
    with op.batch_alter_table('dish', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_dish_title'), ['title'], unique=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dish', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_dish_title'))

    op.drop_table('dish')
    with op.batch_alter_table('submenu', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_submenu_title'))

    op.drop_table('submenu')
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_menu_title'))

    op.drop_table('menu')
    # ### end Alembic commands ###
