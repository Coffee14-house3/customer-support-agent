import React, { useState, useEffect } from "react";
import { FileText, AlertTriangle, ShieldCheck, Download, Copy, Check } from "lucide-react";

export const ReportsTab: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<"eval" | "failure">("eval");
  const [evalText, setEvalText] = useState<string>("");
  const [failureText, setFailureText] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch("/api/reports/evaluation").then((r) => (r.ok ? r.text() : "")),
      fetch("/api/reports/failure").then((r) => (r.ok ? r.text() : "")),
    ])
      .then(([evalDoc, failDoc]) => {
        setEvalText(evalDoc);
        setFailureText(failDoc);
      })
      .catch((err) => console.error("Error loading reports:", err))
      .finally(() => setLoading(false));
  }, []);

  const currentContent = activeSubTab === "eval" ? evalText : failureText;

  const handleCopy = () => {
    navigator.clipboard.writeText(currentContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-500">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent mb-4"></div>
        <p>Loading audit reports...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">System Reliability & Failure Analysis</h2>
          <p className="text-sm text-slate-500">
            Formal audit logs, failure taxonomy, root cause analysis, and production deployment checklist
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
          >
            {copied ? <Check className="w-3.5 h-3.5 mr-1 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
            {copied ? "Copied" : "Copy Markdown"}
          </button>
        </div>
      </div>

      <div className="flex space-x-2 border-b border-slate-200">
        <button
          onClick={() => setActiveSubTab("eval")}
          className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
            activeSubTab === "eval"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          <FileText className="w-4 h-4 inline mr-1.5" />
          Evaluation Report (`reports/evaluation_report.md`)
        </button>
        <button
          onClick={() => setActiveSubTab("failure")}
          className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
            activeSubTab === "failure"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          <AlertTriangle className="w-4 h-4 inline mr-1.5" />
          Failure Analysis Report (`reports/failure_analysis.md`)
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 overflow-x-auto">
        <pre className="text-xs font-mono text-slate-800 whitespace-pre-wrap leading-relaxed">
          {currentContent || "Report content not available."}
        </pre>
      </div>
    </div>
  );
};
