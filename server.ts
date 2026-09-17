import express from "express";
import path from "path";
import fs from "fs";
import { execFile } from "child_process";
import { promisify } from "util";
import { createServer as createViteServer } from "vite";
import dotenv from "dotenv";
import { TypeScriptSupportAgent } from "./server/agentEngine";
import { KNOWLEDGE_BASE_DATA, METRICS_SUMMARY_DATA, GOLDEN_SET_DATA } from "./server/embeddedData";

dotenv.config();

const execFileAsync = promisify(execFile);
const app = express();
const PORT = 3000;

app.use(express.json());

// In-memory TypeScript Support Agent for sub-millisecond local retrieval & Vercel serverless compatibility
const tsAgent = new TypeScriptSupportAgent(KNOWLEDGE_BASE_DATA);

// API Routes
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Query processing endpoint
app.post("/api/chat", async (req, res) => {
  const { query } = req.body;
  if (!query || typeof query !== "string") {
    return res.status(400).json({ error: "A valid 'query' string is required." });
  }

  // Attempt Python agent execution first if Python runtime is present
  try {
    const scriptPath = path.join(process.cwd(), "scripts", "query_agent.py");
    if (fs.existsSync(scriptPath)) {
      const { stdout } = await execFileAsync(
        "python3",
        [scriptPath, query],
        {
          cwd: process.cwd(),
          env: { ...process.env, PYTHONPATH: process.cwd() },
          timeout: 25000,
        }
      );
      const parsed = JSON.parse(stdout.trim());
      return res.json(parsed);
    }
  } catch (err: any) {
    console.warn("Using native TypeScript Support Agent engine:", err?.message);
  }

  // High-speed native TypeScript Agent engine (Vercel Serverless Ready)
  try {
    const result = await tsAgent.processQuery(query);
    return res.json(result);
  } catch (tsErr: any) {
    console.error("TypeScript agent engine error:", tsErr);
    return res.status(500).json({ error: "Agent execution failed." });
  }
});

// Metrics summary
app.get("/api/metrics", (req, res) => {
  return res.json(METRICS_SUMMARY_DATA);
});

// Knowledge base
app.get("/api/knowledge-base", (req, res) => {
  return res.json(KNOWLEDGE_BASE_DATA);
});

// Golden set
app.get("/api/golden-set", (req, res) => {
  return res.json(GOLDEN_SET_DATA);
});

// Evaluation Report (Markdown)
app.get("/api/reports/evaluation", (req, res) => {
  const repPath = path.join(process.cwd(), "reports", "evaluation_report.md");
  if (fs.existsSync(repPath)) {
    return res.type("text/markdown").send(fs.readFileSync(repPath, "utf-8"));
  }
  return res.status(404).send("Evaluation report not found.");
});

// Failure Analysis Report (Markdown)
app.get("/api/reports/failure", (req, res) => {
  const repPath = path.join(process.cwd(), "reports", "failure_analysis.md");
  if (fs.existsSync(repPath)) {
    return res.type("text/markdown").send(fs.readFileSync(repPath, "utf-8"));
  }
  return res.status(404).send("Failure analysis report not found.");
});

async function startServer() {
  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();

export default app;
