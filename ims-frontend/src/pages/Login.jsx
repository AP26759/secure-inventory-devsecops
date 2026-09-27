import { useState, useContext } from "react";
import api from "../api";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/auth/login", { username, password });
      login(res.data.access_token, res.data.user);
      navigate("/dashboard");
    } catch {
      alert("Invalid username or password");
    }
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 520 }}>
        <h2 className="page-title">Login</h2>

        <div className="card">
          <form className="form" onSubmit={handleSubmit}>
            <div className="form-row">
              <label className="label">Username</label>
              <input
                className="input"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </div>

            <div className="form-row">
              <label className="label">Password</label>
              <input
                className="input"
                placeholder="Enter your password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>

            <div className="toolbar" style={{ justifyContent: "flex-end" }}>
              <button className="btn" type="submit">
                Login
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
