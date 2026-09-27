import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api";

export default function EditBook() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    author: "",
    isbn: "",
    category: "",
    quantity: "",
    location: "",
  });

  useEffect(() => {
    async function loadBook() {
      try {
        const res = await api.get(`/inventory/books/${id}`);
        const book = res.data.book || {};

        setForm({
          title: book.title ?? "",
          author: book.author ?? "",
          isbn: book.isbn ?? "",
          category: book.category ?? "",
          quantity: book.quantity ?? "",
          location: book.location ?? "",
        });
      } catch (error) {
        console.error("Error fetching book:", error);
        alert("Failed to load book details.");
      }
    }
    loadBook();
  }, [id]);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/inventory/books/${id}`, {
        ...form,
        quantity: form.quantity === "" ? "" : Number(form.quantity),
      });
      alert("Updated!");
      navigate("/books");
    } catch {
      alert("Update failed");
    }
  };

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 720 }}>
        <h2 className="page-title">Edit Book</h2>

        <div className="card">
          <form className="form" onSubmit={submit}>
            <div className="form-row">
              <label className="label">Title</label>
              <input
                className="input"
                type="text"
                placeholder="Title"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">Author</label>
              <input
                className="input"
                type="text"
                placeholder="Author"
                value={form.author}
                onChange={(e) => setForm({ ...form, author: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">ISBN</label>
              <input
                className="input"
                type="text"
                placeholder="ISBN"
                value={form.isbn}
                onChange={(e) => setForm({ ...form, isbn: e.target.value })}
              />
            </div>

            <div className="form-row">
              <label className="label">Category</label>
              <input
                className="input"
                type="text"
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
                type="text"
                placeholder="Location"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
              />
            </div>

            <hr className="divider" />

            <div className="toolbar" style={{ justifyContent: "flex-end" }}>
              <button className="btn" type="button" onClick={() => navigate("/books")}>
                Cancel
              </button>
              <button className="btn" type="submit">
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
