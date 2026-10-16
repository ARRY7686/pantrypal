from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Location = Literal["pantry", "fridge", "freezer"]
Category = Literal["produce", "dairy", "meat", "grains", "canned", "snacks", "drinks", "spices", "frozen", "other"]


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: Category = "other"
    location: Location = "pantry"
    quantity: float = Field(default=1, ge=0)
    unit: str = Field(default="pcs", min_length=1, max_length=20)
    expires_on: date | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: Category | None = None
    location: Location | None = None
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    expires_on: date | None = None


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    days_left: int | None = None
    status: Literal["fresh", "expiring", "expired", "no-date"] = "no-date"


class Stats(BaseModel):
    total_items: int
    by_location: dict[str, int]
    expiring_soon: int
    expired: int
    expiring_soon_days: int
