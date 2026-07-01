// Single-session results + interactive charts + "Analyze My Workout" (LLM) panel.
import { motion } from "framer-motion";
import {
  Activity, Brain, Flame, Gauge, Lightbulb, Loader2, PieChart, Repeat, Sparkles, Target, Timer, TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { analyzeWorkout } from "../api/analytics.js";
import { getSession } from "../api/sessions.js";
import ExerciseBarChart from "../components/charts/ExerciseBarChart.jsx";
import ExerciseDoughnut from "../components/charts/ExerciseDoughnut.jsx";
import StatCard from "../components/ui/StatCard.jsx";
import { formatDate, formatMinutes } from "../utils/format.js";

const WRAP = "mx-auto w-full max-w-[1600px] px-6 lg:px-10";

const METRICS = [
  { key: "reps", label: "Reps" },
  { key: "estimated_calories", label: "Calories" },
  { key: "duration_seconds", label: "Duration" },
];

export default function SessionResults() {
  const { id } = useParams();
  const [session, setSession] = useState(null);
  const [error, setError] = useState("");
  const [metric, setMetric] = useState("reps");
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data } = await getSession(id);
        setSession(data);
      } catch {
        setError("Session not found.");
      }
    })();
  }, [id]);

  const runAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisError("");
    try {
      const { data } = await analyzeWorkout({ session_id: id });
      setAnalysis(data);
    } catch {
      setAnalysisError("AI analysis failed. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  if (error) return <div className="p-16 text-center text-red-400">{error}</div>;
  if (!session)
    return (
      <div className="flex items-center justify-center p-24 text-slate-400">
        <Loader2 className="animate-spin" /> <span className="ml-2">Loading…</span>
      </div>
    );

  return (
    <div className={`${WRAP} py-10`}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="rounded-3xl glass-strong p-6">
        <div className="flex items-center gap-2 text-emerald-300">
          <Activity size={18} />
          <span className="text-sm">Session results</span>
        </div>
        <h1 className="mt-1 text-2xl font-bold">{formatDate(session.created_at)}</h1>
        <p className="mt-3 text-slate-300">{session.summary}</p>
      </motion.div>

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard icon={Timer} label="Duration (min)" value={session.total_duration_seconds / 60} numeric decimals={1} delay={0} />
        <StatCard icon={Gauge} label="Active (min)" value={session.active_duration_seconds / 60} numeric decimals={1} delay={0.06} />
        <StatCard icon={Repeat} label="Total reps" value={session.total_reps} numeric delay={0.12} />
        <StatCard icon={Flame} label="Calories" value={session.total_estimated_calories} numeric suffix=" kcal" delay={0.18} />
      </div>

      {/* Charts */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-2">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <TrendingUp size={18} className="text-emerald-400" /> By exercise
            </h2>
            <div className="flex gap-1 rounded-xl border border-white/10 bg-white/5 p-1">
              {METRICS.map((m) => (
                <button
                  key={m.key}
                  onClick={() => setMetric(m.key)}
                  className={`rounded-lg px-3 py-1 text-sm transition-colors ${
                    metric === m.key ? "bg-emerald-400 font-medium text-ink-950" : "text-slate-300 hover:bg-white/5"
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>
          <ExerciseBarChart exercises={session.exercises} metricKey={metric} label={METRICS.find((m) => m.key === metric).label} />
        </div>

        <div className="card">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold">
            <PieChart size={18} className="text-emerald-400" /> Calorie split
          </h2>
          <ExerciseDoughnut exercises={session.exercises} metricKey="estimated_calories" />
        </div>
      </div>

      {/* Table */}
      <div className="mt-6 overflow-hidden rounded-2xl glass">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-400">
            <tr>
              {["Exercise", "Sets", "Reps", "Duration", "Calories"].map((h) => (
                <th key={h} className="px-5 py-3 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {session.exercises.map((e, i) => (
              <motion.tr
                key={e.exercise}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.04 }}
                className={`hover:bg-white/5 ${i !== session.exercises.length - 1 ? "border-b border-white/5" : ""}`}
              >
                <td className="px-5 py-3 font-medium text-emerald-300">{e.exercise}</td>
                <td className="px-5 py-3">{e.sets}</td>
                <td className="px-5 py-3">{e.reps}</td>
                <td className="px-5 py-3">{formatMinutes(e.duration_seconds)}</td>
                <td className="px-5 py-3">{e.estimated_calories} kcal</td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* AI analysis */}
      <div className="mt-8 rounded-3xl border border-violet-400/20 bg-gradient-to-br from-violet-500/5 to-emerald-500/5 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <motion.span
              animate={{ scale: [1, 1.08, 1] }}
              transition={{ repeat: Infinity, duration: 2.5 }}
              className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-violet-500/30 to-emerald-400/30 text-violet-200"
            >
              <Brain size={22} />
            </motion.span>
            <div>
              <h2 className="text-lg font-semibold">AI Workout Analysis</h2>
              <p className="text-sm text-slate-400">Personalized coaching from your data.</p>
            </div>
          </div>
          <button onClick={runAnalysis} disabled={analyzing} className="btn-primary">
            {analyzing ? <><Loader2 size={18} className="animate-spin" /> Analyzing…</> : <><Sparkles size={18} /> Analyze My Workout</>}
          </button>
        </div>

        {analysisError && <p className="mt-4 text-sm text-red-400">{analysisError}</p>}

        {analysis && (
          <motion.div initial="hidden" animate="show" variants={{ show: { transition: { staggerChildren: 0.08 } } }} className="mt-6 grid gap-4 sm:grid-cols-2">
            <Block icon={Activity} title="Analysis" text={analysis.analysis} full />
            <Block icon={Lightbulb} title="Suggestions" items={analysis.suggestions} />
            <Block icon={TrendingUp} title="Progress" text={analysis.progress_analysis} />
            <Block icon={Gauge} title="Consistency" text={analysis.consistency_analysis} />
            <Block icon={Target} title="Recommendations" items={analysis.future_recommendations} full />
          </motion.div>
        )}
      </div>
    </div>
  );
}

function Block({ icon: Icon, title, text, items, full }) {
  return (
    <motion.div
      variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
      className={`rounded-2xl glass p-5 ${full ? "sm:col-span-2" : ""}`}
    >
      <h3 className="flex items-center gap-2 font-semibold text-emerald-300">
        <Icon size={16} /> {title}
      </h3>
      {text && <p className="mt-2 text-sm text-slate-300">{text}</p>}
      {items && (
        <ul className="mt-2 space-y-1.5 text-sm text-slate-300">
          {items.map((it, i) => (
            <li key={i} className="flex gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
              {it}
            </li>
          ))}
        </ul>
      )}
    </motion.div>
  );
}
