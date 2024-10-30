import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)


class UserModel(Base):
    __tablename__ = "users"
    user_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=settings.timezone), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=settings.timezone), onupdate=func.now(), nullable=True
    )


class PackageModel(Base):
    __tablename__ = "package"
    package_name: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    unic_id: Mapped[str] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("types.id"))
    cost_content: Mapped[float] = mapped_column(nullable=False)
    cost_shipping: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=settings.timezone), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=settings.timezone), onupdate=func.now(), nullable=True
    )


class TypeModel(Base):
    __tablename__ = "types"
    type_name: Mapped[str] = mapped_column(nullable=False)
