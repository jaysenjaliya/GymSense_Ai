// Upload a completed wearable session CSV -> POST /sessions/upload -> results.
import { motion } from "framer-motion";
import {
  Activity, AlertCircle, Brain, FileCheck2, Loader2, Repeat, Sparkles, UploadCloud,
} from "lucide-react";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { uploadSession } from "../api/sessions.js";
import { IMAGES } from "../assets/images.js";

const WRAP = "mx-auto w-full max-w-[1600px] px-6 lg:px-10";

const STEPS = [
  { icon: Activity, title: "Detect exercises", body: "A deep-learning model classifies 12 gym exercises from your sensor stream." },
  { icon: Repeat, title: "Count reps & sets", body: "Peak detection counts reps; contiguous segments become sets." },
  { icon: Brain, title: "AI coaching", body: "Get analysis, progress and recommendations tailored to your goal." },
];

export default function UploadSession() {
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const pick = (f) => {
    if (f && f.name.toLowerCase().endsWith(".csv")) {
      setFile(f);
      setError("");
    } else if (f) {
      setError("Please choose a .csv file.");
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    pick(e.dataTransfer.files?.[0]);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setError("");
    setBusy(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await uploadSession(formData);
      navigate(`/sessions/${data.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Upload failed. Is this a valid session CSV?");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`${WRAP} py-12`}>
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
        <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">
          <Sparkles size={13} /> AI analysis
        </span>
        <h1 className="mt-4 text-3xl font-bold sm:text-4xl">Upload a session</h1>
        <p className="mt-2 text-slate-400">
          Drop a wearable session CSV with columns{" "}
          <code className="rounded bg-white/10 px-1.5 py-0.5 text-xs text-emerald-300">A_x, A_y, A_z, G_x, G_y, G_z, C_1</code>.
        </p>
      </motion.div>

      <div className="mt-8 grid gap-8 lg:grid-cols-5">
        {/* Dropzone */}
        <form onSubmit={onSubmit} className="lg:col-span-3">
          <motion.div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            animate={dragging ? { scale: 1.01 } : { scale: 1 }}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed p-16 text-center transition-colors ${
              dragging ? "border-emerald-400 bg-emerald-400/10" : "border-white/15 bg-white/[0.02] hover:border-white/30"
            }`}
          >
            <input ref={inputRef} type="file" accept=".csv" className="hidden" onChange={(e) => pick(e.target.files?.[0])} />
            {file ? (
              <>
                <FileCheck2 size={48} className="text-emerald-400" />
                <p className="mt-4 text-lg font-medium text-slate-100">{file.name}</p>
                <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB · click to replace</p>
              </>
            ) : (
              <>
                <motion.div animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 3 }}>
                  <UploadCloud size={52} className="text-slate-400" />
                </motion.div>
                <p className="mt-4 text-lg font-medium text-slate-200">Drag &amp; drop your CSV here</p>
                <p className="text-sm text-slate-500">or click to browse</p>
              </>
            )}
          </motion.div>

          {error && (
            <p className="mt-4 flex items-center gap-2 text-sm text-red-400">
              <AlertCircle size={15} /> {error}
            </p>
          )}

          <button disabled={!file || busy} className="btn-primary mt-6 w-full">
            {busy ? <><Loader2 size={18} className="animate-spin" /> Analyzing… this can take a few seconds</> : <>Analyze workout <Sparkles size={18} /></>}
          </button>
        </form>

        {/* Info panel */}
        <div className="lg:col-span-2">
          <div className="relative overflow-hidden rounded-3xl border border-white/10">
            <img src={IMAGES.dumbbells} alt="" className="h-40 w-full object-cover opacity-40" loading="lazy" />
            <div className="absolute inset-0 bg-gradient-to-t from-ink-950 to-transparent" />
            <div className="absolute bottom-4 left-5 font-display text-lg font-semibold">What happens next</div>
          </div>
          <div className="mt-4 space-y-3">
            {STEPS.map((s, i) => (
              <motion.div
                key={s.title}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + i * 0.1 }}
                className="flex gap-3 rounded-2xl glass p-4"
              >
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-400/15 text-emerald-300">
                  <s.icon size={18} />
                </span>
                <div>
                  <div className="text-sm font-semibold">{s.title}</div>
                  <div className="text-xs text-slate-400">{s.body}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
