import { GOLDEN_SET_DATA } from "../server/embeddedData";

export default function handler(req: any, res: any) {
  res.setHeader("Content-Type", "application/json");
  return res.status(200).json(GOLDEN_SET_DATA);
}
