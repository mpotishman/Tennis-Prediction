export default function SimulationResult({ resultText, error }) {
  if (!resultText && !error) {
    return null;
  }

  return (
    <div className="mt-6 text-center">
      {resultText ? (
        <p className="text-balance font-serif text-xl text-stone-50">
          {resultText}
        </p>
      ) : null}
      {error ? <p className="mt-2 text-sm text-rose-200">{error}</p> : null}
    </div>
  );
}
