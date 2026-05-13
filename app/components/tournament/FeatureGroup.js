// FEATURE GROUP — renders one category of feature checkboxes (e.g. "Serve Performance").
// Receives a single category name, its features object { featureKey: "Label" },
// the current selectedFeatures array, and the setter from TournamentPanel.
//
// Checking a box adds the feature key to selectedFeatures.
// Unchecking removes it. The array is what gets sent to the API on run.
// Rendered four times in TournamentPanel — once per category in FEATURE_MAPPING.

"use client";
import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleQuestion } from "@fortawesome/free-solid-svg-icons";

export default function FeatureGroup({
  category,
  features,
  selectedFeatures,
  setSelectedFeatures,
}) {
  const [showExplanation, setShowExplanation] = useState(false);

  const descriptions = {
    "Match Context": "Factors about the structure of the match itself.",
    "Surface Conditions":
      "How the court surface and player rest affects the outcome.",
    "Rankings and Form":
      "How the players compare in skill, ranking and recent form.",
    "Serve Performance": "How effective each player is on their serve.",
  };

  return (
    <div className="ui-panel rounded-xl p-4 text-left">
      <div className="flex w-full justify-between">
        <p className="ui-text border-b border-[#f5f0de]/30 pb-2 mb-2">
          {category}
        </p>
        <div className="relative">
          <div
            className="flex items-center justify-center w-5 h-5 rounded-full border border-[#f5f0de]/30 text-[#f5f0de]/40 hover:border-[#dcb24d] hover:text-[#dcb24d] transition-colors cursor-pointer text-[10px]"
            onMouseEnter={() => setShowExplanation(true)}
            onMouseLeave={() => setShowExplanation(false)}
          >
            ?
          </div>
          {showExplanation && (
            <div className="ui-panel bg-[#0a1f1c] absolute left-1/2 bottom-full mb-3 -translate-x-1/2 z-10 w-72 rounded-xl border border-stone-50/10 p-4 ui-text normal-case tracking-normal font-normal text-xs leading-relaxed before:content-[''] before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-8 before:border-transparent before:border-t-[#0a1f1c]">
              {descriptions[category]}
            </div>
          )}
        </div>
      </div>

      {Object.entries(features).map(([feature, label]) => (
        <label key={feature} className="ui-text flex items-center gap-2">
          <input
            type="checkbox"
            checked={selectedFeatures.includes(feature)}
            onChange={() =>
              setSelectedFeatures((prev) =>
                prev.includes(feature)
                  ? prev.filter((f) => f !== feature)
                  : [...prev, feature],
              )
            }
          />
          {label}
        </label>
      ))}
    </div>
  );
}
