export default function MatchupRunButton({ runMatchup, isLoading, bothSelected }) {
  return (
    <div>
      <button
        className={`ui-panel ui-text rounded-full px-6 py-3 ${bothSelected ? "cursor-pointer" : "cursor-not-allowed opacity-40"}`}
        onClick={runMatchup}
        disabled={isLoading || !bothSelected}
      >
        {isLoading ? "Running..." : "Run Matchup"}
      </button>
    </div>
  );
}
