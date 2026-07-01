// Authenticated home: quick actions, animated analytics, recent history.
import { motion } from "framer-motion";
import {
  ArrowRight, CalendarDays, Dumbbell, Flame, PieChart, Radio, Repeat, Star, Timer, TrendingUp, UploadCloud,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getSummary } from "../api/analytics.js";
import { listSessions } from "../api/sessions.js";
import { IMAGES } from "../assets/images.js";
import ExerciseDoughnut from "../components/charts/ExerciseDoughnut.jsx";
import ProgressList from "../components/ui/ProgressList.jsx";
import StatCard from "../components/ui/StatCard.jsx";
import { useAuth } from "../hooks/useAuth.js";
import { formatDate, formatNumber } from "../utils/format.js";

const WRAP = "mx-auto w-full max-w-[1600px] px-6 lg:px-10";

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [s, sessions] = await Promise.all([getSummary(), listSessions()]);
        setSummary(s.data);
        setRecent(sessions.data.slice(0, 6));
      } catch {
        setError("Could not load your dashboard.");
      }
    })();
  }, []);

  const topExercises = (summary?.per_exercise || []).slice(0, 6);

  return (
    <div className={`${WRAP} py-10`}>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold sm:text-4xl">
          Welcome back, <span className="gradient-text">{user?.name}</span> 👋
        </h1>
        <p className="mt-1 flex items-center gap-2 text-slate-400">
          <TrendingUp size={15} className="text-emerald-400" />
          Goal: {user?.fitness_goal?.replace("_", " ")}
        </p>
      </motion.div>

      {/* Quick actions */}
      <div className="mt-8 grid gap-5 lg:grid-cols-3">
        <Link to="/upload" className="group relative overflow-hidden rounded-2xl border border-emerald-400/30 lg:col-span-2">
          <img src={IMAGES.uploadHero} alt="" className="absolute inset-0 h-full w-full object-cover opacity-25 transition-transform duration-700 group-hover:scale-105" />
          <div className="absolute inset-0 bg-gradient-to-r from-ink-950 to-emerald-900/40" />
          <div className="relative flex items-center justify-between p-7">
            <div>
              <div className="flex items-center gap-2 text-emerald-300">
                <UploadCloud size={22} />
                <h3 className="text-xl font-semibold">Upload Today's Session</h3>
              </div>
              <p className="mt-1 text-sm text-slate-300">Analyze a completed wearable session CSV in seconds.</p>
            </div>
            <ArrowRight className="text-emerald-300 transition-transform group-hover:translate-x-1.5" />
          </div>
        </Link>

        <div className="relative cursor-not-allowed overflow-hidden rounded-2xl border border-white/10 opacity-70" title="Real-time streaming coming soon">
          <div className="flex h-full items-center justify-between p-7">
            <div>
              <div className="flex items-center gap-2 text-slate-300">
                <Radio size={22} />
                <h3 className="text-xl font-semibold">Start Today's Session</h3>
              </div>
              <p className="mt-1 text-sm text-slate-500">Live tracking — coming soon.</p>
            </div>
            <span className="rounded-full border border-white/10 px-2 py-0.5 text-xs text-slate-500">Soon</span>
          </div>
        </div>
      </div>

      {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

      {/* Stats */}
      {summary && (
        <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard icon={Dumbbell} label="Sessions" value={summary.total_sessions} numeric delay={0} />
          <StatCard icon={Repeat} label="Total reps" value={summary.total_reps} numeric delay={0.05} />
          <StatCard icon={Timer} label="Active min" value={summary.total_active_seconds / 60} numeric decimals={1} delay={0.1} />
          <StatCard icon={Flame} label="Calories" value={summary.total_estimated_calories} numeric suffix=" kcal" delay={0.15} />
          <StatCard icon={CalendarDays} label="This week" value={summary.sessions_last_7_days} numeric delay={0.2} />
          <StatCard icon={Star} label="Favorite" value={summary.favorite_exercise || "—"} delay={0.25} />
        </div>
      )}

      {/* Charts row */}
      {summary && topExercises.length > 0 && (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <PieChart size={18} className="text-emerald-400" /> Time by exercise
            </h2>
            <div className="mx-auto max-w-sm">
              <ExerciseDoughnut exercises={topExercises} metricKey="total_duration_seconds" />
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <TrendingUp size={18} className="text-emerald-400" /> Top exercises · total reps
            </h2>
            <ProgressList items={topExercises} labelKey="exercise" valueKey="total_reps" />
          </motion.div>
        </div>
      )}

      {/* Recent */}
      <div className="mt-10">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent sessions</h2>
          <Link to="/history" className="text-sm text-emerald-400 hover:underline">View all</Link>
        </div>
        {recent.length === 0 ? (
          <div className="mt-3 rounded-2xl glass p-8 text-center text-slate-400">
            No sessions yet — <Link to="/upload" className="text-emerald-400 hover:underline">upload your first one</Link>!
          </div>
        ) : (
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {recent.map((s, i) => (
              <motion.div key={s.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} whileHover={{ y: -3 }}>
                <Link
                  to={`/sessions/${s.id}`}
                  className="flex items-center justify-between rounded-2xl glass px-5 py-4 transition-colors hover:border-emerald-400/40 hover:bg-white/5"
                >
                  <span className="text-sm text-slate-200">{formatDate(s.created_at)}</span>
                  <span className="flex items-center gap-4 text-sm text-slate-400">
                    <span>{s.exercise_count} ex.</span>
                    <span className="flex items-center gap-1"><Repeat size={13} /> {formatNumber(s.total_reps)}</span>
                    <span className="flex items-center gap-1"><Flame size={13} /> {formatNumber(s.total_estimated_calories)}</span>
                  </span>
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
