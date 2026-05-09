// FEATURE GROUP — renders one category of feature checkboxes (e.g. "Serve Performance").
// Receives a single category name, its features object { featureKey: "Label" },
// the current selectedFeatures array, and the setter from TournamentPanel.
//
// Checking a box adds the feature key to selectedFeatures.
// Unchecking removes it. The array is what gets sent to the API on run.
// Rendered four times in TournamentPanel — once per category in FEATURE_MAPPING.

"use client";
import React from "react";

export default function FeatureGroup({
  category,
  features,
  selectedFeatures,
  setSelectedFeatures,
}) {
  return (
    <div className="ui-panel rounded-xl p-4 text-left">
      <p className="ui-text border-b border-[#f5f0de]/30 pb-2 mb-2">
        {category}
      </p>
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
