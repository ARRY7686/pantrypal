import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api.js";

const LOCATIONS = [
  { id: "", label: "All" },
  { id: "pantry", label: "Pantry" },
  { id: "fridge", label: "Fridge" },
  { id: "freezer", label: "Freezer" },
];
const CATEGORIES = ["produce", "dairy", "meat", "grains", "canned", "snacks", "drinks", "spices", "frozen", "other"];
const EMPTY_FORM = { name: "", category: "produce", location: "fridge", quantity: 1, unit: "pcs", expires_on: "" };

function expiryLabel(item) {
  if (item.days_left === null || item.days_left === undefined) return "No expiry date";
  if (item.days_left < 0) return `Expired ${-item.days_left} day${item.days_left === -1 ? "" : "s"} ago`;
  if (item.days_left === 0) return "Expires today";
  return `Expires in ${item.days_left} day${item.days_left === 1 ? "" : "s"}`;
}

function StatCard({ label, value, tone }) {
  return (
    <div className={`stat stat--${tone}`}>
      <span className="stat__value">{value}</span>
      <span className="stat__label">{label}</span>
    </div>
  );
}

function ItemCard({ item, onQuantity, onDelete }) {
  return (
    <article className={`item item--${item.status}`}>
      <header className="item__head">
        <h3 className="item__name">{item.name}</h3>
        <span className={`badge badge--${item.status}`}>{expiryLabel(item)}</span>
      </header>
      <p className="item__meta">
        <span className="chip">{item.location}</span>
        <span className="chip chip--muted">{item.category}</span>
        {item.expires_on && <span className="item__date">{item.expires_on}</span>}
      </p>
      <footer className="item__foot">
        <div className="qty" aria-label={`Quantity of ${item.name}`}>
          <button type="button" onClick={() => onQuantity(item, -1)} disabled={item.quantity <= 0} aria-label="Use one">
            −
          </button>
          <span>
            {item.quantity} {item.unit}
          </span>
          <button type="button" onClick={() => onQuantity(item, 1)} aria-label="Add one">
            +
          </button>
        </div>
        <button type="button" className="link-danger" onClick={() => onDelete(item)}>
          Remove
        </button>
      </footer>
    </article>
  );
}

export default function App() {
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [location, setLocation] = useState("");
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setError("");
      const [list, summary] = await Promise.all([api.listItems({ location, q: search }), api.stats()]);
      setItems(list);
      setStats(summary);
    } catch (e) {
      setError(`Could not reach the PantryPal API (${e.message}).`);
    } finally {
      setLoading(false);
    }
  }, [location, search]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const urgent = useMemo(() => items.filter((i) => i.status === "expiring" || i.status === "expired"), [items]);

  async function addItem(event) {
    event.preventDefault();
    try {
      await api.createItem({ ...form, quantity: Number(form.quantity), expires_on: form.expires_on || null });
      setForm({ ...EMPTY_FORM, location: form.location });
      refresh();
    } catch (e) {
      setError(`Could not add item: ${e.message}`);
    }
  }

  async function changeQuantity(item, delta) {
    await api.updateItem(item.id, { quantity: Math.max(0, item.quantity + delta) });
    refresh();
  }

  async function removeItem(item) {
    await api.deleteItem(item.id);
    refresh();
  }

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <span className="brand__logo" aria-hidden="true">
            P
          </span>
          <div>
            <h1>PantryPal</h1>
            <p>Know what is in your kitchen before it goes off.</p>
          </div>
        </div>
      </header>

      <main className="layout">
        <section className="stats" aria-label="Summary">
          <StatCard label="Items tracked" value={stats?.total_items ?? "–"} tone="neutral" />
          <StatCard
            label={`Expiring within ${stats?.expiring_soon_days ?? 3} days`}
            value={stats?.expiring_soon ?? "–"}
            tone="warn"
          />
          <StatCard label="Expired" value={stats?.expired ?? "–"} tone="bad" />
          <StatCard
            label="Pantry · Fridge · Freezer"
            value={stats ? `${stats.by_location.pantry} · ${stats.by_location.fridge} · ${stats.by_location.freezer}` : "–"}
            tone="neutral"
          />
        </section>

        {urgent.length > 0 && (
          <section className="alert" role="status">
            <strong>Use these first:</strong> {urgent.map((i) => i.name).join(", ")}
          </section>
        )}

        {error && (
          <section className="alert alert--error" role="alert">
            {error}
          </section>
        )}

        <div className="columns">
          <section className="panel" aria-labelledby="add-title">
            <h2 id="add-title">Add an item</h2>
            <form className="form" onSubmit={addItem}>
              <label>
                Name
                <input required maxLength={120} value={form.name} onChange={update("name")} placeholder="e.g. Greek yoghurt" />
              </label>
              <div className="form__row">
                <label>
                  Category
                  <select value={form.category} onChange={update("category")}>
                    {CATEGORIES.map((c) => (
                      <option key={c}>{c}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Location
                  <select value={form.location} onChange={update("location")}>
                    {LOCATIONS.filter((l) => l.id).map((l) => (
                      <option key={l.id} value={l.id}>
                        {l.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <div className="form__row">
                <label>
                  Quantity
                  <input type="number" min="0" step="0.5" value={form.quantity} onChange={update("quantity")} />
                </label>
                <label>
                  Unit
                  <input maxLength={20} value={form.unit} onChange={update("unit")} />
                </label>
              </div>
              <label>
                Expires on
                <input type="date" value={form.expires_on} onChange={update("expires_on")} />
              </label>
              <button type="submit" className="primary">
                Add to {LOCATIONS.find((l) => l.id === form.location)?.label.toLowerCase()}
              </button>
            </form>
          </section>

          <section className="panel panel--wide" aria-labelledby="list-title">
            <div className="toolbar">
              <h2 id="list-title">Inventory</h2>
              <nav className="tabs" aria-label="Filter by location">
                {LOCATIONS.map((l) => (
                  <button
                    key={l.id || "all"}
                    type="button"
                    className={location === l.id ? "tab tab--active" : "tab"}
                    onClick={() => setLocation(l.id)}
                  >
                    {l.label}
                  </button>
                ))}
              </nav>
              <input
                className="search"
                type="search"
                placeholder="Search items…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                aria-label="Search items"
              />
            </div>

            {loading ? (
              <p className="empty">Loading…</p>
            ) : items.length === 0 ? (
              <p className="empty">Nothing here yet. Add your first item on the left.</p>
            ) : (
              <div className="grid">
                {items.map((item) => (
                  <ItemCard key={item.id} item={item} onQuantity={changeQuantity} onDelete={removeItem} />
                ))}
              </div>
            )}
          </section>
        </div>
      </main>

      <footer className="footer">PantryPal · FastAPI + PostgreSQL + React · DevOps capstone</footer>
    </div>
  );
}
