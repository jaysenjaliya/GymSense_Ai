// Animated, hoverable stat tile. Numbers count up; strings render as-is.
import { motion } from "framer-motion";

import CountUp from "./CountUp.jsx";

export default function StatCard({
  icon: Icon,
  label,
  value,
  numeric = false,
  decimals = 0,
  prefix = "",
  suffix = "",
  delay = 0,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -5 }}
      className="group relative overflow-hidden rounded-2xl glass p-5"
    >
      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-emerald-400/20 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />
      {Icon && (
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-emerald-400/20 to-violet-500/20 text-emerald-300 transition-transform duration-300 group-hover:scale-110">
          <Icon size={18} />
        </span>
      )}
      <div className="mt-3 truncate text-2xl font-bold">
        {numeric ? (
          <CountUp value={value} decimals={decimals} prefix={prefix} suffix={suffix} />
        ) : (
          value
        )}
      </div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    </motion.div>
  );
}
