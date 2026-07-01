// Split-screen auth layout: image/brand panel + glass form panel.
import { motion } from "framer-motion";
import { Dumbbell } from "lucide-react";

import { AUTH_BG } from "../assets/images.js";

export default function AuthLayout({ title, subtitle, children, aside }) {
  return (
    <div className="mx-auto grid max-w-6xl gap-8 px-6 py-12 lg:grid-cols-2 lg:items-center">
      {/* Image / brand panel */}
      <div className="relative hidden overflow-hidden rounded-3xl border border-white/10 lg:block">
        <img src={AUTH_BG} alt="" className="h-[34rem] w-full object-cover" loading="lazy" />
        <div className="absolute inset-0 bg-gradient-to-t from-ink-950 via-ink-950/60 to-emerald-900/30" />
        <div className="absolute bottom-0 p-8">
          <div className="flex items-center gap-2 text-emerald-300">
            <Dumbbell size={20} />
            <span className="font-display text-lg font-bold text-white">GymSense AI</span>
          </div>
          <p className="mt-3 max-w-sm text-lg text-slate-200">
            {aside || "Turn wearable sensor data into rep counts, analytics and AI coaching."}
          </p>
        </div>
      </div>

      {/* Form panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="rounded-3xl glass-strong p-8 sm:p-10"
      >
        <h1 className="text-3xl font-bold">{title}</h1>
        {subtitle && <p className="mt-2 text-slate-400">{subtitle}</p>}
        <div className="mt-8">{children}</div>
      </motion.div>
    </div>
  );
}
