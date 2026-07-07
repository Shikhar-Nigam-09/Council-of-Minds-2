import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.user_settings import UserSettings


class UserRepository:
    """Repository layer for User and UserSettings database interactions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email, loading settings relationship."""
        stmt = (
            select(User).where(User.email == email).options(selectinload(User.settings))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID | str) -> Optional[User]:
        """Fetch a user by UUID, loading settings relationship."""
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None
        stmt = (
            select(User).where(User.id == user_id).options(selectinload(User.settings))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """Create a new user and initialize default UserSettings."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            token_version=0,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()

        settings = UserSettings(user_id=user.id)
        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(user)

        return await self.get_by_id(user.id)

    async def increment_token_version(self, user: User) -> int:
        """Increment user's token_version to invalidate all existing tokens."""
        user.token_version += 1
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user.token_version

    async def update_password(self, user: User, hashed_password: str) -> int:
        """Update user password and increment token_version."""
        user.hashed_password = hashed_password
        user.token_version += 1
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user.token_version
