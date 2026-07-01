// Workout history: summary header + animated session cards.
import { motion } from "framer-motion";
import { CalendarClock, Dumbbell, Flame, Loader2, Repeat, Timer } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listSessions } from "../api/sessions.js";
import CountUp from "../components/ui/CountUp.jsx";
import { formatDate, formatMinutes, formatNumber } from "../utils/format.js";

const WRAP = "mx-auto w-full max-w-[1600px] px-6 lg:px-10";

export default function History() {
  const [sessions, setSessions] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data } = await listSessions();
        setSessions(data);
      } catch {
        setError("Could not load history.");
      }
    })();
  }, []);

  if (error) return <div className="p-16 text-center text-red-400">{error}</div>;
  if (!sessions)
    return (
      <div className="flex items-center justify-center p-24 text-slate-400">
        <Loader2 className="animate-spin" /> <span className="ml-2">Loading…</span>
      </div>
    );

  const totals = sessions.reduce(
    (a, s) => ({
      reps: a.reps + s.total_reps,
      cals: a.cals + s.total_estimated_calories,
    }),
    { reps: 0, cals: 0 }
  );

  return (
    <div className={`${WRAP} py-10`}>
      <h1 className="flex items-center gap-2 text-3xl font-bold sm:text-4xl">
        <CalendarClock className="text-emerald-400" /> Workout history
      </h1>

      {/* Summary strip */}
      {sessions.length > 0 && (
        <div className="mt-6 grid grid-cols-3 gap-4">
          {[
            { label: "Sessions", value: sessions.length, suffix: "" },
            { label: "Total reps", value: totals.reps, suffix: "" },
            { label: "Calories", value: totals.cals, suffix: " kcal" },
          ].map((t, i) => (
            <motion.div key={t.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="rounded-2xl glass p-5 text-center">
              <div className="text-2xl font-bold gradient-text">
                <CountUp value={t.value} suffix={t.suffix} />
              </div>
              <div className="text-xs uppercase tracking-wide text-slate-500">{t.label}</div>
            </motion.div>
          ))}
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="mt-6 rounded-2xl glass p-10 text-center text-slate-400">
          No sessions yet.{" "}
          <Link to="/upload" className="text-emerald-400 hover:underline">Upload one</Link>.
        </div>
      ) : (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          {sessions.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(i * 0.04, 0.4) }}
              whileHover={{ y: -4 }}
            >
              <Link
                to={`/sessions/${s.id}`}
                className="group flex flex-wrap items-center justify-between gap-4 rounded-2xl glass p-5 transition-all hover:border-emerald-400/40 hover:bg-white/5"
              >
                <div className="flex items-center gap-3">
                  <span className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-400/15 text-emerald-300 transition-transform group-hover:scale-110">
                    <Dumbbell size={20} />
                  </span>
                  <div>
                    <div className="font-medium text-slate-100">{formatDate(s.created_at)}</div>
                    <div className="text-xs text-slate-500">{s.exercise_count} exercises detected</div>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-sm text-slate-300">
                  <span className="flex items-center gap-1.5"><Repeat size={15} className="text-slate-500" /> {formatNumber(s.total_reps)}</span>
                  <span className="flex items-center gap-1.5"><Timer size={15} className="text-slate-500" /> {formatMinutes(s.total_duration_seconds)}</span>
                  <span className="flex items-center gap-1.5"><Flame size={15} className="text-slate-500" /> {formatNumber(s.total_estimated_calories)} kcal</span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
