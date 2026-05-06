// TOURNAMENT PANEL — shown when the "Simulate Tournament" tab is active.
// Receives selectedModel, selectedFeatures and their setters from page.js.
// Owns its own result/error/loading state since the API call lives here.
//
// User flow: pick a model → toggle features → press Run Tournament
// On run: POSTs { modelType, featuresSelected } to /api/simulation
//         which calls web_simulation.py and returns { winner, winPct, modelLabel }
//
// Child components:
//   FeatureGroup      — renders one category of feature checkboxes
//   TournamentRunButton — triggers runSimulation()
//   SimulationResult  — displays the result or error text

"use client";
import React, { useState } from "react";
import SimulationResult from "../shared/SimulationResult";
import TournamentRunButton from "./TournamentRunButton";
import FeatureGroup from "./FeatureGroup";
import ModelSelector from "./ModelSelector";

export default function TournamentPanel({
  selectedModel,
  setSelectedModel,
  selectedFeatures,
  setSelectedFeatures,
  featureMapping,
}) {
  const [resultText, setResultText] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  //  check to see if all are selected if it matches the length of all the features
  const allSelected =
    selectedFeatures.length ===
    Object.values(featureMapping).flatMap(Object.keys).length;

  // function to change the features one all selected is changed
  function handleSelectAll() {
    if (allSelected) {
      setSelectedFeatures([]);
    } else {
      setSelectedFeatures(Object.values(featureMapping).flatMap(Object.keys));
    }
  }

  async function runSimulation() {
    setError("");
    setResultText("");

    // make sure more than one feature is selected
    if (selectedFeatures.length === 0) {
      setError("Please select at least one feature.");
      return;
    } else {
      setIsLoading(true);
    }

    try {
      const response = await fetch("/api/simulation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          modelType: selectedModel,
          featuresSelected: selectedFeatures,
        }),
      });

      const data = await response.json();
      setResultText(
        Object.entries(data.results)
          .map(([player, count]) => `${player}: ${count}`)
          .join(", "),
      );
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col justify-center">
      {/* model selector div */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-1 mx-auto">
        <ModelSelector
          value="xgboost"
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        >
          XGBoost
        </ModelSelector>
        <ModelSelector
          value="random_forest"
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        >
          Random Forest
        </ModelSelector>
        <ModelSelector
          value="logistic"
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        >
          Logistic Regression
        </ModelSelector>
      </div>

      {/* feature selection div */}
      <div className="flex flex-col">
        {/* Select features heading */}
        <div className="flex justify-between p-4">
          <div>
            <h2 className="ui-text cursor-pointer">Select features</h2>
          </div>
          <div>
            <button
              className="ui-text rounded-full border border-transparent cursor-pointer"
              onClick={handleSelectAll}
            >
              {allSelected ? "Deselect All" : "Select All"}
            </button>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-4  ">
          {Object.entries(featureMapping).map(([category, features]) => (
            <FeatureGroup
              key={category}
              category={category}
              features={features}
              selectedFeatures={selectedFeatures}
              setSelectedFeatures={setSelectedFeatures}
            />
          ))}
        </div>
      </div>

      <div className="p-4">
        <TournamentRunButton
          runSimulation={runSimulation}
          isLoading={isLoading}
        />
      </div>

      <SimulationResult resultText={resultText} error={error} />
    </div>
  );
}
