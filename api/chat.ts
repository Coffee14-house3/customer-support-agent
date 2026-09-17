import { TypeScriptSupportAgent } from "../server/agentEngine.ts";
import { KNOWLEDGE_BASE_DATA } from "../server/embeddedData.ts";

let agent: TypeScriptSupportAgent | null = null;
function getAgent(): TypeScriptSupportAgent {
  if (!agent) {
    agent = new TypeScriptSupportAgent(KNOWLEDGE_BASE_DATA);
  }
  return agent;
}

export default async function handler(req: any, res: any) {
  res.setHeader("Content-Type", "application/json");

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method Not Allowed" });
  }

  try {
    let body = req.body;
    if (typeof body === "string") {
      try {
        body = JSON.parse(body);
      } catch (e) {
        body = {};
      }
    }
    body = body || {};

    const query = body.query;
    if (!query || typeof query !== "string") {
      return res.status(400).json({ error: "A valid 'query' string is required." });
    }

    const ag = getAgent();
    const result = await ag.processQuery(query);
    return res.status(200).json(result);
  } catch (err: any) {
    console.error("Vercel api/chat error:", err);
    return res.status(500).json({ error: err.message || "Failed to process query." });
  }
}
