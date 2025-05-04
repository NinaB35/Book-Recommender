"""create admin

Revision ID: 64d900eb3b1c
Revises: 626885e2e14c
Create Date: 2025-05-04 15:34:19.997625

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import table, column, Integer, String, Boolean, text

from app.environment import settings
from app.security import get_password_hash

# revision identifiers, used by Alembic.
revision: str = '64d900eb3b1c'
down_revision: Union[str, None] = '626885e2e14c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()

    user_table = table(
        'user',
        column('id', Integer),
        column('username', String),
        column('email', String),
        column('hashed_password', String),
        column('is_admin', Boolean),
    )

    hashed_password = get_password_hash(settings.ADMIN_PASS)

    connection.execute(
        user_table.insert().values(
            username=settings.ADMIN_USER,
            email=settings.ADMIN_EMAIL,
            hashed_password=hashed_password,
            is_admin=True,
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    connection.execute(
        text("DELETE FROM user WHERE username = :username"),
        {"username": settings.ADMIN_USER}
    )
