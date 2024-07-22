from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

from .schemas import UserRole

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True, index=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)

    @property
    def is_superadmin(self) -> bool:
        return self.role == UserRole.ROLE_SUPERADMIN

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ROLE_ADMIN

    def enrich_admin_role_by_admin_role(self):
        if not self.is_admin:
            self.role = UserRole.ROLE_ADMIN

    def remove_admin_privileges_from_model(self):
        if self.is_admin:
            self.role = UserRole.ROLE_USER



