import string
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models import URL
from datetime import datetime, timedelta, timezone

BASE62 = string.digits + string.ascii_letters

def encode_id_base62(num: int) -> str:
    if num == 0:
        return BASE62[0]
    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(BASE62[rem])
    return ''.join(reversed(base62))

async def create_short_url(
    db: AsyncSession,
    long_url: str,
    custom_alias: str = None,
    expiry_days: int = None
) -> str:
    if custom_alias:
        result = await db.execute(select(URL).where(URL.short_code == custom_alias))
        if result.scalars().first():
            raise ValueError("Custom alias already exists")
        short_code = custom_alias
    else:
        url_obj = URL(long_url=long_url)
        if expiry_days:
            url_obj.expiry_date = datetime.now(timezone.utc) + timedelta(days=expiry_days)
        db.add(url_obj)
        await db.commit()
        await db.refresh(url_obj)
        short_code = encode_id_base62(url_obj.id)
        url_obj.short_code = short_code
        await db.commit()
        await db.refresh(url_obj)
    return short_code

async def resolve_short_code(db: AsyncSession, short_code: str) -> str:
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    record = result.scalars().first()
    if not record:
        return None
    if record.expiry_date:
        expiry = record.expiry_date.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            return None
    return record.long_url