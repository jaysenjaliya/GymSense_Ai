// Marketing landing page: cinematic hero, features, how-it-works, CTA.
import { motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  LineChart,
  Sparkles,
  Timer,
  UploadCloud,
  Zap,
} from "lucide-react";
import { Link } from "react-router-dom";

import { IMAGES } from "../assets/images.js";
import Reveal from "../components/ui/Reveal.jsx";

const EXERCISES = [
  "Squat", "Bench Press", "Leg Press", "Arm Curl", "Running",
  "Rope Skipping", "Adductor", "Leg Curl", "Riding", "Stair Climber", "Walking",
];

const FEATURES = [
  { icon: UploadCloud, title: "Upload & Auto-Analyze", body: "Drop a wearable session CSV. GymSense segments every exercise and counts your reps automatically." },
  { icon: BrainCircuit, title: "AI Coaching", body: "An LLM turns your data into analysis, progress tracking and forward-looking recommendations." },
  { icon: LineChart, title: "Track Progress", body: "Volume, consistency, calories and per-exercise trends across your entire training history." },
  { icon: Zap, title: "Deep-Learning Core", body: "A Hybrid CNN + self-attention model recognizes 12 gym exercises with ~95% window accuracy." },
];

const STATS = [
  { value: "12", label: "Exercises detected" },
  { value: "~95%", label: "Recognition accuracy" },
  { value: "0", label: "Manual logging" },
];

const STEPS = [
  { icon: UploadCloud, title: "Upload session", body: "Export your wearable CSV and drop it in." },
  { icon: Activity, title: "AI analyzes", body: "Exercises, sets, reps, duration & calories — computed instantly." },
  { icon: Sparkles, title: "Get coached", body: "Personalized insights and next-step recommendations." },
];

export default function Landing() {
  return (
    <div className="mx-auto w-full max-w-[1600px] px-6 lg:px-10">
      {/* HERO */}
      <section className="grid items-center gap-10 py-16 lg:grid-cols-2 lg:py-24">
        <div>
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300"
          >
            <Sparkles size={13} /> AI-powered fitness analytics
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.05 }}
            className="mt-5 text-5xl font-bold leading-[1.05] sm:text-6xl"
          >
            Your workouts,
            <br />
            <span className="gradient-text bg-200 animate-gradient-x">decoded by AI</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="mt-5 max-w-xl text-lg text-slate-400"
          >
            GymSense AI turns raw wearable sensor data into exercise summaries, rep counts,
            analytics and intelligent coaching — no manual logging required.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="mt-8 flex flex-wrap gap-4"
          >
            <Link to="/register" className="btn-primary">
              Use GymSense <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="btn-ghost">Log in</Link>
          </motion.div>

          <div className="mt-10 flex gap-8">
            {STATS.map((s) => (
              <div key={s.label}>
                <div className="text-3xl font-bold gradient-text">{s.value}</div>
                <div className="text-xs uppercase tracking-wide text-slate-500">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Hero image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="relative"
        >
          <div className="animate-float overflow-hidden rounded-3xl border border-white/10 shadow-2xl shadow-emerald-500/10">
            <img
              src={IMAGES.heroAthlete}
              alt="Athlete training in a gym"
              className="h-[30rem] w-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-ink-950 via-ink-950/20 to-transparent" />
          </div>
          {/* floating glass stat card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="absolute -bottom-5 -left-5 flex items-center gap-3 rounded-2xl glass-strong px-4 py-3 shadow-xl"
          >
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-400/20 text-emerald-300">
              <Timer size={20} />
            </span>
            <div>
              <div className="text-sm font-semibold">1,085 reps</div>
              <div className="text-xs text-slate-400">detected this session</div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Exercise marquee */}
      <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02] py-4">
        <div className="flex w-max animate-marquee gap-4">
          {[...EXERCISES, ...EXERCISES].map((ex, i) => (
            <span
              key={i}
              className="whitespace-nowrap rounded-full border border-white/10 px-4 py-1.5 text-sm text-slate-300"
            >
              {ex}
            </span>
          ))}
        </div>
      </div>

      {/* FEATURES */}
      <section className="py-20">
        <Reveal>
          <h2 className="text-center text-3xl font-bold sm:text-4xl">
            Everything you need to <span className="gradient-text">train smarter</span>
          </h2>
        </Reveal>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f, i) => (
            <Reveal key={f.title} delay={i * 0.08}>
              <div className="card group h-full transition-transform duration-300 hover:-translate-y-1.5">
                <span className="mb-4 grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-emerald-400/20 to-violet-500/20 text-emerald-300 transition-transform group-hover:scale-110">
                  <f.icon size={22} />
                </span>
                <h3 className="text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{f.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="grid items-center gap-10 py-16 lg:grid-cols-2">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-white/10">
            <img src={IMAGES.gymInterior} alt="Modern gym" className="h-96 w-full object-cover" loading="lazy" />
            <div className="absolute inset-0 bg-gradient-to-tr from-ink-950/80 to-transparent" />
          </div>
        </Reveal>
        <div>
          <Reveal>
            <h2 className="text-3xl font-bold sm:text-4xl">
              From CSV to <span className="gradient-text">coaching</span> in seconds
            </h2>
          </Reveal>
          <div className="mt-8 space-y-6">
            {STEPS.map((s, i) => (
              <Reveal key={s.title} delay={i * 0.1}>
                <div className="flex gap-4">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl glass text-emerald-300">
                    <s.icon size={20} />
                  </span>
                  <div>
                    <h3 className="font-semibold">{i + 1}. {s.title}</h3>
                    <p className="text-sm text-slate-400">{s.body}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <Reveal>
        <section className="relative mb-20 overflow-hidden rounded-3xl border border-white/10">
          <img src={IMAGES.barbell} alt="" className="absolute inset-0 h-full w-full object-cover opacity-30" loading="lazy" />
          <div className="absolute inset-0 bg-gradient-to-r from-ink-950 via-ink-950/80 to-emerald-900/40" />
          <div className="relative px-8 py-16 text-center">
            <h2 className="text-3xl font-bold sm:text-4xl">Ready to decode your training?</h2>
            <p className="mx-auto mt-3 max-w-xl text-slate-300">
              Create a free account and upload your first session in under a minute.
            </p>
            <Link to="/register" className="btn-primary mt-8">
              Get started free <ArrowRight size={18} />
            </Link>
          </div>
        </section>
      </Reveal>
    </div>
  );
}
