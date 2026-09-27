import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function CreateBook() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    author: "",
    isbn: "",
    category: "",
    quantity: "",
    location: "",
  });

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/inventory/books", {
        ...form,
        quantity: form.quantity === "" ? "" : Number(form.quantity),
      });
      alert("Book created!");
      navigate("/books");
    } catch {
      alert("Error creating book");
    }
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 720 }}>
        <h2 className="page-title">Add Book</h2>

        <div className="card">
          <form className="form" onSubmit={submit}>
            <div className="form-row">
              <label className="label">Title</label>
              <input
                className="input"
                placeholder="Title"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">Author</label>
              <input
                className="input"
                placeholder="Author"
                value={form.author}
                onChange={(e) => setForm({ ...form, author: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">ISBN</label>
              <input
                className="input"
                placeholder="ISBN"
                value={form.isbn}
                onChange={(e) => setForm({ ...form, isbn: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">Category</label>
              <input
                className="input"
                placeholder="Category"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">Quantity</label>
              <input
                className="input"
                type="number"
                placeholder="Quantity"
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">Location</label>
              <input
                className="input"
                placeholder="Location"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
              />
            </div>

            <hr className="divider" />

            <div className="toolbar" style={{ justifyContent: "flex-end" }}>
              <button
                className="btn"
                type="button"
                onClick={() => navigate("/books")}
              >
                Cancel
              </button>
              <button className="btn" type="submit">
                Create
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
