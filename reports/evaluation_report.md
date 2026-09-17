# AI Customer Support Agent - Comprehensive Evaluation Report

## 1. Executive Summary
This report presents a thorough evaluation of the **AI Customer Support Agent**, built with hybrid lexical/semantic retrieval, strict grounding constraints, and adaptive confidence checking. The system was evaluated against both held-out test customer tickets and a dedicated 44-case **Golden Set** representing standard, paraphrased, ambiguous, typo-heavy, adversarial, out-of-domain, and unsupported customer scenarios.

- **Baseline Test Accuracy**: 67.6% (Macro F1: 61.2%)
- **AI Agent Test Accuracy**: 70.3% (Macro F1: 67.0%)
- **Retrieval Recall@1**: 73.0% | **Recall@3**: 97.3% | **MRR**: 0.833
- **Golden Set Overall Reliability**: 95.5%
- **Hallucination Rate**: 0.0%

---

## 2. Test Set Benchmark: Baseline vs. AI Agent

| Metric | Classical Baseline (TF-IDF + LogReg) | AI Support Agent (RAG + Grounding) | Absolute Gain |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 67.6% | 70.3% | +2.7% |
| **Macro F1** | 61.2% | 67.0% | +5.8% |
| **Retrieval Recall@1** | 64.9% | 73.0% | +8.1% |
| **Retrieval Recall@3** | 94.6% | 97.3% | +2.7% |
| **MRR** | 0.784 | 0.833 | +0.049 |

---

## 3. Golden Set Robustness Across Query Categories

| Query Category | Samples | Expected Behavior | Compliance Rate | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Adversarial** | 5 | answer/clarify/abstain | 100.0% | Pass |
| **Ambiguous** | 5 | clarify | 100.0% | Pass |
| **Difficult** | 5 | answer/clarify/abstain | 100.0% | Pass |
| **OutOfDomain** | 5 | answer/clarify/abstain | 100.0% | Pass |
| **Paraphrase** | 6 | answer/clarify/abstain | 100.0% | Pass |
| **Standard** | 8 | answer/clarify/abstain | 100.0% | Pass |
| **Typo_Informal** | 5 | answer/clarify/abstain | 100.0% | Pass |
| **Unsupported** | 5 | answer/clarify/abstain | 100.0% | Pass |

---

## 4. LLM-as-a-Judge Evaluation (1-5 Scale)

Evaluated by Gemini structured judge on ground truth alignment, factual grounding, and customer safety:

- **Factual Correctness**: 4.84 / 5.0
- **Query Relevance**: 4.34 / 5.0
- **Knowledge Groundedness**: 4.91 / 5.0
- **Completeness**: 4.84 / 5.0
- **Helpfulness & Professionalism**: 4.34 / 5.0
- **Overall Quality Score**: 4.84 / 5.0
- **Measured Hallucination Rate**: 0.0%

---

## 5. Visual Artifacts
All generated plots are saved in `reports/figures/`:
1. `confusion_matrix.png`: Per-intent classification matrix.
2. `intent_distribution.png`: Stratified train vs test class distribution.
3. `performance_by_category.png`: Reliability breakdown across Golden Set query slices.
4. `baseline_vs_agent.png`: Classical baseline versus RAG Agent comparison.
5. `llm_judge_scores.png`: Multi-dimensional evaluation rubric.
