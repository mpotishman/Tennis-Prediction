// TAB BUTTON — the top-level navigation buttons ("Simulate Tournament" / "Simulate Matchup").
// Receives onClick (switches simType in page.js), isActive (highlights the selected tab),
// and isLoading (disables the button while a simulation is running).
// Styled via TabButton.module.css which provides the glass-effect background.

"use client";

import styles from "./TabButton.module.css";

export default function SimulationButtons({
  children,
  onClick,
  isActive,
  isLoading,
}) {
  return (
    <div className={styles.panel}>
      <button
        className={`${styles.button} rounded-full px-6 py-3 text-sm font-semibold uppercase tracking-[0.18em] transition ${
          isActive ? "border-2 border-stone-50" : "border border-transparent"
        }`}
        disabled={isLoading}
        onClick={onClick}
        type="button"
      >
        {isLoading ? "Running..." : children}
      </button>
    </div>
  );
}
