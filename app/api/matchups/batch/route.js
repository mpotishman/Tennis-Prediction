import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { getPythonExecutable } from "@/app/lib/python";

const execFileAsync = promisify(execFile);

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  try {
    const {
      matchups,
      modelType = "xgboost",
      featuresSelected,
      yearEnd = 2026,
    } = await request.json();

    if (!Array.isArray(matchups) || matchups.length === 0) {
      return Response.json(
        { error: "At least one matchup is required." },
        { status: 400 },
      );
    }

    if (matchups.length > 200) {
      return Response.json(
        { error: "A maximum of 200 matchups can be predicted at once." },
        { status: 400 },
      );
    }

    const invalidMatchup = matchups.some(
      (matchup) =>
        matchup.matchId == null ||
        typeof matchup.player1 !== "string" ||
        typeof matchup.player2 !== "string" ||
        !matchup.player1.trim() ||
        !matchup.player2.trim(),
    );

    if (invalidMatchup) {
      return Response.json(
        { error: "Every matchup requires a match ID and two player names." },
        { status: 400 },
      );
    }

    if (
      !Array.isArray(featuresSelected) ||
      featuresSelected.length === 0
    ) {
      return Response.json(
        { error: "At least one model feature is required." },
        { status: 400 },
      );
    }

    const { stdout } = await execFileAsync(
      getPythonExecutable(),
      [
        "src/scripts/web_matchups_batch.py",
        JSON.stringify(matchups),
        modelType,
        JSON.stringify(featuresSelected),
        String(yearEnd),
      ],
      {
        cwd: process.cwd(),
        maxBuffer: 1024 * 1024 * 10,
        // The first request may train and save the model. Later requests load it.
        timeout: 180000,
      },
    );

    return Response.json(JSON.parse(stdout.trim()));
  } catch (error) {
    const message =
      error.stderr?.trim() ||
      error.message ||
      "Batch matchup prediction failed.";
    return Response.json({ error: message }, { status: 500 });
  }
}
