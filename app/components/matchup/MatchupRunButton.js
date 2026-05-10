// MATCHUP RUN BUTTON — triggers the head-to-head matchup prediction.
// Receives runMatchup (the fetch function from MatchupPanel) and isLoading.
// Disabled and shows "Running..." while the API call is in progress.

import React from "react";

export default function MatchupRunButton({ runMatchup, isLoading }) {
  return (
    <div>
      <button className="ui-panel ui-text rounded-full px-6 py-3" onClick={runMatchup} disabled={isLoading}>
        {isLoading ? "Running..." : "Run Matchup"}
      </button>
    </div>
  );
}
