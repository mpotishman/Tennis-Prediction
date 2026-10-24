"use client";
import { useEffect, useMemo, useState } from "react";
import MatchDisplay from "./MatchDisplay";

const MATCHUP_FEATURES = [
  "tourney_k_value",
  "tourney_level",
  "best_of",
  "round",
  "surface",
  "surface_elo_gap",
  "days_rest_gap",
  "elo_gap",
  "rank_gap",
  "rank_points_gap",
  "winrate_gap",
  "h2h_gap",
  "hold_rate_gap",
  "first_srv_win_rate_gap",
  "second_srv_win_rate_gap",
];

export default function TodaysPanel({
  error,
  setError,
  matches,
  setMatches,
  predictionsByMatchId,
  setPredictionsByMatchId,
}) {
  const [isLoading, setIsLoading] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionError, setPredictionError] = useState("");

  // Fetch today's matches automatically whenever this panel is mounted.
  useEffect(() => {
    const today = new Date();

    getMatches(
      today.getDate(),
      today.getMonth() + 1,
      today.getFullYear(),
    );
  }, []);

  const upcomingMatches = useMemo(
    () =>
      matches.filter(
        (match) => match.status?.type?.state === "pre",
      ),
    [matches],
  );

  const completedMatches = useMemo(
    () =>
      matches.filter(
        (match) => match.status?.type?.state === "post",
      ),
    [matches],
  );

  // Predict every upcoming match in one backend request. The Python batch
  // script loads/trains the model once and reuses it for every pairing. Results
  // live in page.js, so switching tabs does not discard and recalculate them.
  useEffect(() => {
    if (upcomingMatches.length === 0) {
      setPredictionError("");
      setIsPredicting(false);
      return;
    }

    const matchesWithoutPredictions = upcomingMatches.filter(
      (match) => !predictionsByMatchId[String(match.id)],
    );

    if (matchesWithoutPredictions.length === 0) {
      setPredictionError("");
      setIsPredicting(false);
      return;
    }

    let ignoreResult = false;

    async function getBatchPredictions() {
      setIsPredicting(true);
      setPredictionError("");

      try {
        const matchups = matchesWithoutPredictions.map((match) => ({
          matchId: String(match.id),
          player1:
            match.competitors?.[0]?.athlete?.displayName,
          player2:
            match.competitors?.[1]?.athlete?.displayName,
        }));

        const response = await fetch("/api/matchups/batch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            matchups,
            modelType: "xgboost",
            featuresSelected: MATCHUP_FEATURES,
            yearEnd: 2026,
          }),
        });

        const data = await response.json();

        if (!response.ok || data.error) {
          throw new Error(data.error || "Could not predict today’s matches.");
        }

        if (!ignoreResult) {
          setPredictionsByMatchId((currentPredictions) => ({
            ...currentPredictions,
            ...Object.fromEntries(
              data.predictions.map((prediction) => [
                String(prediction.matchId),
                prediction,
              ]),
            ),
          }));
        }
      } catch (batchError) {
        if (!ignoreResult) {
          setPredictionError(
            batchError.message || "Could not predict today’s matches.",
          );
        }
      } finally {
        if (!ignoreResult) {
          setIsPredicting(false);
        }
      }
    }

    getBatchPredictions();

    return () => {
      ignoreResult = true;
    };
  }, [upcomingMatches]);

  // function to fetch match data
  async function getMatches(day, month, year) {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/todays-matches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ day, month, year }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || "Could not fetch today’s matches.");
      }

      const mensMatches = (data.events ?? []).flatMap((event) =>
        (event.groupings ?? []).flatMap((group) => {
          if (group.grouping?.displayName !== "Men's Singles") {
            return [];
          }

          return (group.competitions ?? [])
            .filter((match) => {
              const player1 =
                match.competitors?.[0]?.athlete?.displayName;
              const player2 =
                match.competitors?.[1]?.athlete?.displayName;

              return (
                player1 &&
                player2 &&
                player1 !== "TBD" &&
                player2 !== "TBD"
              );
            })
            .map((match) => ({
              ...match,
              tournamentName: event.name,
              matchType: group.grouping.displayName,
            }));
        }),
      );

      setMatches(mensMatches);
    } catch (fetchError) {
      setError(
        fetchError.message || "Could not fetch today’s matches.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex w-full flex-col gap-8 ">
      {error && <p>{error}</p>}

      <section className="flex flex-col gap-4">
        <div className="text-left p-4 ui-text text-3xl"><h2>Upcoming Matches</h2></div>

        {isLoading && upcomingMatches.length === 0 && (
          <p>Loading today&apos;s matches...</p>
        )}

        {!isLoading && !error && upcomingMatches.length === 0 && (
          <p>No upcoming men&apos;s singles matches found today.</p>
        )}

        {predictionError && (
          <p className="text-sm text-red-300">{predictionError}</p>
        )}

        {upcomingMatches.map((match) => (
          <MatchDisplay
            key={match.id}
            match={match}
            prediction={
              predictionsByMatchId[String(match.id)] ?? null
            }
            isPredictionLoading={
              isPredicting &&
              !predictionsByMatchId[String(match.id)]
            }
            predictionError={predictionError}
          />
        ))}
      </section>

      {completedMatches.length > 0 && (
        <section className="flex flex-col gap-4">
          <div className="text-left p-4 ui-text text-3xl">
            <h2>Completed Matches</h2>
          </div>
          

          {completedMatches.map((match) => (
            <MatchDisplay
              key={match.id}
              match={match}
              completed
            />
          ))}
        </section>
      )}
    </div>
  );
}
