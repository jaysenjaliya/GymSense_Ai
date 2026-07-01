// Sticky glass navigation bar. Links adapt to auth state.
import { motion } from "framer-motion";
import { Dumbbell, LayoutDashboard, LogOut, Upload, History as HistoryIcon } from "lucide-react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth.js";

const linkClass = ({ isActive }) =>
  `flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors ${
    isActive ? "bg-white/10 text-emerald-300" : "text-slate-300 hover:text-white"
  }`;

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <motion.header
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="sticky top-0 z-50 border-b border-white/10 bg-ink-950/70 backdrop-blur-xl"
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-emerald-400 to-violet-500 text-ink-950">
            <Dumbbell size={18} strokeWidth={2.5} />
          </span>
          <span className="text-lg font-bold font-display">
            <span className="gradient-text">Gym</span>Sense<span className="text-emerald-400"> AI</span>
          </span>
        </Link>

        <nav className="flex items-center gap-1.5">
          {user ? (
            <>
              <NavLink to="/dashboard" className={linkClass}>
                <LayoutDashboard size={15} /> Dashboard
              </NavLink>
              <NavLink to="/upload" className={linkClass}>
                <Upload size={15} /> Upload
              </NavLink>
              <NavLink to="/history" className={linkClass}>
                <HistoryIcon size={15} /> History
              </NavLink>
              <span className="ml-2 hidden text-sm text-slate-500 sm:inline">
                {user.name}
              </span>
              <button
                onClick={handleLogout}
                className="ml-1 flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-sm text-slate-300 hover:bg-white/5"
              >
                <LogOut size={15} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-3 py-1.5 text-sm text-slate-300 hover:text-white">
                Login
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-gradient-to-r from-emerald-400 to-teal-400 px-4 py-1.5 text-sm font-semibold text-ink-950 transition-transform hover:scale-105"
              >
                Get Started
              </Link>
            </>
          )}
        </nav>
      </div>
    </motion.header>
  );
}
