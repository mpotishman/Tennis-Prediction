// SIMULATION RESULT — shared display component used by both TournamentPanel and MatchupPanel.
// Renders nothing if both resultText and error are empty.
// Shows resultText (the prediction) in serif font, or error in rose if something went wrong.

export default function SimulationResult({ resultText, error }) {
  if (!resultText && !error) {
    return null;
  }

  return (
    <div className="text-center">
      {resultText ? (
        <p className="text-balance font-serif text-xl text-stone-50">
          {resultText}
        </p>
      ) : null}
      {error ? <p className="mt-2 text-sm text-rose-200">{error}</p> : null}
    </div>
  );
}
