// Registration form: name, email, password, age, gender, height_cm, weight_kg, goal.
import { AlertCircle, ArrowRight, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import AuthLayout from "../components/AuthLayout.jsx";
import { useAuth } from "../hooks/useAuth.js";

const GENDERS = [["male", "Male"], ["female", "Female"], ["other", "Other"]];
const GOALS = [["fat_loss", "Fat loss"], ["hypertrophy", "Hypertrophy"], ["endurance", "Endurance"]];

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "", email: "", password: "", age: "",
    gender: "male", height_cm: "", weight_kg: "", fitness_goal: "hypertrophy",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register({
        ...form,
        age: Number(form.age),
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
      });
      navigate("/dashboard");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Registration failed. Check your inputs.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Tell us a bit about you — it powers your calorie & AI insights."
      aside="“GymSense recognized 11 exercises and 1,085 reps from one upload.”"
    >
      <form onSubmit={onSubmit} className="grid grid-cols-2 gap-4">
        <Field className="col-span-2" label="Name" name="name" value={form.name} onChange={onChange} placeholder="Jay Doe" />
        <Field className="col-span-2" label="Email" name="email" type="email" value={form.email} onChange={onChange} placeholder="you@example.com" />
        <Field className="col-span-2" label="Password (min 8 chars)" name="password" type="password" value={form.password} onChange={onChange} placeholder="••••••••" />
        <Field label="Age" name="age" type="number" value={form.age} onChange={onChange} placeholder="28" />
        <Select label="Gender" name="gender" value={form.gender} onChange={onChange} options={GENDERS} />
        <Field label="Height (cm)" name="height_cm" type="number" step="0.1" value={form.height_cm} onChange={onChange} placeholder="178" />
        <Field label="Weight (kg)" name="weight_kg" type="number" step="0.1" value={form.weight_kg} onChange={onChange} placeholder="75" />
        <Select className="col-span-2" label="Fitness goal" name="fitness_goal" value={form.fitness_goal} onChange={onChange} options={GOALS} />

        {error && (
          <p className="col-span-2 flex items-center gap-2 text-sm text-red-400">
            <AlertCircle size={15} /> {error}
          </p>
        )}
        <button disabled={busy} className="btn-primary col-span-2 mt-1 w-full">
          {busy ? <><Loader2 size={18} className="animate-spin" /> Creating…</> : <>Create account <ArrowRight size={18} /></>}
        </button>
      </form>

      <p className="mt-6 text-sm text-slate-400">
        Already registered?{" "}
        <Link to="/login" className="font-medium text-emerald-400 hover:underline">Log in</Link>
      </p>
    </AuthLayout>
  );
}

function Field({ label, className = "", ...props }) {
  return (
    <label className={`block ${className}`}>
      <span className="label">{label}</span>
      <input className="input" required {...props} />
    </label>
  );
}

function Select({ label, options, className = "", ...props }) {
  return (
    <label className={`block ${className}`}>
      <span className="label">{label}</span>
      <select className="input" {...props}>
        {options.map(([value, text]) => (
          <option key={value} value={value} className="bg-ink-900">{text}</option>
        ))}
      </select>
    </label>
  );
}
