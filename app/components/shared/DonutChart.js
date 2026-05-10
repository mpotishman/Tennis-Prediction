"use client";
import React from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip } from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";
ChartJS.register(ArcElement, Tooltip, ChartDataLabels);

export default function DonutChart({
  player1,
  player2,
  player1Pct,
  player2Pct,
}) {
  if (!player1Pct || !player2Pct) return null;
  const data = {
    labels: [player1, player2],
    datasets: [
      {
        data: [player1Pct, player2Pct],
        backgroundColor: ["#dcb24d", "rgba(245,240,222,0.1)"],
        borderWidth: 0,
        weight: 1,
      },
      {
        data: [100],
        backgroundColor: ["rgba(245,240,222,0.05)"],
        borderWidth: 0,
        weight: 0.4,
        datalabels: { display: false },
      },
    ],
  };

  const options = {
    circumference: 180,
    rotation: -90,
    cutout: "70%",
    layout: {
      padding: { left: 80, right: 80, top: 40 },
    },
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
      datalabels: {
        color: "#f5f0de",
        anchor: "end",
        align: "end",
        formatter: (value, ctx) => {
          const label = ctx.chart.data.labels[ctx.dataIndex];
          return `${label}\n${Math.round(value * 10) / 10}%`;
        },
        font: { size: 11, weight: "bold" },
      },
    },
  };

  return <Doughnut data={data} options={options} />;
}
