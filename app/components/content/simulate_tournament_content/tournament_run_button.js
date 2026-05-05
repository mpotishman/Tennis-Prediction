import React from "react";

export default function TournamentRunButton({runSimulation, isLoading}) {
  return (
    <div>
      <button onClick={runSimulation} disabled={isLoading}>
        {isLoading ? "Running..." : "Run Tournament"}
      </button>
    </div>
  );
}
