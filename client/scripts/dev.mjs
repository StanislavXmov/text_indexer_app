import { spawn } from "node:child_process";

const host = process.env.HOST || "0.0.0.0";

const child = spawn("vite", ["--host", host], {
  stdio: "inherit",
  shell: true,
});

child.on("exit", (code) => {
  process.exit(code ?? 0);
});
