from datetime import date, timedelta


def days_from_today(n: int) -> str:
    return (date.today() + timedelta(days=n)).isoformat()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_checks_database(client):
    assert client.get("/ready").json() == {"status": "ready"}


def test_create_item_returns_201_and_status(client, make_item):
    item = make_item(name="Yoghurt", expires_on=days_from_today(10))
    assert item["id"] > 0
    assert item["name"] == "Yoghurt"
    assert item["status"] == "fresh"
    assert item["days_left"] == 10


def test_create_item_validation(client):
    assert client.post("/api/items", json={"name": ""}).status_code == 422
    assert client.post("/api/items", json={"name": "Rice", "location": "garage"}).status_code == 422
    assert client.post("/api/items", json={"name": "Rice", "quantity": -1}).status_code == 422


def test_list_items_and_filter_by_location(client, make_item):
    make_item(name="Milk", location="fridge")
    make_item(name="Peas", location="freezer", category="frozen")
    make_item(name="Pasta", location="pantry", category="grains")
    assert len(client.get("/api/items").json()) == 3
    freezer = client.get("/api/items", params={"location": "freezer"}).json()
    assert [i["name"] for i in freezer] == ["Peas"]


def test_search_by_name(client, make_item):
    make_item(name="Basmati rice", location="pantry")
    make_item(name="Milk")
    assert [i["name"] for i in client.get("/api/items", params={"q": "RICE"}).json()] == ["Basmati rice"]


def test_get_item_and_404(client, make_item):
    item = make_item()
    assert client.get(f"/api/items/{item['id']}").json()["name"] == "Milk"
    assert client.get("/api/items/9999").status_code == 404


def test_update_item_quantity_and_location(client, make_item):
    item = make_item(quantity=2)
    response = client.put(f"/api/items/{item['id']}", json={"quantity": 0.5, "location": "freezer"})
    assert response.status_code == 200
    assert response.json()["quantity"] == 0.5
    assert response.json()["location"] == "freezer"
    assert response.json()["name"] == "Milk"  # untouched fields stay as they were


def test_delete_item(client, make_item):
    item = make_item()
    assert client.delete(f"/api/items/{item['id']}").status_code == 204
    assert client.get(f"/api/items/{item['id']}").status_code == 404
    assert client.delete(f"/api/items/{item['id']}").status_code == 404


def test_expiring_endpoint_and_statuses(client, make_item):
    make_item(name="Old bread", location="pantry", expires_on=days_from_today(-1))
    make_item(name="Cheese", expires_on=days_from_today(2))
    make_item(name="Honey", location="pantry", expires_on=days_from_today(300))
    make_item(name="Salt", location="pantry")  # no expiry date
    expiring = client.get("/api/items/expiring", params={"days": 3}).json()
    assert [(i["name"], i["status"]) for i in expiring] == [("Old bread", "expired"), ("Cheese", "expiring")]


def test_stats(client, make_item):
    make_item(name="Old milk", expires_on=days_from_today(-3))
    make_item(name="Cream", expires_on=days_from_today(1))
    make_item(name="Ice cream", location="freezer", expires_on=days_from_today(60))
    stats = client.get("/api/stats").json()
    assert stats["total_items"] == 3
    assert stats["by_location"] == {"pantry": 0, "fridge": 2, "freezer": 1}
    assert stats["expired"] == 1
    assert stats["expiring_soon"] == 1


def test_metrics_endpoint_exposes_prometheus_format(client):
    client.get("/health")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
