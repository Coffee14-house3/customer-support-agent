import React, { useState, useEffect } from "react";
import { BookOpen, Search, Tag, CheckCircle2, ChevronDown, ChevronRight } from "lucide-react";
import { RetrievedDocument } from "../types";
import { KNOWLEDGE_BASE_DATA } from "../../server/embeddedData";

export const KnowledgeBaseTab: React.FC = () => {
  const [kbDocs, setKbDocs] = useState<RetrievedDocument[]>(KNOWLEDGE_BASE_DATA as any);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(KNOWLEDGE_BASE_DATA?.[0]?.kb_id || null);

  useEffect(() => {
    fetch("/api/knowledge-base")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setKbDocs(data);
        }
      })
      .catch((err) => console.error("Failed to fetch fresh KB:", err));
  }, []);

  const filteredDocs = (Array.isArray(kbDocs) ? kbDocs : []).filter((d) => {
    const q = searchQuery.toLowerCase();
    return (
      (d.title || "").toLowerCase().includes(q) ||
      (d.category || "").toLowerCase().includes(q) ||
      (d.policy_summary || "").toLowerCase().includes(q) ||
      (d.resolution_procedure || "").toLowerCase().includes(q)
    );
  });

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-500">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent mb-4"></div>
        <p>Loading support knowledge base policies...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Support Policy Knowledge Base</h2>
          <p className="text-sm text-slate-500">
            Official operational policies and resolution procedures extracted from training data ({kbDocs.length} topics)
          </p>
        </div>

        <div className="relative w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search policies or procedures..."
            className="w-full text-xs pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="space-y-3">
        {filteredDocs.map((doc) => {
          const isExpanded = expandedId === doc.kb_id;

          return (
            <div
              key={doc.kb_id}
              className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden transition-all"
            >
              <button
                onClick={() => setExpandedId(isExpanded ? null : doc.kb_id)}
                className="w-full text-left px-5 py-4 flex items-center justify-between hover:bg-slate-50/80 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-indigo-600" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400" />
                  )}
                  <div>
                    <span className="font-semibold text-slate-900 text-sm mr-2">{doc.title}</span>
                    <span className="inline-flex items-center text-xs font-medium text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                      <Tag className="w-3 h-3 mr-1" />
                      {doc.category}
                    </span>
                  </div>
                </div>

                <span className="font-mono text-xs text-slate-400">{doc.kb_id}</span>
              </button>

              {isExpanded && (
                <div className="px-5 pb-5 pt-2 border-t border-slate-100 bg-slate-50/50 space-y-4">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Official Policy Summary
                    </h4>
                    <p className="text-sm text-slate-800 leading-relaxed bg-white p-3 rounded-lg border border-slate-200">
                      {doc.policy_summary}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                      Standard Resolution Procedure
                    </h4>
                    <p className="text-sm text-slate-700 leading-relaxed bg-white p-3 rounded-lg border border-slate-200">
                      {doc.resolution_procedure}
                    </p>
                  </div>

                  {doc.example_queries && doc.example_queries.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                        Representative Query Variations
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {doc.example_queries.map((eq, i) => (
                          <span
                            key={i}
                            className="text-xs text-slate-600 bg-white px-2.5 py-1 rounded-md border border-slate-200"
                          >
                            "{eq}"
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
