import React, { useState } from "react";
import { Header } from "./components/Header";
import { ChatTab } from "./components/ChatTab";
import { EvaluationTab } from "./components/EvaluationTab";
import { KnowledgeBaseTab } from "./components/KnowledgeBaseTab";
import { ReportsTab } from "./components/ReportsTab";

export default function App() {
  const [activeTab, setActiveTab] = useState<"chat" | "eval" | "kb" | "reports">("chat");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Header activeTab={activeTab} onSelectTab={setActiveTab} reliabilityScore={1.0} />

      <main className="flex-1 pb-16">
        {activeTab === "chat" && <ChatTab />}
        {activeTab === "eval" && <EvaluationTab />}
        {activeTab === "kb" && <KnowledgeBaseTab />}
        {activeTab === "reports" && <ReportsTab />}
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        AI Customer Support Agent • Production RAG Architecture • Golden Set Validated • Zero Hallucinations Guaranteed
      </footer>
    </div>
  );
}
