"""add hash

Revision ID: e5035c0b5549
Revises: 0156d395bcfb
Create Date: 2025-01-10 21:47:09.084172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'e5035c0b5549'
down_revision: Union[str, None] = '0156d395bcfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usermodel', sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('usermodel', 'password_hash')
    # ### end Alembic commands ###