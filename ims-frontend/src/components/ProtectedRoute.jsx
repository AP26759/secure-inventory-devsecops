import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function ProtectedRoute({ children, role }) {
  const { token, user } = useContext(AuthContext);

  if (!token) return <Navigate to="/login" />;

  if (role && user?.role !== role) return <Navigate to="/dashboard" />;

  return children;
}
