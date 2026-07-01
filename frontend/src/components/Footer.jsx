// Minimal footer.
import { Dumbbell } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-ink-950/60">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 py-8 text-sm text-slate-500 sm:flex-row">
        <div className="flex items-center gap-2">
          <Dumbbell size={16} className="text-emerald-400" />
          <span className="font-display font-semibold text-slate-300">GymSense AI</span>
        </div>
        <p>Wearable sensor analysis · rep detection · AI coaching</p>
        <p>© {new Date().getFullYear()} GymSense AI</p>
      </div>
    </footer>
  );
}
