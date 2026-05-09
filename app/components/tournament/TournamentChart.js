import React from "react";
import BarChart from "../shared/BarChart";

export default function TournamentChart({ results }) {
  if (!results) return null;

  // sort by win count descending, take top 15
  const top15 = Object.entries(results)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 15);

  const labels = top15.map(([player]) => player);
  const values = top15.map(([, count]) => count);

  return <BarChart labels={labels} values={values} label="Tournament Wins" />;
}
