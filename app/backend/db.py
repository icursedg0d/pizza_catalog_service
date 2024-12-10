from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    "postgresql+asyncpg://pizza:UBkTbjvdYFNwWTH9HQZX9YAl5KzYIYIi@dpg-ctc2cld2ng1s73bt00j0-a.frankfurt-postgres.render.com/pizza_service_iwj8",
    echo=True,
)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
