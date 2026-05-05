"use client";

import React, { useState } from "react";
import SimulationButtons from "../buttons/simulation-button";
import SimulateTournamentContent from "../content/simulate_tournament_content/simulate_tournament_content";
import SimulateMatchupContent from "../content/simulate_matchup_content/simulate_matchup_content";

const FEATURE_MAPPING = {
  elo_gap: "Elo Gap",
  tourney_k_value: "Tournament Weight",
  best_of: "Best Of",
  surface: "Surface",
  tourney_level: "Tournament Level",
  round: "Round",
  winrate_gap: "Recent Win Rate Gap",
  surface_elo_gap: "Surface Elo Gap",
  rank_gap: "Ranking Gap",
  rank_points_gap: "Ranking Points Gap",
  days_rest_gap: "Rest Days Gap",
  hold_rate_gap: "Hold Rate Gap",
  first_srv_win_rate_gap: "1st Serve Win Gap",
  second_srv_win_rate_gap: "2nd Serve Win Gap",
};

export default function LowerHalfPage() {
  const [simType, setSimType] = useState(1);
  const [selectedModel, setSelectedModel] = useState("xgboost");
  const [selectedFeatures, setSelectedFeatures] = useState(
    Object.keys(FEATURE_MAPPING),
  );

  const content =
    simType === 1 ? (
      <SimulateTournamentContent
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        selectedFeatures={selectedFeatures}
        setSelectedFeatures={setSelectedFeatures}
        featureMapping={FEATURE_MAPPING}
      />
    ) : (
      <SimulateMatchupContent
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        selectedFeatures={selectedFeatures}
        setSelectedFeatures={setSelectedFeatures}
        featureMapping={FEATURE_MAPPING}
      />
    );

  return (
    <>
      <div className="flex gap-2 justify-center p-4">
        <SimulationButtons
          onClick={() => setSimType(1)}
          isActive={simType === 1}
        >
          Simulate Tournament
        </SimulationButtons>
        <SimulationButtons
          onClick={() => setSimType(2)}
          isActive={simType === 2}
        >
          Simulate Matchup
        </SimulationButtons>
      </div>
      <div>{content}</div>
    </>
  );
}
