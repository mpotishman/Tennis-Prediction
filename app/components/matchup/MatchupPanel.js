// MATCHUP PANEL — shown when the "Simulate Matchup" tab is active.
// Receives selectedModel, selectedFeatures and their setters from page.js.
// Fetches the full player list from /api/players on mount and stores it locally.
// Owns its own player1, player2, result/error/loading state.
//
// User flow: search and select two players → press Run → see win probability
// On run: POSTs { player1, player2, modelType, featuresSelected } to /api/matchup
//         which calls web_matchup.py and returns { winner, loser, winPct, modelLabel }
//
// Child components:
//   PlayerDropdown  — searchable dropdown, calls onSelect when a player is chosen
//   MatchupRunButton — triggers runMatchup()
//   SimulationResult — displays the result or error text

"use client";
import React from "react";
import { useState, useEffect } from "react";

import SimulationResult from "../shared/SimulationResult";
import PlayerDropdown from "./PlayerDropdown";
import MatchupRunButton from "./MatchupRunButton";

export default function MatchupPanel({
  selectedModel,
  setSelectedModel,
  selectedFeatures,
  setSelectedFeatures,
  featureMapping,
}) {
  const [players, setPlayers] = useState([]);
  const [player1, setPlayer1] = useState("");
  const [player2, setPlayer2] = useState("");

  const [resultText, setResultText] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // make the function to call to api/matchup
  async function runMatchup() {
    setIsLoading(true);
    setError("");
    setResultText("");

    try {
      const response = await fetch("/api/matchup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player1,
          player2,
          modelType: selectedModel,
          featuresSelected: selectedFeatures,
        }),
      });

      const data = await response.json();
      setResultText(
        `${data.modelLabel} suggests ${data.winner} wins ${data.winPct}% of the time against ${data.loser}!`,
      );
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetch("/api/players")
      .then((r) => r.json())
      .then(setPlayers);
  }, []);

  return (
    <div className="text-center">
      <div className="flex items-center gap-6 justify-center">
        <PlayerDropdown players={players} onSelect={setPlayer1} />
        <span className="text-stone-50 font-semibold uppercase tracking-[0.18em] text-sm">
          VS
        </span>
        <PlayerDropdown players={players} onSelect={setPlayer2} />
      </div>

      <MatchupRunButton runMatchup={runMatchup} isLoading={isLoading} />
      <SimulationResult resultText={resultText} error={error} />
    </div>
  );
}
