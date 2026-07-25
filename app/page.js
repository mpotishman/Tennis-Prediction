// ROOT PAGE — entry point for the entire app.
// Owns all shared state: which tab is active (simType), which model is selected,
// and which features are selected. Both panels receive this state as props so they
// always use the same model and feature choices regardless of which tab is open.
//
// Tournament and Matchup result state is also lifted here so that switching tabs
// does not unmount the panels' results — state persists in the parent.
//
// Data flow:
//   page.js  →  TournamentPanel  →  /api/simulation  →  src/scripts/web_simulation.py
//   page.js  →  MatchupPanel     →  /api/matchup     →  src/scripts/web_matchup.py
//
// Tab switching only swaps the displayed panel — it never triggers an API call.
// API calls are triggered by the Run buttons inside each panel.

"use client";

import React, { useState } from "react";
import TabButton from "./components/shared/TabButton";
import TournamentPanel from "./components/tournament/TournamentPanel";
import MatchupPanel from "./components/matchup/MatchupPanel";
import ModelEvaluationPanel from "./components/evaluation/ModelEvaluationPanel";
import styles from "./page.module.css";

const FEATURE_MAPPING = {
  "Match Context": {
    tourney_k_value: "Tournament Weight",
    tourney_level: "Tournament Level",
    best_of: "Best Of",
    round: "Round",
  },

  "Surface Conditions": {
    surface: "Surface",
    surface_elo_gap: "Surface Elo Gap",
    days_rest_gap: "Rest Days Gap",
  },

  "Rankings and Form": {
    elo_gap: "Elo Gap",
    rank_gap: "Ranking Gap",
    rank_points_gap: "Ranking Points Gap",
    winrate_gap: "Recent Win Rate Gap",
    h2h_gap: "Head-to-Head Gap",
  },

  "Serve Performance": {
    hold_rate_gap: "Hold Rate Gap",
    first_srv_win_rate_gap: "1st Serve Win Gap",
    second_srv_win_rate_gap: "2nd Serve Win Gap",
  },
};

export default function HomePage() {
  const [activeSection, setActiveSection] = useState("predict");
  const [simType, setSimType] = useState(1);
  const [selectedModel, setSelectedModel] = useState("xgboost");
  const [selectedFeatures, setSelectedFeatures] = useState(
    Object.values(FEATURE_MAPPING).flatMap(Object.keys),
  );

  // --- Tournament state lifted from TournamentPanel ---
  // Kept here so results persist when switching to the Matchup tab and back.
  const [tResultText, setTResultText] = useState("");
  const [tError, setTError] = useState("");
  const [tResults, setTResults] = useState(null);
  const [tPredictedBracket, setTPredictedBracket] = useState(null);
  const [selectedTournament, setSelectedTournament] = useState("2026 Australian Open");

  // set the badmatchups state if there is
  const [badMatchups, setBadMatchups] = useState(null);

  // --- Matchup state lifted from MatchupPanel ---
  // Kept here so results persist when switching to the Tournament tab and back.
  const [mResultText, setMResultText] = useState("");
  const [mError, setMError] = useState("");
  const [mPlayer1winPct, setMPlayer1winPct] = useState(0);
  const [mPlayer2winPct, setMPlayer2winPct] = useState(0);
  const [mRan, setMRan] = useState(false);
  const [mChartPlayer1, setMChartPlayer1] = useState("");
  const [mChartPlayer2, setMChartPlayer2] = useState("");
  // Player selections and year sliders — lifted so they survive tab switches
  const [mPlayer1, setMPlayer1] = useState("");
  const [mPlayer2, setMPlayer2] = useState("");
  const [mPlayer1YearStart, setMPlayer1YearStart] = useState(2026);
  const [mPlayer2YearStart, setMPlayer2YearStart] = useState(2026);

  const simulatorContent =
    simType === 1 ? (
      <TournamentPanel
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        selectedFeatures={selectedFeatures}
        setSelectedFeatures={setSelectedFeatures}
        featureMapping={FEATURE_MAPPING}
        resultText={tResultText}
        setResultText={setTResultText}
        error={tError}
        setError={setTError}
        results={tResults}
        setResults={setTResults}
        predictedBracket={tPredictedBracket}
        setPredictedBracket={setTPredictedBracket}
        selectedTournament={selectedTournament}
        setSelectedTournament={setSelectedTournament}
        badMatchups={badMatchups}
        setBadMatchups={setBadMatchups}
      />
    ) : (
      <MatchupPanel
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        selectedFeatures={selectedFeatures}
        setSelectedFeatures={setSelectedFeatures}
        featureMapping={FEATURE_MAPPING}
        resultText={mResultText}
        setResultText={setMResultText}
        error={mError}
        setError={setMError}
        player1winPct={mPlayer1winPct}
        setPlayer1winPct={setMPlayer1winPct}
        player2winPct={mPlayer2winPct}
        setPlayer2winPct={setMPlayer2winPct}
        ran={mRan}
        setRan={setMRan}
        chartPlayer1={mChartPlayer1}
        setChartPlayer1={setMChartPlayer1}
        chartPlayer2={mChartPlayer2}
        setChartPlayer2={setMChartPlayer2}
        player1={mPlayer1}
        setPlayer1={setMPlayer1}
        player2={mPlayer2}
        setPlayer2={setMPlayer2}
        player1YearStart={mPlayer1YearStart}
        setPlayer1YearStart={setMPlayer1YearStart}
        player2YearStart={mPlayer2YearStart}
        setPlayer2YearStart={setMPlayer2YearStart}
      />
    );

  return (
    <main
      className={`${styles.page} flex min-h-screen flex-col items-center justify-start overflow-x-hidden px-6 pt-24`}
    >
      <div aria-hidden="true" className={styles.glow} />
      <div aria-hidden="true" className={styles.frame} />
      <div className="relative z-10 flex w-full max-w-[1400px] flex-col items-center gap-8 pb-16 text-center">
        <nav
          className={styles.siteNav}
          data-active={activeSection}
          aria-label="Primary"
        >
          <span aria-hidden="true" className={styles.siteNavMarker} />
          <button
            aria-current={activeSection === "predict" ? "page" : undefined}
            className={styles.siteNavButton}
            onClick={() => setActiveSection("predict")}
            type="button"
          >
            Predict
          </button>
          <button
            aria-current={activeSection === "evaluation" ? "page" : undefined}
            className={styles.siteNavButton}
            onClick={() => setActiveSection("evaluation")}
            type="button"
          >
            Model Evaluation
          </button>
        </nav>

        <h1
          className={`${styles.title} text-[clamp(3.5rem,10vw,7rem)] font-semibold uppercase leading-[0.92] tracking-[0.16em] text-stone-50 drop-shadow-[0_18px_40px_rgba(6,17,16,0.35)]`}
        >
          Tennis Predictor
        </h1>

        <div className="flex w-full flex-col gap-3">
          {activeSection === "predict" ? (
            <>
              <div className="flex gap-2 justify-center ">
                <TabButton onClick={() => setSimType(1)} isActive={simType === 1}>
                  Simulate Tournament
                </TabButton>
                <TabButton onClick={() => setSimType(2)} isActive={simType === 2}>
                  Simulate Matchup
                </TabButton>
              </div>
              <div className="w-full">{simulatorContent}</div>
            </>
          ) : (
            <ModelEvaluationPanel />
          )}
        </div>
      </div>
    </main>
  );
}
