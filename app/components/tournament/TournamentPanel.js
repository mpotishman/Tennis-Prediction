// TOURNAMENT PANEL — shown when the "Simulate Tournament" tab is active.
// Receives selectedModel, selectedFeatures and their setters from page.js.
// Result state (resultText, error, results, predictedBracket) is also received
// from page.js so it persists when switching between tabs.
//
// User flow: pick a model → toggle features → press Run Tournament
// On run: POSTs { modelType, featuresSelected } to /api/simulation
//         which calls src/scripts/web_simulation.py and returns { winner, winPct, modelLabel }
//
// Child components:
//   FeatureGroup      — renders one category of feature checkboxes
//   TournamentRunButton — triggers runSimulation()
//   SimulationResult  — displays the result or error text

"use client";
import React, { useState, useEffect, useRef } from "react";
import SimulationResult from "../shared/SimulationResult";
import TournamentRunButton from "./TournamentRunButton";
import FeatureGroup from "./FeatureGroup";
import ModelSelector from "./ModelSelector";
import TournamentChart from "./TournamentChart";
import BracketDisplay from "./BracketDisplay";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleQuestion } from "@fortawesome/free-solid-svg-icons";
const tournaments = [
  "2026 Wimbledon",
  "2026 Australian Open",
  "2026 Roland Garros",
  "2025 Australian Open",
  "2025 Roland Garros",
  "2025 Wimbledon",
  "2025 US Open",
  "2024 Australian Open",
  "2024 Roland Garros",
  "2024 Wimbledon",
  "2024 US Open",
  "2023 Australian Open",
  "2023 Roland Garros",
  "2023 Wimbledon",
  "2023 US Open",
  "2022 Australian Open",
  "2022 Roland Garros",
  "2022 Wimbledon",
  "2022 US Open",
  "2021 Australian Open",
  "2021 Roland Garros",
  "2021 Wimbledon",
  "2021 US Open",
  "2020 Australian Open",
  "2020 Roland Garros",
  "2020 US Open",
];

export default function TournamentPanel({
  selectedModel,
  setSelectedModel,
  selectedFeatures,
  setSelectedFeatures,
  selectedTournament,
  setSelectedTournament,
  featureMapping,
  // Result state lifted to page.js so it persists across tab switches
  resultText,
  setResultText,
  error,
  setError,
  results,
  setResults,
  predictedBracket,
  setPredictedBracket,
  badMatchups,
  setBadMatchups,
}) {
  // Local-only UI state — does not need to persist across tab switches
  const [isLoading, setIsLoading] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [open, setOpen] = useState(false);

  const containerRef = useRef(null);

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

  const noneSelected = selectedFeatures.length === 0;

  useEffect(() => {
    if (!resultText) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [resultText]);

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
          tournamentSelected: selectedTournament,
        }),
      });

      const data = await response.json();
      setResults(data.results);
      setResultText(
        `${data.modelLabel} suggests ${data.winner} wins the ${data.tournament} ${data.winPct}% of the time!`,
      );
      // Python sends this as snake_case `bad_matchups` (see web_simulation.py)
      console.log("Raw bad matchups:", data.bad_matchups);
      setBadMatchups(data.bad_matchups ?? null);
      setPredictedBracket(data.predicted_bracket);
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  // close when clicking outside the component
  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-col justify-center">
      <div ref={containerRef} className="flex justify-center">
        <div className="relative">
          <input
            className="rounded-full px-4 py-2 text-sm font-semibold uppercase tracking-widest bg-transparent border border-stone-50/40 text-stone-50 placeholder:text-stone-400 focus:outline-none focus:border-stone-50"
            value={selectedTournament}
            onChange={(e) => {
              setSelectedTournament(e.target.value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            placeholder="Select Tournament"
          />

          {open && (
            <ul className="absolute z-10 w-full mt-2 rounded-xl border border-stone-50/20 bg-stone-900/90 backdrop-blur-sm max-h-48 overflow-y-auto">
              {tournaments.map((tournament) => (
                <li
                  key={tournament}
                  className="px-4 py-2 cursor-pointer hover:bg-stone-700 text-stone-50 text-sm uppercase tracking-widest"
                  onClick={() => {
                    setSelectedTournament(tournament);
                    setOpen(false);
                  }}
                >
                  {tournament}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
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
          value="logistic"
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        >
          Logistic Regression
        </ModelSelector>
        <ModelSelector
          value="random_forest"
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
        >
          Random Forest
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
          noneSelected={noneSelected}
        />
      </div>

      {resultText && (
        <div>
          <div className="flex relative mt-6 justify-center gap-4 items-center">
            <div className="fade-in-down" style={{ animationDelay: "0s" }}>
              <SimulationResult resultText={resultText} error={error} />
            </div>
          </div>

          <div className="fade-in-down" style={{ animationDelay: "0.2s" }}>
            <TournamentChart results={results} />
          </div>

          <div
            className="fade-in-down flex flex-col p-4 mt-8 text-stone-50 w-full"
            style={{ animationDelay: "0.4s" }}
          >
            {predictedBracket && (
              <>
                <div className="flex justify-center gap-16 items-center">
                  <div className="text-balance font-serif text-xl">
                    Most common bracket matchups over the 1,000 simulations:
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
  ui-panel bg-[#0a1f1c] absolute left-1/2 bottom-full mb-3 -translate-x-1/2 z-10
  w-72 rounded-xl border border-stone-50/10 p-4
  ui-text normal-case tracking-normal font-normal text-xs leading-relaxed
  before:content-[''] before:absolute before:top-full before:left-1/2
  before:-translate-x-1/2 before:border-8 before:border-transparent
  before:border-t-[#0a1f1c]"
                      >
                        <p className="m-0">
                          The percentage is how likely each player goes through.
                          Later rounds don&apos;t add up to 100% due to potential
                          upsets in other simulations.
                        </p>
                        {Array.isArray(badMatchups) &&
                          badMatchups.length > 0 && (
                            <>
                              <p className="mt-3 mb-1 font-semibold">
                                First-round matchups where at least one player has no data:
                              </p>
                              <ul className="m-0 pl-4">
                                {badMatchups.map((m, i) => (
                                  <li key={i} className="mb-1 text-[11px]">
                                    <strong>{m.player}</strong> vs {m.opponent}
                                    {m.player_missing &&
                                      " [missing player data]"}
                                    {m.opponent_missing &&
                                      " [missing opponent data]"}
                                  </li>
                                ))}
                                <p className="mt-3 mb-1 font-semibold">
                                  Players with no prior data have a 25% chance of advancing. If both players have no prior data, the winner is decided by a coin toss.
                                </p>
                              </ul>
                            </>
                          )}
                      </div>
                    )}
                  </div>
                </div>
                <BracketDisplay bracketInformation={predictedBracket} />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
