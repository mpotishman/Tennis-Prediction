"use client";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import React from "react";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function BarChart({ labels, values, label }) {
  const data = {
    labels,
    datasets: [
      {
        label,
        data: values,
        backgroundColor: "rgba(245, 240, 222, 0.15)",
        borderColor: "rgba(245, 240, 222, 0.6)",
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.parsed.y} wins`,
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "#f5f0de", font: { size: 11 }, maxRotation: 45 },
        grid: { color: "rgba(245,240,222,0.05)" },
      },
      y: {
        title: {
          display: true,
          text: "Wins out of 10,000",
          color: "#f5f0de",
        },
        ticks: { color: "#f5f0de" },
        grid: { color: "rgba(245,240,222,0.05)" },
      },
    },
  };

  return (
    <div className="w-full max-w-3xl mx-auto mt-6">
      <Bar data={data} options={options} />
    </div>
  );
}
