from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, DateTime, func, UniqueConstraint

class Base(DeclarativeBase):
    pass

class CarAd(Base):
    __tablename__ = "car_ads"
    __table_args__ = (UniqueConstraint("url", name="uq_car_ads_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    url: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    price_usd: Mapped[int] = mapped_column(Integer, nullable=False)
    odometer: Mapped[int] = mapped_column(Integer, nullable=False)

    username: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    image_url: Mapped[str] = mapped_column(String, nullable=False)
    images_count: Mapped[int] = mapped_column(Integer, nullable=False)

    car_number: Mapped[str] = mapped_column(String, nullable=False)
    car_vin: Mapped[str] = mapped_column(String, nullable=False)

    datetime_found: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
