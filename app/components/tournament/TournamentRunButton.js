// TOURNAMENT RUN BUTTON — triggers the tournament simulation.
// Receives runSimulation (the fetch function from TournamentPanel) and isLoading.
// Disabled and shows "Running..." while the API call is in progress.

import React from "react";

export default function TournamentRunButton({ runSimulation, isLoading }) {
  return (
    <div>
      <button className="ui-panel ui-text rounded-full px-6 py-3" onClick={runSimulation} disabled={isLoading}>
        {isLoading ? "Running..." : "Run Tournament"}
      </button>
    </div>
  );
}
