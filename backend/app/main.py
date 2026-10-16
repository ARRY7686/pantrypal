from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .db import Base, engine, get_db
from .schemas import ItemCreate, ItemOut, ItemUpdate, Location, Stats


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Containers run `alembic upgrade head` before Uvicorn starts; create_all is a no-op
    # there and keeps the SQLite test database self-contained.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(app, endpoint="/metrics")


def to_out(item: models.Item) -> ItemOut:
    out = ItemOut.model_validate(item)
    if item.expires_on is None:
        return out
    out.days_left = (item.expires_on - date.today()).days
    if out.days_left < 0:
        out.status = "expired"
    elif out.days_left <= settings.expiring_soon_days:
        out.status = "expiring"
    else:
        out.status = "fresh"
    return out


def get_item_or_404(item_id: int, db: Session) -> models.Item:
    item = db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/")
def root():
    return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get("/api/items", response_model=list[ItemOut])
def list_items(
    location: Location | None = None,
    q: str | None = Query(default=None, description="Case-insensitive name search"),
    db: Session = Depends(get_db),
):
    stmt = select(models.Item)
    if location:
        stmt = stmt.where(models.Item.location == location)
    if q:
        stmt = stmt.where(models.Item.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(models.Item.expires_on.is_(None), models.Item.expires_on, models.Item.name)
    return [to_out(i) for i in db.scalars(stmt)]


@app.get("/api/items/expiring", response_model=list[ItemOut])
def expiring_items(days: int = Query(default=settings.expiring_soon_days, ge=0, le=365), db: Session = Depends(get_db)):
    cutoff = date.today() + timedelta(days=days)
    stmt = (
        select(models.Item)
        .where(models.Item.expires_on.is_not(None), models.Item.expires_on <= cutoff)
        .order_by(models.Item.expires_on)
    )
    return [to_out(i) for i in db.scalars(stmt)]


@app.get("/api/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return to_out(get_item_or_404(item_id, db))


@app.post("/api/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = models.Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_out(item)


@app.put("/api/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = get_item_or_404(item_id, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return to_out(item)


@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_item_or_404(item_id, db))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/stats", response_model=Stats)
def stats(db: Session = Depends(get_db)):
    today = date.today()
    soon = today + timedelta(days=settings.expiring_soon_days)
    rows = db.execute(select(models.Item.location, func.count(models.Item.id)).group_by(models.Item.location)).all()
    by_location = {"pantry": 0, "fridge": 0, "freezer": 0} | {loc: n for loc, n in rows}
    expired = db.scalar(select(func.count(models.Item.id)).where(models.Item.expires_on < today)) or 0
    expiring = (
        db.scalar(
            select(func.count(models.Item.id)).where(models.Item.expires_on >= today, models.Item.expires_on <= soon)
        )
        or 0
    )
    return Stats(
        total_items=sum(by_location.values()),
        by_location=by_location,
        expiring_soon=expiring,
        expired=expired,
        expiring_soon_days=settings.expiring_soon_days,
    )
