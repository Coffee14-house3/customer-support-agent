export interface RetrievedDocument {
  kb_id: string;
  intent: string;
  category: string;
  title: string;
  policy_summary: string;
  resolution_procedure: string;
  example_queries?: string[];
  similarity_score: number;
}

export interface TicketTriage {
  sentiment: "Positive" | "Neutral" | "Frustrated" | "Urgent";
  urgency: "P1 - Critical" | "P2 - High" | "P3 - Medium" | "P4 - Low";
  suggested_action: "Auto-Resolved via RAG" | "Escalate to Human Agent" | "Clarification Needed" | "Security Flag";
  agent_summary: string;
  draft_agent_reply: string;
}

export interface BaselineComparison {
  intent: string;
  similarity: number;
  response: string;
  matched_via: string;
  verdict: "RAG Outperforms" | "Parity";
}

export interface AgentResponse {
  query: string;
  cleaned_query: string;
  answer: string;
  status:
    | "grounded_response"
    | "clarification_requested"
    | "abstain_out_of_domain"
    | "abstain_unsupported_facts"
    | "adversarial_rejected"
    | "invalid_empty_query";
  confidence_level: "HIGH" | "MEDIUM" | "CLARIFICATION_NEEDED" | "LOW" | "REJECT";
  confidence_score: number;
  predicted_intent: string;
  retrieved_documents: RetrievedDocument[];
  grounded: boolean;
  abstention: boolean;
  reason?: string;
  execution_time_ms?: number;
  ticket_triage?: TicketTriage;
  baseline_comparison?: BaselineComparison;
}

export interface GoldenSetCase {
  id: string;
  category: string;
  query: string;
  expected_intent?: string;
  expected_answer?: string;
  required_facts?: string[];
  key_facts_required?: string[];
  acceptable_behavior?: "answer" | "clarify" | "abstain" | string;
  expected_behavior?: "answer" | "clarify" | "abstain" | string;
  difficulty?: string;
  notes?: string;
}

export interface MetricsSummary {
  baseline_test_metrics: {
    model: string;
    test_sample_count: number;
    accuracy: number;
    macro_f1: number;
    recall_at_1: number;
    recall_at_3: number;
    mrr: number;
  };
  agent_test_metrics: {
    model: string;
    test_sample_count: number;
    accuracy: number;
    macro_f1: number;
    recall_at_1: number;
    recall_at_3: number;
    mrr: number;
  };
  golden_set_reliability: number;
  category_breakdown: Record<
    string,
    {
      total: number;
      success: number;
      failures: Array<{
        id: string;
        query: string;
        expected_behavior: string;
        agent_status: string;
        agent_answer: string;
        judge_reason: string;
      }>;
      success_rate: number;
    }
  >;
  llm_judge_summary: {
    correctness: number;
    relevance: number;
    groundedness: number;
    completeness: number;
    helpfulness: number;
    overall_score: number;
    hallucination_rate: number;
  };
  sample_evaluations: Array<{
    id: string;
    category: string;
    query: string;
    acceptable_behavior: string;
    agent_status: string;
    agent_answer: string;
    success: boolean;
    judge_reason: string;
  }>;
}
