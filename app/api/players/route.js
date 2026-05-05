import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export const runtime = "nodejs";

export async function GET() {
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        `
import pandas as pd, json
df = pd.read_csv("data/processed/combined.csv")
names = sorted(set(df["player_name"].dropna()) | set(df["opponent_name"].dropna()))
print(json.dumps(names))
      `,
      ],
      { cwd: process.cwd() },
    );

    return Response.json(JSON.parse(stdout.trim()));
  } catch (e) {
    return Response.json([], { status: 500 });
  }
}
