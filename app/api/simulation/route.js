import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  try {
    const { modelType = "xgboost", featuresSelected, tournamentSelected} = await request.json();

    const { stdout } = await execFileAsync("python3", ["src/scripts/web_simulation.py", modelType, JSON.stringify(featuresSelected), JSON.stringify(tournamentSelected)], {
      cwd: process.cwd(),
      maxBuffer: 1024 * 1024 * 10,
      timeout: 120000,
    });

    const result = JSON.parse(stdout.trim());
    return Response.json(result);
  } catch (error) {
    const message = error.stderr?.trim() || "Simulation failed.";
    return Response.json({ error: message }, { status: 500 });
  }
}
