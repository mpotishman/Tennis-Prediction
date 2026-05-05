"use client";

import styles from "./simulation-button.module.css";

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
