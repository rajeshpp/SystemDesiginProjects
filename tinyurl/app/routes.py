from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, services
from app.db import AsyncSessionLocal

router = APIRouter()

def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/shorten", response_model=schemas.URLResponse)
async def shorten_url(
    payload: schemas.URLRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    custom: str = Query(default=None)
):
    try:
        short_code = await services.create_short_url(
            db,
            str(payload.url),
            custom_alias=custom,
            expiry_days=payload.expiry_days
        )
        return {"short_url": f"{request.base_url}{short_code}"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.get("/{short_code}")
async def get_long_url(short_code: str, db: AsyncSession = Depends(get_db)):
    long_url = await services.resolve_short_code(db, short_code)
    print(long_url)
    if not long_url:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    return {"long_url": long_url}

@router.get("/redirect/{short_code}")
async def redirect_to_url(short_code: str, db: AsyncSession = Depends(get_db)):
    long_url = await services.resolve_short_code(db, short_code)
    if not long_url:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    return RedirectResponse(url=long_url, status_code=302)