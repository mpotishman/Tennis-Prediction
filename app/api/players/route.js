import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export const runtime = "nodejs";

export async function GET() {
  try {
    // returns eg { "Roger Federer": 2000, "Carlos Alcaraz": 2020, ... }
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        `
import pandas as pd, json
df = pd.read_csv("data/processed/combined.csv")
df["year"] = df["tourney_date"].str[:4].astype(int)
p1 = df.groupby("player_name")["year"].min()
p2 = df.groupby("opponent_name")["year"].min()
combined = pd.concat([p1, p2]).groupby(level=0).min()
print(json.dumps(combined.to_dict()))
      `,
      ],
      { cwd: process.cwd() },
    );

    return Response.json(JSON.parse(stdout.trim()));
  } catch (e) {
    return Response.json([], { status: 500 });
  }
}
