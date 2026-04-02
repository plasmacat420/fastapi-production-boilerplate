import uuid
import uuid as uuid_module

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator

from app.models.base import Base, TimestampMixin


class UUIDType(TypeDecorator):
    """Platform-independent UUID type. Uses PostgreSQL's UUID natively,
    and CHAR(32) with SQLite for testing."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid_module.UUID):
            return uuid_module.UUID(value).hex
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid_module.UUID):
            return uuid_module.UUID(value)
        return value


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
