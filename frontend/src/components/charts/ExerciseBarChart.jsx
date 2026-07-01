// Bar chart of a metric per exercise, built on Chart.js via react-chartjs-2.
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

/**
 * @param exercises array of objects with an `exercise` field
 * @param metricKey  field to plot (e.g. "reps", "total_reps")
 * @param label      dataset label
 */
export default function ExerciseBarChart({ exercises = [], metricKey, label, color = "#34d399" }) {
  const data = {
    labels: exercises.map((e) => e.exercise),
    datasets: [
      {
        label,
        data: exercises.map((e) => e[metricKey]),
        backgroundColor: color,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { labels: { color: "#cbd5e1" } } },
    scales: {
      x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
      y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" }, beginAtZero: true },
    },
  };

  if (!exercises.length) {
    return <p className="text-sm text-slate-500">No exercise data to chart.</p>;
  }
  return <Bar data={data} options={options} />;
}
