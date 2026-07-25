"use client";

import { useEffect, useState } from "react";
import EvaluationResults from "./EvaluationResults";
import LineChart from "../charts/LineChart";

export default function ModelEvaluationPanel() {
  const [backtestData, setBacktestData] = useState(null);
  const [error, setError] = useState("");
  const [statData, setStatData] = useState(null);

  const [openDropdown, setOpenDropdown] = useState("2025");

  // if press currently opened year set it equla to none so nothing shows up
  function handleClick(year) {
    setOpenDropdown((currentYear) => (currentYear === year ? null : year));
  }

  useEffect(() => {
    fetch("/api/backtest")
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setBacktestData(data.summary);
          setStatData(data.statData);
        }
      })
      .catch(() => {
        setError("Could not load backtest data.");
      });
  }, []);

  if (error) {
    return <pre className="w-full text-left text-stone-50">{error}</pre>;
  }

  if (!backtestData || !statData) {
    return (
      <pre className="w-full text-left text-stone-50">
        Loading backtest data...
      </pre>
    );
  }

  const years = statData.map(([year]) => year);

  const accuracyStats = {
    labels: years,
    datasets: [
      {
        label: "Accuracy",
        data: statData.map(([, accuracy]) => accuracy),
      },
    ],
  };

  const logLossStats = {
    labels: years,
    datasets: [
      {
        label: "Log Loss",
        data: statData.map(([, , logLoss]) => logLoss),
      },
    ],
  };

  const brierScoreStats = {
    labels: years,
    datasets: [
      {
        label: "Brier Score",
        data: statData.map(([, , , brierScore]) => brierScore),
      },
    ],
  };

  return (
    <div className="flex flex-col gap-4 justify-center">
      <div className="ui-panel border border-stone-50/10 rounded-2xl px-6 py-3 text-[#f5f0de]/60 text-xs tracking-wide text-center w-full max-w-3xl mx-auto">
        This page shows walk-forward backtest results for the tennis prediction
        model. For each year, the model is trained only on matches from earlier
        years, then tested on matches from that year. Results can be compared
        across different feature sets. Accuracy is the percentage of winners
        predicted correctly, where higher is better. Log Loss evaluates the
        quality and confidence of predicted probabilities, heavily penalising
        confident incorrect predictions, where lower is better. Brier Score
        measures how close the predicted probabilities are to the actual
        outcomes, where lower is better.
      </div>

      {Object.entries(backtestData)
        .reverse()
        .map(([year, stats]) => (
          <EvaluationResults
            key={year}
            year={year}
            stats={stats}
            onClick={handleClick}
            yearOpened={openDropdown}
          />
        ))}

      <LineChart data={statData} />


    </div>
  );
}
