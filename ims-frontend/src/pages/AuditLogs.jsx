import { useEffect, useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchLogs() {
      try {
        const res = await api.get("/audit/logs");
        setLogs(res.data.logs || []);
      } catch (error) {
        console.log("Error fetching audit logs:", error);
        if (error.response && error.response.status === 401) {
          alert("You are not authorized to view audit logs. Please login.");
          navigate("/login");
        } else {
          alert("Failed to load audit logs.");
        }
      }
    }

    fetchLogs();
  }, [navigate]);

  return (
    <div className="page">
      <div className="container">
        <h2 className="page-title">Audit Logs</h2>

        <div className="card">
          {Array.isArray(logs) && logs.length > 0 ? (
            <ul className="list">
              {logs.map((log) => (
                <li className="list-item" key={log.id}>
                  <div>
                    <div>
                      <strong>{log.action}</strong>{" "}
                      <span className="meta">({log.resource_type})</span>
                    </div>

                    <div className="meta">
                      Time: {log.timestamp} • User: {log.username || "Unknown"} (ID:{" "}
                      {log.user_id ?? "N/A"})
                    </div>
                  </div>

                  <div className="row-actions">
                    <span className="meta">#{log.id}</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="meta">No logs found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
