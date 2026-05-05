"use client";
import React, { useState } from "react";
import SimulationResult from "../simulation-result";
import TournamentRunButton from "./tournament_run_button";

export default function SimulateTournamentContent({
  selectedModel,
  setSelectedModel,
  selectedFeatures,
  setSelectedFeatures,
  featureMapping,
}) {
  const [resultText, setResultText] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function runSimulation() {
    setIsLoading(true);
    setError("");
    setResultText("");

    try {
      const response = await fetch("/api/simulation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ modelType: selectedModel, featuresSelected: selectedFeatures }),
      });

      const data = await response.json();
      setResultText(`${data.modelLabel} suggests ${data.winner} to win ${data.winPct}% of the time!`);
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center">
      <div className="flex gap-4">
        <label>
          <input
            type="radio"
            name="model"
            checked={selectedModel === "xgboost"}
            onChange={() => setSelectedModel("xgboost")}
          />
          XGBoost
        </label>

        <label>
          <input
            type="radio"
            name="model"
            checked={selectedModel === "random_forest"}
            onChange={() => setSelectedModel("random_forest")}
          />
          Random Forest
        </label>

        <label>
          <input
            type="radio"
            name="model"
            checked={selectedModel === "logistic"}
            onChange={() => setSelectedModel("logistic")}
          />
          Logistic Regression
        </label>
      </div>

      {/* loop through each feature.  */}
      {Object.entries(featureMapping).map(([feature, label]) => (
        <label key={feature}>
          <input
            type="checkbox"
            name="features"
            // set checked to true IF its in the selected features
            checked={selectedFeatures.includes(feature)}
            // on change, read the previous state of setSelectedFeatures, if feature already selected - remove it, else add it by copying whole array and adding new feature
            onChange={() =>
              setSelectedFeatures((prev) =>
                prev.includes(feature)
                  ? prev.filter((f) => f !== feature)
                  : [...prev, feature],
              )
            }
          />
          {label}
        </label>
      ))}
      <TournamentRunButton runSimulation={runSimulation} isLoading={isLoading} />
      <SimulationResult resultText={resultText} error={error} />
    </div>
  );
}
