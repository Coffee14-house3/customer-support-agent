import React from "react";
import { Bot, ShieldCheck, CheckCircle2, BarChart2, BookOpen, FileText, MessageSquare } from "lucide-react";

interface HeaderProps {
  activeTab: "chat" | "eval" | "kb" | "reports";
  onSelectTab: (tab: "chat" | "eval" | "kb" | "reports") => void;
  reliabilityScore?: number;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onSelectTab, reliabilityScore = 0.955 }) => {
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-20 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-xs">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-semibold text-slate-900 tracking-tight">Customer Support AI Agent</h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <ShieldCheck className="w-3 h-3 mr-1" />
                  RAG Grounded
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Grounded Retrieval • Hallucination Defense • Golden Set Validated ({(reliabilityScore * 100).toFixed(1)}% Reliability)
              </p>
            </div>
          </div>

          <nav className="flex space-x-1 sm:space-x-2">
            <button
              id="tab-btn-chat"
              onClick={() => onSelectTab("chat")}
              className={`inline-flex items-center px-3 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                activeTab === "chat"
                  ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-1.5" />
              Live Agent
            </button>
            <button
              id="tab-btn-eval"
              onClick={() => onSelectTab("eval")}
              className={`inline-flex items-center px-3 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                activeTab === "eval"
                  ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <BarChart2 className="w-4 h-4 mr-1.5" />
              Evaluation Benchmark
            </button>
            <button
              id="tab-btn-kb"
              onClick={() => onSelectTab("kb")}
              className={`inline-flex items-center px-3 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                activeTab === "kb"
                  ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <BookOpen className="w-4 h-4 mr-1.5" />
              Knowledge Base
            </button>
            <button
              id="tab-btn-reports"
              onClick={() => onSelectTab("reports")}
              className={`inline-flex items-center px-3 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                activeTab === "reports"
                  ? "bg-indigo-50 text-indigo-700 border border-indigo-200"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <FileText className="w-4 h-4 mr-1.5" />
              Audit Reports
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
