"use client";
import React from "react";
import { useState, useEffect, useRef } from "react";

import SimulationResult from "../shared/SimulationResult";
import PlayerDropdown from "./PlayerDropdown";
import MatchupRunButton from "./MatchupRunButton";
import MatchupChart from "./MatchupChart";

const TOP_PLAYERS = [
  "Jannik Sinner",
  "Carlos Alcaraz",
  "Alexander Zverev",
  "Novak Djokovic",
  "Daniil Medvedev",
  "Casper Ruud",
  "Taylor Fritz",
  "Andrey Rublev",
  "Tommy Paul",
  "Holger Rune",
  "Grigor Dimitrov",
  "Stefanos Tsitsipas",
  "Ben Shelton",
  "Alex De Minaur",
  "Hubert Hurkacz",
];

const LEGENDS = [
  "Roger Federer",
  "Rafael Nadal",
  "Andy Murray",
  "Pete Sampras",
  "Andre Agassi",
  "Ivan Lendl",
  "Boris Becker",
  "Stefan Edberg",
  "John McEnroe",
  "Jimmy Connors",
  "Bjorn Borg",
];

function sortPlayers(players) {
  return [...players].sort((a, b) => {
    const aTop = TOP_PLAYERS.indexOf(a);
    const bTop = TOP_PLAYERS.indexOf(b);
    const aLegend = LEGENDS.indexOf(a);
    const bLegend = LEGENDS.indexOf(b);

    if (aTop !== -1 && bTop !== -1) return aTop - bTop;
    if (aTop !== -1) return -1;
    if (bTop !== -1) return 1;
    if (aLegend !== -1 && bLegend !== -1) return aLegend - bLegend;
    if (aLegend !== -1) return -1;
    if (bLegend !== -1) return 1;
    return a.localeCompare(b);
  });
}

