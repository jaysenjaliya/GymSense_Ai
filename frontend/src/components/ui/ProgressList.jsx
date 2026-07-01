// Animated horizontal bars showing each item's share of the total.
import { motion } from "framer-motion";

export default function ProgressList({ items = [], labelKey, valueKey, unit = "" }) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">No data yet.</p>;
  }
  const max = Math.max(...items.map((i) => i[valueKey])) || 1;

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={item[labelKey]}>
          <div className="mb-1 flex justify-between text-sm">
            <span className="text-slate-200">{item[labelKey]}</span>
            <span className="text-slate-400">
              {Math.round(item[valueKey]).toLocaleString()}
              {unit}
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-white/5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(item[valueKey] / max) * 100}%` }}
              transition={{ duration: 0.9, delay: i * 0.06, ease: "easeOut" }}
              className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-violet-400"
            />
          </div>
        </div>
      ))}
    </div>
  );
}
