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
import TournamentChart from "./TournamentChart";
import BracketDisplay from "./BracketDisplay";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleQuestion } from "@fortawesome/free-solid-svg-icons";

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
  const [results, setResults] = useState(null);
  const [predictedBracket, setPredictedBracket] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);

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
      setResults(data.results);
      setResultText(
        `${data.modelLabel} suggests ${data.winner} to win ${data.winPct}% of the time!`,
      );
      setPredictedBracket(data.predicted_bracket);
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-col justify-center">
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
      <div className="mx-auto flex w-full max-w-6xl flex-col">
        {/* Select features heading */}
        <div className="flex items-center justify-between gap-4 p-4">
          <h2 className="ui-text cursor-pointer">Select features</h2>
          <button
            className="ui-text rounded-full border border-stone-50/15 px-4 py-2 cursor-pointer"
            onClick={handleSelectAll}
          >
            {allSelected ? "Deselect All" : "Select All"}
          </button>
        </div>

        <div className="grid w-full grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
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
      <TournamentChart results={results} />
      <div className="flex flex-col p-4 mt-8  text-stone-50 w-full ">
        <div>
          {/* predictedBracket looks like {round: {match pos: {p1 win percent, p2 win percent}}} - needs three loops to get to bottom stage*/}
          {predictedBracket && (
            <>
              <div className="flex justify-center gap-16 items-center">
                <div className="text-balance font-serif text-xl">
                  Most common bracket matchups over the 10,000 simulations:
                </div>
                <div className="relative">
                  <FontAwesomeIcon
                    icon={faCircleQuestion}
                    onMouseEnter={() => setShowExplanation(true)}
                    onMouseLeave={() => setShowExplanation(false)}
                    className="cursor-pointer"
                  />
                  {showExplanation && (
                    <div
                      className="
      ui-panel absolute left-1/2 bottom-full mb-3 -translate-x-1/2 z-10
      w-72 rounded-xl border border-stone-50/10 p-4
      ui-text normal-case tracking-normal font-normal text-xs leading-relaxed
      before:content-[''] before:absolute before:top-full before:left-1/2
      before:-translate-x-1/2 before:border-8 before:border-transparent
      before:border-t-[rgba(245,240,222,0.1)]
    "
                    >
                      The percentage is how likely each player goes through.
                      Later rounds don&apos;t add up to 100% due to potential upsets
                      in other simulations.
                    </div>
                  )}
                </div>
                
              </div>
              <BracketDisplay bracketInformation={predictedBracket} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
