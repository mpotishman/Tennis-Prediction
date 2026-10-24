// Node's child-process module lets this server route run the Python simulator.
import { execFile } from "node:child_process";
// execFile normally uses callbacks; promisify lets us await its result.
import { promisify } from "node:util";
// Select the project virtual environment's Python executable when available.
import { getPythonExecutable } from "@/app/lib/python";

const execFileAsync = promisify(execFile);

// This route needs Node.js APIs such as child_process, so it cannot use the
// more restricted Next.js Edge runtime.
export const runtime = "nodejs";
// Always run the route when requested instead of caching a previous simulation.
export const dynamic = "force-dynamic";

// Handle POST requests sent to /api/simulation.
export async function POST(request) {
  try {
    // Read the JSON body sent by TournamentPanel. Use XGBoost when the caller
    // does not explicitly select another model.
    const {
      modelType = "xgboost",
      featuresSelected,
      tournamentSelected,
    } = await request.json();

    // Reject an invalid request before starting the relatively expensive
    // Python process. HTTP 400 means the client supplied bad input.
    if (!Array.isArray(featuresSelected) || featuresSelected.length === 0) {
      return Response.json(
        { error: "Select at least one feature before running the simulation." },
        { status: 400 },
      );
    }

    // A tournament is also required by web_simulation.py.
    if (!tournamentSelected) {
      return Response.json(
        { error: "Select a tournament before running the simulation." },
        { status: 400 },
      );
    }

    // Start Python and wait for it to finish. Each array item after the script
    // path becomes a command-line argument received by web_simulation.py.
    const { stdout } = await execFileAsync(
      getPythonExecutable(),
      [
        "src/scripts/web_simulation.py",
        modelType,
        JSON.stringify(featuresSelected),
        JSON.stringify(tournamentSelected),
      ],
      {
        // Run from the project root so Python can resolve data and source paths.
        cwd: process.cwd(),
        // Tournament simulations can return a large JSON bracket.
        maxBuffer: 1024 * 1024 * 10,
        // Stop a simulation that runs for longer than two minutes.
        timeout: 120000,
      },
    );

    // The Python script prints JSON to stdout. Convert that text into a
    // JavaScript value and return it to the browser as an HTTP JSON response.
    const result = JSON.parse(stdout.trim());
    return Response.json(result);
  } catch (error) {
    // Prefer Python's stderr because it usually contains the useful traceback.
    // Fall back to the JavaScript error or a generic message.
    const message =
      error.stderr?.trim() ||
      error.message ||
      "Simulation failed.";
    // HTTP 500 indicates that processing failed on the server.
    return Response.json({ error: message }, { status: 500 });
  }
}