export default function MatchupPanel({
  selectedModel,
  setSelectedModel,
  selectedFeatures,
  setSelectedFeatures,
  featureMapping,
  // Result state lifted to page.js so it persists across tab switches
  resultText,
  setResultText,
  error,
  setError,
  player1winPct,
  setPlayer1winPct,
  player2winPct,
  setPlayer2winPct,
  ran,
  setRan,
  chartPlayer1,
  setChartPlayer1,
  chartPlayer2,
  setChartPlayer2,
  // Player selections and year sliders lifted to page.js to persist across tab switches
  player1,
  setPlayer1,
  player2,
  setPlayer2,
  player1YearStart,
  setPlayer1YearStart,
  player2YearStart,
  setPlayer2YearStart,
}) {
  // Local-only state — player list does not need to persist (re-fetched on mount)
  const [players, setPlayers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const bothSelected = player1 && player2;

  const [playerYears, setPlayerYears] = useState({});

  // Size the chart from the visible space below the prediction sentence.
  const resultRef = useRef(null);
  const [chartHeight, setChartHeight] = useState(320);

  // make the function to call to api/matchup
  async function runMatchup() {
    setIsLoading(true);
    setError("");
    setResultText("");

    try {
      const response = await fetch("/api/matchup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player1,
          player2,
          modelType: selectedModel,
          // Matchup has no feature selector, so always use the full feature set —
          // never the tournament tab's selection (which may exclude the gap
          // features that distinguish players and collapse results to 50/50).
          featuresSelected: Object.values(featureMapping).flatMap(Object.keys),
          p1year_end: player1YearStart,
          p2year_end: player2YearStart,
        }),
      });

      const data = await response.json();
      setRan(true);
      // Commit chart player names only on run, not on dropdown change
      setChartPlayer1(player1);
      setChartPlayer2(player2);
      setResultText(
        `${data.modelLabel} suggests ${data.player_1_year} ${data.player_1} wins ${data.player_1_prob}% of the time against ${data.player_2_year} ${data.player_2}!`,
      );
      setPlayer1winPct(data.player_1_prob);
      setPlayer2winPct(data.player_2_prob);
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetch("/api/players")
      .then((r) => r.json())
      .then((data) => {
        setPlayerYears(data);
        setPlayers(sortPlayers(Object.keys(data)));
      });
  }, []);

  useEffect(() => {
    const range = playerYears[player1];
    if (range) {
      setPlayer1YearStart((year) =>
        Math.min(Math.max(year, range.minYear), range.maxYear),
      );
    }
  }, [player1, playerYears, setPlayer1YearStart]);

  useEffect(() => {
    const range = playerYears[player2];
    if (range) {
      setPlayer2YearStart((year) =>
        Math.min(Math.max(year, range.minYear), range.maxYear),
      );
    }
  }, [player2, playerYears, setPlayer2YearStart]);

  useEffect(() => {
    if (!ran || !resultRef.current) return;

    function updateChartHeight() {
      const resultBottom = resultRef.current.getBoundingClientRect().bottom;
      const remainingHeight = Math.max(window.innerHeight - resultBottom, 0);

      // Use 75% of the visible area below the result, while retaining a useful
      // minimum on short screens and preventing an enormous chart on tall ones.
      setChartHeight(
        Math.max(220, Math.min(680, Math.round(remainingHeight * 0.75))),
      );
    }

    updateChartHeight();
    window.addEventListener("resize", updateChartHeight);

    const observer = new ResizeObserver(updateChartHeight);
    observer.observe(resultRef.current);

    return () => {
      window.removeEventListener("resize", updateChartHeight);
      observer.disconnect();
    };
  }, [ran, resultText]);

  return (
    <div className="flex w-full flex-col items-center gap-2 overflow-x-hidden">
      <div className="ui-panel border border-stone-50/10 rounded-full px-6 py-2 text-[#f5f0de]/60 text-xs tracking-wide italic text-center max-w-xl">
        Note: This simulation uses the latest available data for each player.
        Choosing a retired player will use stats from their last recorded match.
        All predictions are done using XgBoost with all features selected.
      </div>
      <div className="flex flex-col md:flex-row items-center gap-6 justify-center">
        <div className="flex flex-col gap-4">
          <PlayerDropdown
            players={players}
            value={player1}
            onSelect={(p) => {
              setPlayer1(p);
              setPlayer1YearStart(playerYears[p]?.maxYear ?? 2026);
            }}
          />
          {player1 && (
            <>
              <input
                type="range"
                min={playerYears[player1]?.minYear}
                max={playerYears[player1]?.maxYear}
                value={player1YearStart}
                onChange={(e) => setPlayer1YearStart(Number(e.target.value))}
                className="w-full accent-[#dcb24d] cursor-pointer opacity-70 hover:opacity-100 transition-opacity"
              />
              <span className="text-[#dcb24d] text-xs font-bold uppercase tracking-widest text-center w-full block">
                {player1YearStart}
              </span>
            </>
          )}
        </div>

        <span className="text-stone-50 font-semibold uppercase tracking-[0.18em] text-sm">
          VS
        </span>
        <div className="flex flex-col gap-4">
          <PlayerDropdown
            players={players}
            value={player2}
            onSelect={(p) => {
              setPlayer2(p);
              setPlayer2YearStart(playerYears[p]?.maxYear ?? 2026);
            }}
          />
          {player2 && (
            <>
              <input
                type="range"
                min={playerYears[player2]?.minYear}
                max={playerYears[player2]?.maxYear}
                value={player2YearStart}
                onChange={(e) => setPlayer2YearStart(Number(e.target.value))}
                className="w-full accent-[#dcb24d] cursor-pointer opacity-70 hover:opacity-100 transition-opacity"
              />
              <span className="text-[#dcb24d] text-xs font-bold uppercase tracking-widest text-center w-full block">
                {player2YearStart}
              </span>
            </>
          )}
        </div>
      </div>

      <div className="">
        <MatchupRunButton runMatchup={runMatchup} isLoading={isLoading} bothSelected={bothSelected} />
      </div>

      <div ref={resultRef}>
        <SimulationResult resultText={resultText} error={error} />
      </div>

      {ran && (
        <div className="mt-4 flex w-full justify-center pointer-events-none">
          <div
            style={{
              height: `${chartHeight}px`,
              width: `min(100%, ${Math.round(chartHeight * 2.2)}px)`,
            }}
          >
            <MatchupChart
              player1={chartPlayer1}
              player2={chartPlayer2}
              player1winPct={player1winPct}
              player2winPct={player2winPct}
            />
          </div>
        </div>
      )}
    </div>
  );
}
