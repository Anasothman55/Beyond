"""add relation ship

Revision ID: 4c11e7cd1b70
Revises: 8e4ef23f7674
Create Date: 2025-01-14 19:47:51.332352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4c11e7cd1b70'
down_revision: Union[str, None] = '8e4ef23f7674'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookmodel', sa.Column('user_uid', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'bookmodel', 'usermodel', ['user_uid'], ['uid'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bookmodel', type_='foreignkey')
    op.drop_column('bookmodel', 'user_uid')
    # ### end Alembic commands ###
