import { readFile } from "node:fs/promises";
import path from "node:path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const SUMMARY_FILE = path.join(
  process.cwd(),
  "outputs",
  "backtests",
  "feature_sets",
  "summary_metrics.csv",
);

const FEATURE_SET_ORDER = [
  "full",
  "elo_only",
  "surface_elo_only",
  "ranking_only",
  "elo_surface",
  "form_only",
  "serve_only",
];

function parseSummaryCsv(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  const headers = lines[0].split(",");

  return lines.slice(1).map((line) => {
    const values = line.split(",");
    const row = Object.fromEntries(
      headers.map((header, index) => [header, values[index]]),
    );

    return {
      feature_set: row.feature_set,
      model_type: row.model_type,
      test_year: Number(row.test_year),
      num_matches: Number(row.num_matches),
      accuracy: Number(row.accuracy),
      log_loss: Number(row.log_loss),
      brier_score: Number(row.brier_score),
    };
  });
}

export async function GET() {
  try {
    const csvText = await readFile(SUMMARY_FILE, "utf8");

    const summary = parseSummaryCsv(csvText);

    const {
      grouped,
      statData,
    } = groupByYearAndFeatureSet(summary);

    return Response.json({
      source: "outputs/backtests/feature_sets/summary_metrics.csv",
      summary: grouped,
      statData: statData,
    });
  } catch (error) {
    return Response.json(
      { error: "Could not load backtest summary metrics." },
      { status: 500 },
    );
  }
}

function groupByYearAndFeatureSet(data) {
  const groupedDict = {};

  data.forEach((row) => {
    const year = row.test_year;
    const featureSet = row.feature_set;

    if (!groupedDict[year]) {
      groupedDict[year] = {};
    }

    groupedDict[year][featureSet] = {
      Accuracy: row.accuracy,
      "Log Loss": row.log_loss,
      "Brier Score": row.brier_score,
      "Number of Matches": row.num_matches,
      "Model Type": row.model_type,
    };
  });

  const statData = [];

  const years = Object.keys(groupedDict).sort(
    (yearA, yearB) => Number(yearA) - Number(yearB),
  );

  years.forEach((year) => {
    const currentFeatureSets = groupedDict[year];
    const fullStats = currentFeatureSets.full;

    if (fullStats) {
      statData.push([
        Number(year),
        fullStats.Accuracy,
        fullStats["Log Loss"],
        fullStats["Brier Score"],
      ]);
    }

    groupedDict[year] = Object.fromEntries(
      FEATURE_SET_ORDER
        .filter((featureSet) => currentFeatureSets[featureSet])
        .map((featureSet) => [
          featureSet,
          currentFeatureSets[featureSet],
        ]),
    );
  });

  return {
    grouped: groupedDict,
    statData: statData,
  };
}