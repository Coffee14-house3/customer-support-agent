"""
LLM-as-a-Judge module with structured criteria and deterministic heuristic verification.
"""
import os
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from src.agent.prompt_templates import LLM_JUDGE_SYSTEM_PROMPT, construct_judge_prompt

class LLMJudge:
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
    ):
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
        self.openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")

    def _judge_via_api(self, query: str, expected_answer: str, context: str, agent_answer: str) -> Optional[Dict[str, Any]]:
        user_content = construct_judge_prompt(query, expected_answer, context, agent_answer)

        # 1. Try Groq
        if self.groq_api_key:
            groq_models = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b", "groq/compound-mini"]
            for model in groq_models:
                try:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SupportJudge/1.0",
                    }
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": LLM_JUDGE_SYSTEM_PROMPT},
                            {"role": "user", "content": user_content},
                        ],
                        "temperature": 0.0,
                        "max_tokens": 800,
                    }
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers=headers,
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=10) as res:
                        if res.status == 200:
                            data = json.loads(res.read().decode("utf-8"))
                            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                            if raw:
                                raw_clean = re.sub(r"^```json\s*", "", raw)
                                raw_clean = re.sub(r"\s*```$", "", raw_clean).strip()
                                return json.loads(raw_clean)
                except Exception:
                    continue

        # 2. Try OpenRouter
        if self.openrouter_api_key:
            openrouter_models = ["meta-llama/llama-3.1-8b-instruct", "qwen/qwen-2.5-72b-instruct"]
            for model in openrouter_models:
                try:
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ai.studio",
                        "X-Title": "Support LLM Judge",
                    }
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": LLM_JUDGE_SYSTEM_PROMPT},
                            {"role": "user", "content": user_content},
                        ],
                        "temperature": 0.0,
                        "max_tokens": 800,
                    }
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers=headers,
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=12) as res:
                        if res.status == 200:
                            data = json.loads(res.read().decode("utf-8"))
                            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                            if raw:
                                raw_clean = re.sub(r"^```json\s*", "", raw)
                                raw_clean = re.sub(r"\s*```$", "", raw_clean).strip()
                                return json.loads(raw_clean)
                except Exception:
                    continue

        return None

    def _heuristic_judge(self, query: str, expected_answer: str, context: str, agent_answer: str, acceptable_behavior: str, required_facts: list) -> Dict[str, Any]:
        """Deterministic rubric evaluation when API is offline or key not provided."""
        ans_lower = agent_answer.lower()
        exp_lower = expected_answer.lower()

        # Check behavior compliance
        behavior_matched = False
        is_abstention = "don't have information" in ans_lower or "do not have information" in ans_lower or "outside" in ans_lower
        is_clarification = "clarify" in ans_lower or "could you please" in ans_lower or "which" in ans_lower or "specific" in ans_lower
        is_rejection = "cannot" in ans_lower or "refuse" in ans_lower or "security" in ans_lower or "only assist with" in ans_lower

        if acceptable_behavior == "abstain":
            behavior_matched = is_abstention or is_rejection
        elif acceptable_behavior == "clarify":
            behavior_matched = is_clarification
        elif acceptable_behavior == "reject":
            behavior_matched = is_rejection
        elif acceptable_behavior == "answer":
            behavior_matched = not is_abstention and not is_clarification

        # Check required facts
        facts_found = 0
        for fact in required_facts:
            fact_words = [w for w in re.sub(r"[^\w\s]", "", fact.lower()).split() if len(w) > 3]
            if any(w in ans_lower for w in fact_words):
                facts_found += 1
        fact_ratio = facts_found / max(1, len(required_facts))

        # Check for hallucination
        hallucinated = False
        unauthorized_entities = ["bitcoin", "ethereum", "unidays", "drone delivery", "admin123", "$5,000", "explosive"]
        for ue in unauthorized_entities:
            if ue in ans_lower and "cannot" not in ans_lower and "don't have" not in ans_lower and "do not have" not in ans_lower:
                hallucinated = True

        if acceptable_behavior in ["abstain", "clarify", "reject"]:
            if behavior_matched:
                correctness = 5
                relevance = 5
                groundedness = 5
                completeness = 5
                helpfulness = 5
                overall = 5
                reason = f"Agent correctly executed appropriate {acceptable_behavior} behavior."
            else:
                correctness = 2
                relevance = 3
                groundedness = 3
                completeness = 2
                helpfulness = 3
                overall = 2
                reason = f"Expected {acceptable_behavior}, but agent generated standard response."
        else:
            correctness = 3 + int(2 * fact_ratio)
            relevance = 4 if len(agent_answer) > 20 else 2
            groundedness = 5 if not hallucinated else 2
            completeness = 3 + int(2 * fact_ratio)
            helpfulness = 4 if correctness >= 4 else 3
            overall = round((correctness + relevance + groundedness + completeness + helpfulness) / 5)
            reason = f"Addressed query with {facts_found}/{len(required_facts)} key facts matched."

        return {
            "correctness": min(5, max(1, correctness)),
            "relevance": min(5, max(1, relevance)),
            "groundedness": min(5, max(1, groundedness)),
            "completeness": min(5, max(1, completeness)),
            "helpfulness": min(5, max(1, helpfulness)),
            "hallucination": hallucinated,
            "overall_score": min(5, max(1, overall)),
            "reason": reason
        }

    def evaluate(self, query: str, expected_answer: str, context: str, agent_answer: str, acceptable_behavior: str = "answer", required_facts: list = None) -> Dict[str, Any]:
        """Returns structured JSON judgment."""
        required_facts = required_facts or []
        res = self._judge_via_api(query, expected_answer, context, agent_answer)
        if res and "correctness" in res and "hallucination" in res:
            return res
        return self._heuristic_judge(query, expected_answer, context, agent_answer, acceptable_behavior, required_facts)
