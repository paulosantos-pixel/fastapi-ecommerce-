"""agregar pedidos e items_pedido

Revision ID: 2cce941214ae
Revises: 
Create Date: 2026-09-14 11:37:10.994695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2cce941214ae'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('pedidos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('estado', sa.String(), nullable=True),
        sa.Column('total', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pedidos_id'), 'pedidos', ['id'], unique=False)
    
    op.create_table('items_pedido',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pedido_id', sa.Integer(), nullable=True),
        sa.Column('producto_id', sa.Integer(), nullable=True),
        sa.Column('cantidad', sa.Integer(), nullable=True),
        sa.Column('precio_unitario', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id'], ),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_pedido_id'), 'items_pedido', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_items_pedido_id'), table_name='items_pedido')
    op.drop_table('items_pedido')
    op.drop_index(op.f('ix_pedidos_id'), table_name='pedidos')
    op.drop_table('pedidos')
