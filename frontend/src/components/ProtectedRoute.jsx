// Route guard: redirects unauthenticated users to /login.
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";

export default function ProtectedRoute() {
  const { user } = useAuth();
  // TODO: also handle a loading/bootstrap state before redirecting.
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
