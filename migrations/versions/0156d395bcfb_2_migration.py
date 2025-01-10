"""2  migration

Revision ID: 0156d395bcfb
Revises: 6ee2833b7ea8
Create Date: 2025-01-10 20:51:55.656317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0156d395bcfb'
down_revision: Union[str, None] = '6ee2833b7ea8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_usermodel_email'), 'usermodel', ['email'], unique=True)
    op.create_index(op.f('ix_usermodel_first_name'), 'usermodel', ['first_name'], unique=False)
    op.create_index(op.f('ix_usermodel_last_name'), 'usermodel', ['last_name'], unique=False)
    op.create_index(op.f('ix_usermodel_username'), 'usermodel', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_usermodel_username'), table_name='usermodel')
    op.drop_index(op.f('ix_usermodel_last_name'), table_name='usermodel')
    op.drop_index(op.f('ix_usermodel_first_name'), table_name='usermodel')
    op.drop_index(op.f('ix_usermodel_email'), table_name='usermodel')
    # ### end Alembic commands ###
