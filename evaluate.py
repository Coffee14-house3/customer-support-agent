"""
Comprehensive Evaluation Pipeline for the AI Customer Support Agent.
Computes classification, retrieval, LLM-as-a-Judge, and reliability metrics.
Generates publication-quality figures and markdown reports.
"""
import os
import csv
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score

from baseline.tfidf_baseline import TfidfBaseline
from src.agent.support_agent import SupportAgent
from src.evaluation.llm_judge import LLMJudge

REPORTS_DIR = "reports"
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
TEST_CSV = "data/processed/test.csv"
GOLDEN_SET_JSON = "data/golden_set/golden_set.json"
KB_JSON = "data/processed/knowledge_base.json"

def plot_confusion_matrix(y_true, y_pred, labels, output_path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title("Support Intent Classification - Confusion Matrix")
    plt.ylabel("True Intent")
    plt.xlabel("Predicted Intent")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_intent_distribution(train_csv, test_csv, output_path):
    train_counts = {}
    with open(train_csv) as f:
        for r in csv.DictReader(f):
            train_counts[r["intent"]] = train_counts.get(r["intent"], 0) + 1
    test_counts = {}
    with open(test_csv) as f:
        for r in csv.DictReader(f):
            test_counts[r["intent"]] = test_counts.get(r["intent"], 0) + 1

    intents = sorted(list(train_counts.keys()))
    x = np.arange(len(intents))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(x - width/2, [train_counts.get(i, 0) for i in intents], width, label="Train", color="#3b82f6")
    plt.bar(x + width/2, [test_counts.get(i, 0) for i in intents], width, label="Test", color="#10b981")
    plt.xlabel("Intent Class")
    plt.ylabel("Ticket Count")
    plt.title("Stratified Intent Distribution (Train vs Test)")
    plt.xticks(x, intents, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_category_performance(cat_scores, output_path):
    cats = list(cat_scores.keys())
    scores = [cat_scores[c]["success_rate"] * 100 for c in cats]

    plt.figure(figsize=(10, 5))
    colors = ["#10b981" if s >= 80 else "#f59e0b" if s >= 60 else "#ef4444" for s in scores]
    bars = plt.bar(cats, scores, color=colors, width=0.55)
    plt.ylabel("Acceptable Behavior Compliance (%)")
    plt.ylim(0, 105)
    plt.title("Agent Reliability & Robustness across Query Categories")
    plt.xticks(rotation=30, ha="right")
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 2, f"{h:.1f}%", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_baseline_vs_agent(baseline_metrics, agent_metrics, output_path):
    metrics = ["Accuracy", "Macro F1", "Recall@1", "Recall@3", "MRR"]
    base_vals = [
        baseline_metrics["accuracy"],
        baseline_metrics["macro_f1"],
        baseline_metrics["recall_at_1"],
        baseline_metrics["recall_at_3"],
        baseline_metrics["mrr"]
    ]
    agent_vals = [
        agent_metrics["accuracy"],
        agent_metrics["macro_f1"],
        agent_metrics["recall_at_1"],
        agent_metrics["recall_at_3"],
        agent_metrics["mrr"]
    ]

    x = np.arange(len(metrics))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar(x - width/2, [v * 100 for v in base_vals], width, label="TF-IDF Baseline", color="#64748b")
    plt.bar(x + width/2, [v * 100 for v in agent_vals], width, label="AI Support Agent", color="#2563eb")
    plt.ylabel("Score (%)")
    plt.title("Performance Comparison: Classical Baseline vs AI Support Agent")
    plt.xticks(x, metrics)
    plt.ylim(0, 110)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def plot_judge_scores(judge_summary, output_path):
    dims = ["Correctness", "Relevance", "Groundedness", "Completeness", "Helpfulness", "Overall"]
    keys = ["correctness", "relevance", "groundedness", "completeness", "helpfulness", "overall_score"]
    vals = [judge_summary[k] for k in keys]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(dims, vals, color="#6366f1", width=0.5)
    plt.ylim(0, 5.5)
    plt.ylabel("Average Score (1 to 5)")
    plt.title("LLM-as-a-Judge Evaluation Dimensions on Golden Set")
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 0.1, f"{h:.2f}", ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def run_evaluation():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    print("--- 1. Evaluating Classical Baseline ---")
    baseline = TfidfBaseline()
    baseline.train()
    base_res = baseline.evaluate_test_set(TEST_CSV)
    print(f"Baseline Accuracy: {base_res['accuracy']:.4f}, Macro F1: {base_res['macro_f1']:.4f}")

    print("--- 2. Evaluating AI Support Agent on Test Set ---")
    agent = SupportAgent()
    test_rows = []
    with open(TEST_CSV, "r", encoding="utf-8") as f:
        test_rows = list(csv.DictReader(f))

    agent_preds = []
    test_trues = []
    agent_r1 = 0
    agent_r3 = 0
    agent_mrr = 0.0

    for r in test_rows:
        q = r["customer_query"]
        true_intent = r["intent"]
        test_trues.append(true_intent)

        res = agent.process_query(q)
        agent_preds.append(res["predicted_intent"])

        retrieved_intents = [d["intent"] for d in res["retrieved_documents"]]
        if retrieved_intents and retrieved_intents[0] == true_intent:
            agent_r1 += 1
        if true_intent in retrieved_intents:
            agent_r3 += 1
            agent_mrr += 1.0 / (retrieved_intents.index(true_intent) + 1)

    n_test = len(test_rows)
    agent_acc = accuracy_score(test_trues, agent_preds)
    agent_macro_f1 = f1_score(test_trues, agent_preds, average="macro", zero_division=0)
    labels = sorted(list(set(test_trues)))

    agent_metrics = {
        "model": "AI Support Agent (RAG + Grounding)",
        "test_sample_count": n_test,
        "accuracy": round(agent_acc, 4),
        "macro_f1": round(agent_macro_f1, 4),
        "recall_at_1": round(agent_r1 / n_test, 4),
        "recall_at_3": round(agent_r3 / n_test, 4),
        "mrr": round(agent_mrr / n_test, 4)
    }

    print(f"Agent Accuracy: {agent_metrics['accuracy']:.4f}, Macro F1: {agent_metrics['macro_f1']:.4f}")

    print("--- 3. Evaluating on Dedicated Golden Set ---")
    with open(GOLDEN_SET_JSON, "r", encoding="utf-8") as f:
        golden_items = json.load(f)

    judge = LLMJudge()
    golden_results = []
    cat_breakdown = {}
    judge_totals = {
        "correctness": 0.0,
        "relevance": 0.0,
        "groundedness": 0.0,
        "completeness": 0.0,
        "helpfulness": 0.0,
        "overall_score": 0.0,
        "hallucinations": 0
    }

    for item in golden_items:
        q = item["query"]
        cat = item["category"]
        exp_behavior = item["acceptable_behavior"]
        exp_ans = item["expected_answer"]

        res = agent.process_query(q)
        ans = res["answer"]
        top_context = res["retrieved_documents"][0]["policy_summary"] if res["retrieved_documents"] else "None"

        # LLM Judge evaluation
        j_eval = judge.evaluate(
            query=q,
            expected_answer=exp_ans,
            context=top_context,
            agent_answer=ans,
            acceptable_behavior=exp_behavior,
            required_facts=item.get("required_facts", [])
        )

        for k in ["correctness", "relevance", "groundedness", "completeness", "helpfulness", "overall_score"]:
            judge_totals[k] += j_eval[k]
        if j_eval.get("hallucination", False):
            judge_totals["hallucinations"] += 1

        # Check behavior success
        ans_lower = ans.lower()
        success = False
        if exp_behavior == "abstain":
            success = ("don't have information" in ans_lower or "do not have information" in ans_lower or "outside" in ans_lower or "cannot" in ans_lower)
        elif exp_behavior == "clarify":
            success = ("clarify" in ans_lower or "could you please" in ans_lower or "specify" in ans_lower)
        elif exp_behavior == "reject":
            success = ("cannot" in ans_lower or "refuse" in ans_lower or "only assist with" in ans_lower or "not authorized" in ans_lower)
        elif exp_behavior == "answer":
            success = ("don't have information" not in ans_lower and "clarify" not in ans_lower)

        if cat not in cat_breakdown:
            cat_breakdown[cat] = {"total": 0, "success": 0, "failures": []}
        cat_breakdown[cat]["total"] += 1
        if success:
            cat_breakdown[cat]["success"] += 1
        else:
            cat_breakdown[cat]["failures"].append({
                "id": item["id"],
                "query": q,
                "expected_behavior": exp_behavior,
                "agent_status": res["status"],
                "agent_answer": ans,
                "judge_reason": j_eval.get("reason", "")
            })

        golden_results.append({
            "id": item["id"],
            "category": cat,
            "query": q,
            "acceptable_behavior": exp_behavior,
            "agent_status": res["status"],
            "agent_answer": ans,
            "success": success,
            "judge_eval": j_eval
        })

    n_gold = len(golden_items)
    judge_summary = {k: round(v / n_gold, 2) for k, v in judge_totals.items() if k != "hallucinations"}
    judge_summary["hallucination_rate"] = round(judge_totals["hallucinations"] / n_gold, 4)

    for cat, data in cat_breakdown.items():
        data["success_rate"] = round(data["success"] / data["total"], 4)

    total_success = sum(d["success"] for d in cat_breakdown.values())
    overall_golden_reliability = round(total_success / n_gold, 4)

    # Generate Figures
    print("--- 4. Generating Visual Plots ---")
    plot_confusion_matrix(test_trues, agent_preds, labels, os.path.join(FIGURES_DIR, "confusion_matrix.png"))
    plot_intent_distribution("data/processed/train.csv", TEST_CSV, os.path.join(FIGURES_DIR, "intent_distribution.png"))
    plot_category_performance(cat_breakdown, os.path.join(FIGURES_DIR, "performance_by_category.png"))
    plot_baseline_vs_agent(base_res, agent_metrics, os.path.join(FIGURES_DIR, "baseline_vs_agent.png"))
    plot_judge_scores(judge_summary, os.path.join(FIGURES_DIR, "llm_judge_scores.png"))

    # Save summary JSON
    summary_data = {
        "baseline_test_metrics": base_res,
        "agent_test_metrics": agent_metrics,
        "golden_set_reliability": overall_golden_reliability,
        "category_breakdown": cat_breakdown,
        "llm_judge_summary": judge_summary,
        "sample_evaluations": golden_results[:10]
    }
    with open(os.path.join(REPORTS_DIR, "metrics_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # Generate Markdown Reports
    print("--- 5. Generating Evaluation & Failure Analysis Reports ---")
    _write_evaluation_report(base_res, agent_metrics, cat_breakdown, judge_summary, overall_golden_reliability)
    _write_failure_analysis_report(cat_breakdown)
    print("Evaluation completed successfully!")

def _write_evaluation_report(base_res, agent_metrics, cat_breakdown, judge_summary, golden_rel):
    content = f"""# AI Customer Support Agent - Comprehensive Evaluation Report

## 1. Executive Summary
This report presents a thorough evaluation of the **AI Customer Support Agent**, built with hybrid lexical/semantic retrieval, strict grounding constraints, and adaptive confidence checking. The system was evaluated against both held-out test customer tickets and a dedicated 44-case **Golden Set** representing standard, paraphrased, ambiguous, typo-heavy, adversarial, out-of-domain, and unsupported customer scenarios.

- **Baseline Test Accuracy**: {base_res['accuracy'] * 100:.1f}% (Macro F1: {base_res['macro_f1'] * 100:.1f}%)
- **AI Agent Test Accuracy**: {agent_metrics['accuracy'] * 100:.1f}% (Macro F1: {agent_metrics['macro_f1'] * 100:.1f}%)
- **Retrieval Recall@1**: {agent_metrics['recall_at_1'] * 100:.1f}% | **Recall@3**: {agent_metrics['recall_at_3'] * 100:.1f}% | **MRR**: {agent_metrics['mrr']:.3f}
- **Golden Set Overall Reliability**: {golden_rel * 100:.1f}%
- **Hallucination Rate**: {judge_summary['hallucination_rate'] * 100:.1f}%

---

## 2. Test Set Benchmark: Baseline vs. AI Agent

| Metric | Classical Baseline (TF-IDF + LogReg) | AI Support Agent (RAG + Grounding) | Absolute Gain |
| :--- | :---: | :---: | :---: |
| **Accuracy** | {base_res['accuracy'] * 100:.1f}% | {agent_metrics['accuracy'] * 100:.1f}% | +{(agent_metrics['accuracy'] - base_res['accuracy']) * 100:.1f}% |
| **Macro F1** | {base_res['macro_f1'] * 100:.1f}% | {agent_metrics['macro_f1'] * 100:.1f}% | +{(agent_metrics['macro_f1'] - base_res['macro_f1']) * 100:.1f}% |
| **Retrieval Recall@1** | {base_res['recall_at_1'] * 100:.1f}% | {agent_metrics['recall_at_1'] * 100:.1f}% | +{(agent_metrics['recall_at_1'] - base_res['recall_at_1']) * 100:.1f}% |
| **Retrieval Recall@3** | {base_res['recall_at_3'] * 100:.1f}% | {agent_metrics['recall_at_3'] * 100:.1f}% | +{(agent_metrics['recall_at_3'] - base_res['recall_at_3']) * 100:.1f}% |
| **MRR** | {base_res['mrr']:.3f} | {agent_metrics['mrr']:.3f} | +{(agent_metrics['mrr'] - base_res['mrr']):.3f} |

---

## 3. Golden Set Robustness Across Query Categories

| Query Category | Samples | Expected Behavior | Compliance Rate | Status |
| :--- | :---: | :---: | :---: | :---: |
"""
    for cat, d in sorted(cat_breakdown.items()):
        status_tag = "Pass" if d["success_rate"] >= 0.8 else "Needs Monitoring"
        content += f"| **{cat}** | {d['total']} | {d.get('failures', [{}])[0].get('expected_behavior', 'various') if d.get('failures') else 'answer/clarify/abstain'} | {d['success_rate']*100:.1f}% | {status_tag} |\n"

    content += f"""
---

## 4. LLM-as-a-Judge Evaluation (1-5 Scale)

Evaluated by Gemini structured judge on ground truth alignment, factual grounding, and customer safety:

- **Factual Correctness**: {judge_summary['correctness']:.2f} / 5.0
- **Query Relevance**: {judge_summary['relevance']:.2f} / 5.0
- **Knowledge Groundedness**: {judge_summary['groundedness']:.2f} / 5.0
- **Completeness**: {judge_summary['completeness']:.2f} / 5.0
- **Helpfulness & Professionalism**: {judge_summary['helpfulness']:.2f} / 5.0
- **Overall Quality Score**: {judge_summary['overall_score']:.2f} / 5.0
- **Measured Hallucination Rate**: {judge_summary['hallucination_rate'] * 100:.1f}%

---

## 5. Visual Artifacts
All generated plots are saved in `reports/figures/`:
1. `confusion_matrix.png`: Per-intent classification matrix.
2. `intent_distribution.png`: Stratified train vs test class distribution.
3. `performance_by_category.png`: Reliability breakdown across Golden Set query slices.
4. `baseline_vs_agent.png`: Classical baseline versus RAG Agent comparison.
5. `llm_judge_scores.png`: Multi-dimensional evaluation rubric.
"""
    with open(os.path.join(REPORTS_DIR, "evaluation_report.md"), "w", encoding="utf-8") as f:
        f.write(content)

def _write_failure_analysis_report(cat_breakdown):
    content = """# Customer Support Agent - Failure & Reliability Analysis

## 1. Why the Headline Metric is Misleading
In customer support systems, a headline metric like **"90% Accuracy"** is fundamentally deceptive and dangerous if viewed in isolation. Here is why:

1. **Catastrophic Cost of False Positives**:
   - In standard NLP, misclassifying a query from "order_tracking" to "shipping_delay" is penalized by 1 point.
   - In production customer support, if the system hallucinatingly confirms: *"Yes, we provide an immediate $500 cash reimbursement"*, the business suffers real financial and legal liability.
2. **The Abstention Blind Spot**:
   - A model forced to predict an answer on every input will achieve high recall on known classes, but a **0% safety rate** on out-of-domain and adversarial inputs.
   - In our system, **deliberate abstention** ("I don't have information about that in the knowledge base") on out-of-domain and unsupported inputs is treated as a **SUCCESS**, not a failure.
3. **The Ambiguity Trap**:
   - When a user submits "Cancel", answering with "Your subscription is cancelled" without verifying if they meant an active physical order or a software plan causes severe user frustration. Asking a clarifying question is the only reliable behavior.

---

## 2. Identified Failure Modes & Edge Cases

"""
    failure_found = False
    for cat, d in cat_breakdown.items():
        if d.get("failures"):
            failure_found = True
            content += f"### Category: {cat} (Failure Count: {len(d['failures'])})\n"
            for f_item in d["failures"]:
                content += f"- **Query**: \"{f_item['query']}\"\n"
                content += f"  - **Expected Behavior**: `{f_item['expected_behavior']}`\n"
                content += f"  - **Agent Response**: \"{f_item['agent_answer']}\"\n"
                content += f"  - **Root Cause**: {f_item['judge_reason']}\n"
                content += f"  - **Mitigation Strategy**: Improve intent thresholding or expand query synonym mappings.\n\n"

    if not failure_found:
        content += "No critical failures observed across the Golden Set evaluation suite. All 8 query categories met the target behavioral constraints.\n\n"

    content += """## 3. Reliability Principles Implemented in this Agent

1. **Zero Hallucination Guardrail**:
   - System prompts and deterministic fallback synthesis explicitly forbid generating facts outside the retrieved knowledge base.
2. **Explicit Confidence Gating**:
   - Cosine similarity below threshold (0.22) automatically triggers a safe abstention rather than an extrapolated answer.
3. **Dedicated Ambiguity Disambiguator**:
   - Queries with <= 2 words lacking a named entity trigger a clarification dialogue.
4. **Adversarial Input Sanitization**:
   - Prompt injections and jailbreak patterns are intercepted prior to knowledge retrieval, preserving prompt integrity.
"""
    with open(os.path.join(REPORTS_DIR, "failure_analysis.md"), "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    run_evaluation()
