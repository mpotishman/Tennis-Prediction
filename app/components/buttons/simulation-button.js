"use client";

import { useState } from "react";

import styles from "./simulation-button.module.css";

export default function SimulationButtons({ children, onClick, fetchPath }) {
  const [winner, setWinner] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleClick() {
    // The parent owns the content below, so tell it which view to show first.
    if (onClick) {
      onClick();
    }

    setIsLoading(true);
    setError("");
    setWinner("");

    try {
      const response = await fetch(fetchPath, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Simulation failed");
      }

      const data = await response.json();
      setWinner(data.winner);
    } catch {
      setError("Could not run simulation right now.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={`${styles.panel} flex flex-col items-center gap-4`}>
      <button
        className={`${styles.button} rounded-full px-6 py-3 text-sm font-semibold uppercase tracking-[0.18em] transition`}
        disabled={isLoading}
        onClick={handleClick}
        type="button"
      >
        {isLoading ? "Running..." : children}
      </button>
      {winner ? <p className={styles.result}>{winner}</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}
    </div>
  );
}
