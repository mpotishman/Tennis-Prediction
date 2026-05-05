import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  try {
    const { player1, player2, modelType = "xgboost", featuresSelected } = await request.json();

    const { stdout } = await execFileAsync("python3", [
      "src/web_matchup.py",
      player1,
      player2,
      modelType,
      JSON.stringify(featuresSelected),
    ], {
      cwd: process.cwd(),
      maxBuffer: 1024 * 1024 * 10,
      timeout: 120000,
    });

    const result = JSON.parse(stdout.trim());
    return Response.json(result);
  } catch (error) {
    const message = error.stderr?.trim() || "Matchup simulation failed.";
    return Response.json({ error: message }, { status: 500 });
  }
}