"use client";

function formatMatchTime(match) {
  const espnDetail = match.status?.type?.detail;

  if (
    !match.date ||
    match.timeValid === false ||
    espnDetail?.includes("TBD")
  ) {
    return "Time TBD";
  }

  const date = new Date(match.date);

  if (Number.isNaN(date.getTime())) {
    return "Invalid date";
  }

  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    day: "numeric",
    month: "long",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);
}

export default function MatchDisplay({
  match,
  prediction = null,
  isPredictionLoading = false,
  predictionError = "",
  completed = false,
}) {
  const player1 =
    match.competitors?.[0]?.athlete?.displayName ?? "TBD";
  const player2 =
    match.competitors?.[1]?.athlete?.displayName ?? "TBD";
  const date = formatMatchTime(match);

  return (
    <div className="ui-panel grid grid-cols-1 gap-3 p-4 ui-text md:grid-cols-[280px_1px_minmax(0,1fr)_1px_200px] md:items-center md:gap-0">
      <div className="flex p-4">{date}</div>

      <div
        aria-hidden="true"
        className="hidden h-10 bg-stone-200 md:block"
      />

      <div className="text-left md:pl-12">
        <span className="text-xl font-bold">{player1}</span>
        <span className="mx-2 text-sm">vs</span>
        <span className="text-xl font-bold">{player2}</span>
      </div>

      <div
        aria-hidden="true"
        className="hidden h-10 bg-stone-200 md:block"
      />

      <div className="md:pl-6">
        {completed ? (
          <p className="text-sm">
            {match.notes?.[0]?.text ??
              match.status?.type?.detail ??
              "Final"}
          </p>
        ) : (
          <>
            {isPredictionLoading && <p>Predicting...</p>}

            {!isPredictionLoading && predictionError && (
              <p className="text-sm text-red-300">
                Prediction unavailable
              </p>
            )}

            {!isPredictionLoading && prediction && (
              <div>
                <p className="font-bold">
                  {prediction.player1Probability}% /{" "}
                  {prediction.player2Probability}%
                </p>

                <p className="text-xs">
                  {prediction.player1Probability >
                  prediction.player2Probability
                    ? player1
                    : player2}{" "}
                  predicted
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
