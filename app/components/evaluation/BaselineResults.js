// Keep the headline comparison compact enough to scan before the yearly detail.

function formatMetric(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }

  return Number(value).toFixed(digits);
}

export default function BaselineResults({ rows }) {
  if (!rows?.length) {
    return null;
  }

  return (
    <section className="ui-panel w-full overflow-hidden rounded-2xl border border-stone-50/10 text-left text-stone-50">
      <div className="border-b border-stone-50/10 px-6 py-5">
        <h2 className="text-xl font-semibold">Simple Baseline Comparison</h2>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-[#f5f0de]/60">
          Every method starts with the same held-out future matches. The
          higher-ranked rule excludes matches with missing or tied rankings and
          only reports accuracy because hard 0% and 100% probabilities are not
          meaningful probability forecasts.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse">
          <thead className="bg-black/10 text-xs uppercase tracking-[0.12em] text-[#f5f0de]/50">
            <tr>
              <th className="px-6 py-4 font-medium">Method</th>
              <th className="px-4 py-4 text-right font-medium">Matches</th>
              <th className="px-4 py-4 text-right font-medium">Coverage</th>
              <th className="px-4 py-4 text-right font-medium">Accuracy</th>
              <th className="px-4 py-4 text-right font-medium">Log loss</th>
              <th className="px-6 py-4 text-right font-medium">Brier score</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                className={
                  row.method === "full_xgboost"
                    ? "border-t border-emerald-300/20 bg-emerald-400/10 text-sm font-semibold"
                    : "border-t border-stone-50/10 text-sm"
                }
                key={row.method}
              >
                <td className="px-6 py-4 font-medium">{row.label}</td>
                <td className="px-4 py-4 text-right tabular-nums">
                  {row.num_matches.toLocaleString()}
                </td>
                <td className="px-4 py-4 text-right tabular-nums">
                  {(row.coverage * 100).toFixed(1)}%
                </td>
                <td className="px-4 py-4 text-right tabular-nums">
                  {(row.accuracy * 100).toFixed(2)}%
                </td>
                <td className="px-4 py-4 text-right tabular-nums">
                  {formatMetric(row.log_loss)}
                </td>
                <td className="px-6 py-4 text-right tabular-nums">
                  {formatMetric(row.brier_score)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
