from abc import ABCMeta, abstractmethod
from typing import Union, Optional

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import UserDTO
from .schemas import UserRole


class AbstractUserDAL(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, db_session):
        pass

    @abstractmethod
    def create_user(
            self,
            username,
            # name,
            # surname,
            email,
            hashed_password,
            roles,
    ) -> UserDTO:
        pass

    @abstractmethod
    def delete_user(self, user_id) -> Optional[int]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id) -> Optional[UserDTO]:
        pass

    @abstractmethod
    def get_user_by_email(self, email) -> Optional[UserDTO]:
        pass

    @abstractmethod
    def update_user(self, user_id, kwargs) -> Optional[UserDTO]:
        pass


class SQLAlchemyUserDAL(AbstractUserDAL):
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self,
            username: str,
            # name: str,
            # surname: str,
            email: str,
            hashed_password: str,
            role: UserRole,
    ) -> UserDTO:
        new_user = User(
            username=username,
            # name=name,
            # surname=surname,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return UserDTO.model_validate(new_user)

    async def delete_user(self, user_id: int) -> Optional[int]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return UserDTO.model_validate(user_row[0])

    async def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return UserDTO.model_validate(user_row[0])

    async def update_user(self, user_id: int, **kwargs) -> Union[int, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return UserDTO.model_validate(update_user_id_row[0])
