import { existsSync, statSync } from "node:fs";
import path from "node:path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const dataPath =
    process.env.TENNIS_DATA_PATH ??
    path.join(process.cwd(), "data", "processed", "combined.csv");
  const dataReady = existsSync(dataPath) && statSync(dataPath).size > 0;

  return Response.json(
    { status: dataReady ? "ready" : "starting", dataReady },
    { status: dataReady ? 200 : 503 },
  );
}
