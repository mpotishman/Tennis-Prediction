import React from "react";

export default function MatchupRunButton({runMatchup , isLoading}) {
  return (
    <div>
      <button onClick={runMatchup} disabled={isLoading}>
        {isLoading ? "Running..." : "Run Tournament"}
      </button>
    </div>
  );
}