from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CarAd

@dataclass(frozen=True)
class CarAdDTO:
    url: str
    title: str
    price_usd: int
    odometer: int
    username: str
    phone_number: int | None
    image_url: str
    images_count: int
    car_number: str
    car_vin: str

async def insert_ignore(session: AsyncSession, ad: CarAdDTO) -> bool:
    stmt = (
        insert(CarAd)
        .values(**ad.__dict__)
        .on_conflict_do_nothing(index_elements=["url"])
        .returning(CarAd.id)
    )
    res = await session.execute(stmt)
    row = res.first()
    await session.commit()
    return row is not None
