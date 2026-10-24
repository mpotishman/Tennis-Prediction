// Use the project Python environment instead of whichever python3 Next happens to inherit.

import { existsSync } from "node:fs";
import path from "node:path";


export function getPythonExecutable() {
  if (process.env.PYTHON_BIN) {
    return process.env.PYTHON_BIN;
  }

  const candidates = [
    path.join(process.cwd(), ".venv", "bin", "python"),
    path.join(process.cwd(), "venv", "bin", "python"),
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
  ];

  return candidates.find((candidate) => existsSync(candidate)) ?? "python3";
}
