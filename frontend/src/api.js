// Thin wrapper around the PantryPal REST API. All paths are relative, so the same
// build works behind Vite (dev), nginx (Docker Compose) and the Kubernetes Ingress.
const BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* non-JSON error body */
    }
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  listItems: (params = {}) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString();
    return request(`/items${query ? `?${query}` : ""}`);
  },
  stats: () => request("/stats"),
  createItem: (item) => request("/items", { method: "POST", body: JSON.stringify(item) }),
  updateItem: (id, changes) => request(`/items/${id}`, { method: "PUT", body: JSON.stringify(changes) }),
  deleteItem: (id) => request(`/items/${id}`, { method: "DELETE" }),
};
