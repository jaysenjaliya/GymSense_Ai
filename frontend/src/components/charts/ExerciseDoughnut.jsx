// Doughnut chart of a metric split across exercises.
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

const PALETTE = [
  "#34d399", "#8b5cf6", "#22d3ee", "#f59e0b", "#f472b6",
  "#60a5fa", "#a3e635", "#fb7185", "#2dd4bf", "#c084fc", "#facc15",
];

export default function ExerciseDoughnut({ exercises = [], metricKey }) {
  if (!exercises.length) {
    return <p className="text-sm text-slate-500">No data to chart yet.</p>;
  }

  const data = {
    labels: exercises.map((e) => e.exercise),
    datasets: [
      {
        data: exercises.map((e) => e[metricKey]),
        backgroundColor: PALETTE,
        borderColor: "#0b1120",
        borderWidth: 2,
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    cutout: "62%",
    plugins: {
      legend: { position: "right", labels: { color: "#cbd5e1", boxWidth: 12, font: { size: 11 } } },
    },
  };

  return <Doughnut data={data} options={options} />;
}
