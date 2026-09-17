import { KNOWLEDGE_BASE_DATA } from "../server/embeddedData.ts";

export default function handler(req: any, res: any) {
  res.setHeader("Content-Type", "application/json");
  return res.status(200).json(KNOWLEDGE_BASE_DATA);
}
