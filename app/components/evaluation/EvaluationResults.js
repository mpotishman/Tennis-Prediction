import React from "react";
import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { faAngleDown } from "@fortawesome/free-solid-svg-icons";

export default function EvaluationResults({
  year,
  stats,
  onClick,
  yearOpened,
}) {
  const FEATURE_MAP = {
    full: "All Features",
    elo_only: "Overall Elo",
    surface_elo_only: "Surface Elo",
    ranking_only: "Rankings",
    elo_surface: "Overall + Surface Elo",
    form_only: "Recent Form",
    serve_only: "Serve Statistics",
  };

  const { full, ...otherFeatureSets } = stats;

  return (
    <>
      <div
        className={`flex ui-panel p-4 rounded-2xl transition-all duration-300 ${
          yearOpened === year ? "min-h-40" : "h-20"
        }`}
      >
        <div className="flex w-16 shrink-0 items-center tracking-tight text-white font-bold text-2xl tabular-nums ">
          {year}
        </div>

        <div className="self-stretch border-l border-stone-200 mx-4" />

        <div className="flex flex-1 flex-col text-white ui-text">
          <div className="flex w-full items-center">
            <div className="w-32 shrink-0">{FEATURE_MAP["full"]}</div>

            <div className="h-10 border-l border-stone-200 mx-4" />

            <div className="flex gap-4">
              <div>Accuracy: {(full.Accuracy * 100).toFixed(2)}%</div>
              <div>Log Loss: {full["Log Loss"].toFixed(2)}</div>
              <div>Brier Score: {full["Brier Score"].toFixed(2)}</div>
            </div>

            <button
              type="button"
              className="ml-auto cursor-pointer"
              onClick={() => onClick(year)}
            >
              <FontAwesomeIcon
                icon={yearOpened === year ? faAngleDown : faAngleRight}
              />
            </button>
          </div>

          {yearOpened === year && (
            <div className="mt-4 flex flex-col gap-3">
              {Object.entries(otherFeatureSets).map(([featureSet, stat]) => (
                <div key={featureSet} className="flex items-center">
                  <div className="w-32 shrink-0">{FEATURE_MAP[featureSet]}</div>

                  <div className="h-10 border-l border-stone-200 mx-4" />

                  <div className="flex gap-4">
                    <div>Accuracy: {(stat.Accuracy * 100).toFixed(2)}%</div>
                    <div>Log Loss: {stat["Log Loss"].toFixed(2)}</div>
                    <div>Brier Score: {stat["Brier Score"].toFixed(2)}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
