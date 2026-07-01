// Route guard: waits for auth bootstrap, then redirects unauthenticated users.
import { Loader2 } from "lucide-react";
import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../hooks/useAuth.js";

export default function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center p-24 text-slate-400">
        <Loader2 className="animate-spin" />
        <span className="ml-2">Loading…</span>
      </div>
    );
  }
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
