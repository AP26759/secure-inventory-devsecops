import { useEffect, useState, useContext, useCallback } from "react";
import api from "../api";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Books() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState("");
  const { user } = useContext(AuthContext);

  const [category, setCategory] = useState("");
  const [categories, setCategories] = useState([]);

  const load = useCallback(async () => {
    const res = await api.get("/inventory/books", {
      params: {
        search,
        category: category || undefined,
      },
    });
    setBooks(res.data.books || res.data);
  }, [search, category]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    async function loadCategories() {
      try {
        const res = await api.get("/inventory/categories");
        setCategories(res.data.categories || []);
      } catch (err) {
        console.error("Failed to load categories", err);
      }
    }
    loadCategories();
  }, []);

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this book? This action cannot be undone."
    );
    if (!confirmed) return;

    try {
      await api.delete(`/inventory/books/${id}`);
      alert("Book deleted");
      load();
    } catch (err) {
      console.error("Delete failed:", err);
      alert("Failed to delete book");
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h2 className="page-title">Books</h2>

        <div className="card">
          <div className="toolbar">
            <input
              className="input input--search"
              placeholder="Search..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

            <button className="btn" onClick={load}>
              Search
            </button>

            <select
              className="select--compact"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">All categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <ul className="list">
            {books.map((b) => (
              <li className="list-item" key={b.id}>
                <div>
                  <div>
                    <strong>{b.title}</strong> — {b.author}
                  </div>
                  <div className="meta">
                    Category: {b.category || "N/A"} • ISBN: {b.isbn || "N/A"} • Qty:{" "}
                    {b.quantity ?? "N/A"}
                  </div>
                </div>

                {user.role === "librarian" && (
                  <div className="row-actions">
                    <Link className="btn" to={`/manage/edit/${b.id}`}>
                      Edit
                    </Link>

                    <button
                      className="btn btn--danger"
                      onClick={() => handleDelete(b.id)}
                      type="button"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
