// api/health.ts
function handler(req, res) {
  res.setHeader("Content-Type", "application/json");
  return res.status(200).json({
    status: "ok",
    provider: "vercel-serverless",
    timestamp: (/* @__PURE__ */ new Date()).toISOString()
  });
}
export {
  handler as default
};
