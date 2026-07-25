"use client";

import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
);

export default function LineChart({ data }) {
  const chartData = {
    labels: data.map(([year]) => year),
    datasets: [
      {
        label: "Accuracy",
        data: data.map(([, accuracy]) => accuracy),
        borderColor: "#38bdf8",
        backgroundColor: "#38bdf8",
        pointBackgroundColor: "#38bdf8",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 7,
        pointHitRadius: 12,
        borderWidth: 3,
        tension: 0.3,
      },
      {
        label: "Log Loss",
        data: data.map(([, , logLoss]) => logLoss),
        borderColor: "#fbbf24",
        backgroundColor: "#fbbf24",
        pointBackgroundColor: "#fbbf24",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 7,
        pointHitRadius: 12,
        borderWidth: 3,
        tension: 0.3,
      },
      {
        label: "Brier Score",
        data: data.map(([, , , brierScore]) => brierScore),
        borderColor: "#c4b5fd",
        backgroundColor: "#c4b5fd",
        pointBackgroundColor: "#c4b5fd",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 7,
        pointHitRadius: 12,
        borderWidth: 3,
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        labels: {
          color: "#ffffff",
          font: {
            size: 14,
          },
        },
      },
      tooltip: {
        enabled: true,
      },
      datalabels: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: "#ffffff",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.08)",
        },
      },
      y: {
        ticks: {
          color: "#ffffff",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.08)",
        },
      },
    },
  };

  return (
    <div className="relative h-[450px] w-full">
      <Line data={chartData} options={options} />
    </div>
  );
}