import { useEffect, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const fetchStores = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/stores`);
      const data = await res.json();
      setStores(data.stores || []);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const createStore = async () => {
    setCreating(true);
    await fetch(`${API_BASE}/stores`, { method: "POST" });
    setTimeout(fetchStores, 3000);
    setCreating(false);
  };

  const deleteStore = async (id) => {
    if (!window.confirm("Delete this store permanently?")) return;

    await fetch(`${API_BASE}/stores/${id}`, {
      method: "DELETE",
    });

    fetchStores();
  };

  useEffect(() => {
    fetchStores();
  }, []);

  const statusClass = (status) => {
    if (status === "Ready") return "status ready";
    if (status === "Failed") return "status failed";
    return "status provisioning";
  };

  return (
    <div className="app-bg">
      <div className="container">
        {/* Header */}
        <div className="header">
          <h1>🚀 Store Provisioning Platform</h1>
          <p>Automated Kubernetes Store Orchestration Dashboard</p>
        </div>

        {/* Actions */}
        <div className="actions">
          <button className="btn secondary" onClick={fetchStores}>
            Refresh
          </button>

          <button
            className="btn primary"
            onClick={createStore}
            disabled={creating}
          >
            {creating ? "Provisioning…" : "+ Create Store"}
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="loader">Loading stores…</div>
        ) : stores.length === 0 ? (
          <div className="empty">No stores provisioned yet.</div>
        ) : (
          <div className="grid">
            {stores.map((store) => (
              <div className="card" key={store.store_id}>
                {/* Top */}
                <div className="card-header">
                  <h3>{store.store_id}</h3>
                  <span className={statusClass(store.status)}>
                    {store.status}
                  </span>
                </div>

                {/* Body */}
                <div className="card-body">
                  <p>
                    <strong>Namespace:</strong> {store.namespace}
                  </p>

                  <div className="links">
                    <a
                      href={store.nodeport_url}
                      target="_blank"
                      rel="noreferrer"
                      className="link node"
                    >
                      Open NodePort ↗
                    </a>

                    <a
                      href={store.ingress_url}
                      target="_blank"
                      rel="noreferrer"
                      className="link ingress"
                    >
                      Open Ingress ↗
                    </a>
                  </div>

                </div>

                {/* Footer */}
                <div className="card-footer">
                  <button
                    className="btn danger"
                    onClick={() => deleteStore(store.store_id)}
                  >
                    Delete Store
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}