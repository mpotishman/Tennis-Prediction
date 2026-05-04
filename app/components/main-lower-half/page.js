"use client";

import React, { useState } from "react";
import SimulationButtons from "../buttons/simulation-button";
import SimulateTournamentContent from "../content/simulate_tournament_content";
import SimulateMatchupContent from "../content/simulate_matchup_content";

export default function LowerHalfPage() {
  const [simType, setSimType] = useState(1);
  // This state decides which content component is shown below the buttons.
  const content =
    simType === 1 ? <SimulateTournamentContent /> : <SimulateMatchupContent />;


  return (
    <>
      <div className="flex gap-2 justify-center p-4">
        <SimulationButtons
          fetchPath="/api/simulation"
          onClick={() => setSimType(1)}
         >
          Run Simulation
        </SimulationButtons>
        <SimulationButtons

          onClick={() => setSimType(2)}
        >
          Simulate Matchup
        </SimulationButtons>

      </div>
      <div>{content}</div>
    </>
  );
}
