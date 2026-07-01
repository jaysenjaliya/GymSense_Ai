// Login form -> AuthContext.login -> redirect to dashboard.
import { AlertCircle, ArrowRight, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthLayout from "../components/AuthLayout.jsx";
import { useAuth } from "../hooks/useAuth.js";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to see your analytics and AI coaching."
      aside="“No manual logging. Upload, and let the AI do the rest.”"
    >
      <form onSubmit={onSubmit} className="space-y-5">
        <label className="block">
          <span className="label">Email</span>
          <input className="input" name="email" type="email" value={form.email} onChange={onChange} required placeholder="you@example.com" />
        </label>
        <label className="block">
          <span className="label">Password</span>
          <input className="input" name="password" type="password" value={form.password} onChange={onChange} required placeholder="••••••••" />
        </label>

        {error && (
          <p className="flex items-center gap-2 text-sm text-red-400">
            <AlertCircle size={15} /> {error}
          </p>
        )}

        <button disabled={busy} className="btn-primary w-full">
          {busy ? <><Loader2 size={18} className="animate-spin" /> Signing in…</> : <>Sign in <ArrowRight size={18} /></>}
        </button>
      </form>

      <p className="mt-6 text-sm text-slate-400">
        No account?{" "}
        <Link to="/register" className="font-medium text-emerald-400 hover:underline">Create one</Link>
      </p>
    </AuthLayout>
  );
}
