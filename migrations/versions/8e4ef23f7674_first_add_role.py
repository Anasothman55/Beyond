"""first add role

Revision ID: 8e4ef23f7674
Revises: e5035c0b5549
Create Date: 2025-01-13 14:45:06.051616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8e4ef23f7674'
down_revision: Union[str, None] = 'e5035c0b5549'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usermodel', sa.Column('role', sa.VARCHAR(), server_default='user', nullable=True))
    op.create_index(op.f('ix_usermodel_role'), 'usermodel', ['role'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_usermodel_role'), table_name='usermodel')
    op.drop_column('usermodel', 'role')
    # ### end Alembic commands ###
