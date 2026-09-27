import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const { user, logout } = useContext(AuthContext);

  return (
    <div className="page">
      <div className="container">
        <h2 className="page-title">
          Welcome, {user.username}{" "}
          <span className="meta">({user.role})</span>
        </h2>

        <div className="card">
          <div className="toolbar">
            <Link to="/books" className="btn">
              View Books
            </Link>

            {user.role === "librarian" && (
              <>
                <Link to="/manage/create" className="btn">
                  Add Book
                </Link>

                <Link to="/audit" className="btn">
                  View Audit Logs
                </Link>
              </>
            )}
          </div>

          <hr className="divider" />

          <div className="toolbar" style={{ justifyContent: "flex-end" }}>
            <button className="btn" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
