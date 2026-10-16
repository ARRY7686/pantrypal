"""Fill PantryPal with a realistic kitchen so the UI and dashboards have something to show.

Usage: python scripts/seed_demo_data.py [http://localhost:8000]
Expiry dates are relative to today, so the "expiring soon" and "expired" states always appear.
"""

import json
import sys
import urllib.request
from datetime import date, timedelta

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")

ITEMS = [
    ("Whole milk", "dairy", "fridge", 1, "l", 2),
    ("Greek yoghurt", "dairy", "fridge", 4, "pots", 6),
    ("Cheddar cheese", "dairy", "fridge", 250, "g", 21),
    ("Baby spinach", "produce", "fridge", 1, "bag", 1),
    ("Chicken thighs", "meat", "fridge", 600, "g", -1),
    ("Strawberries", "produce", "fridge", 1, "punnet", 0),
    ("Basmati rice", "grains", "pantry", 2, "kg", 400),
    ("Penne pasta", "grains", "pantry", 3, "packs", 220),
    ("Chopped tomatoes", "canned", "pantry", 6, "cans", 540),
    ("Peanut butter", "snacks", "pantry", 1, "jar", 95),
    ("Sourdough bread", "grains", "pantry", 1, "loaf", 3),
    ("Smoked paprika", "spices", "pantry", 1, "jar", None),
    ("Frozen peas", "frozen", "freezer", 1, "kg", 180),
    ("Vanilla ice cream", "frozen", "freezer", 1, "tub", 75),
    ("Salmon fillets", "meat", "freezer", 4, "pcs", 45),
]


def post(item):
    request = urllib.request.Request(
        f"{BASE}/api/items", data=json.dumps(item).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


for name, category, location, quantity, unit, days in ITEMS:
    expires = (date.today() + timedelta(days=days)).isoformat() if days is not None else None
    created = post(
        {"name": name, "category": category, "location": location, "quantity": quantity, "unit": unit,
         "expires_on": expires}
    )
    print(f"{created['id']:>3}  {created['name']:<20} {created['location']:<8} {created['status']}")
