import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { getPythonExecutable } from "@/app/lib/python";

const execFileAsync = promisify(execFile);

export const runtime = "nodejs";

export async function GET() {
  try {
    // Returns each player's actual recorded career range.
    const { stdout } = await execFileAsync(
      getPythonExecutable(),
      [
        "-c",
        `
import pandas as pd, json
df = pd.read_csv("data/processed/combined.csv")
df["year"] = df["tourney_date"].str[:4].astype(int)
ranges = df.groupby("player_name")["year"].agg(["min", "max"])
result = {
    player: {"minYear": int(row["min"]), "maxYear": int(row["max"])}
    for player, row in ranges.iterrows()
}
print(json.dumps(result))
      `,
      ],
      { cwd: process.cwd() },
    );

    return Response.json(JSON.parse(stdout.trim()));
  } catch (e) {
    return Response.json([], { status: 500 });
  }
}
