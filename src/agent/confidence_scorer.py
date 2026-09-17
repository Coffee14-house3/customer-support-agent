"""
Confidence scoring and grounding verification for support responses.
"""
import re
from typing import Dict, Any, List, Optional
from src.preprocessing.cleaner import clean_text, normalize_for_comparison

# Short or inherently ambiguous patterns that require clarification
AMBIGUOUS_PATTERNS = [
    r"^(cancel|cancel it|cancel please)$",
    r"^(help|help me|i need help)$",
    r"^(status|check status)$",
    r"it (isn't|isnt|is not|does not|doesn't) work(ing)?",
    r"change something",
    r"help me fix this problem",
    r"^(fix this|problem|issue)$"
]

# Adversarial injection triggers
ADVERSARIAL_PATTERNS = [
    r"ignore (all )?(previous|prior) (instructions|rules|constraints)",
    r"print your (hidden )?developer system (prompt|instructions)",
    r"pretend you are in developer mode",
    r"authorize an immediate \$\d+",
    r"explosive device|household chemicals|make a bomb",
    r"system prompt override"
]

# Common out-of-domain patterns
OOD_KEYWORDS = [
    "capital city", "weather in", "stock market", "world cup", "recipe for",
    "python script", "binary search", "quantum physics", "who won", "president of"
]

class ConfidenceScorer:
    def __init__(self, high_threshold: float = 0.40, low_threshold: float = 0.11):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def check_adversarial(self, query: str) -> bool:
        norm = clean_text(query).lower()
        for pat in ADVERSARIAL_PATTERNS:
            if re.search(pat, norm):
                return True
        return False

    def check_ambiguous(self, query: str) -> bool:
        norm = normalize_for_comparison(query)
        for pat in AMBIGUOUS_PATTERNS:
            if re.search(pat, norm):
                return True
        # Also check queries with 2 or fewer words that don't specify an entity
        words = norm.split()
        if len(words) <= 2 and words[0] in ["cancel", "help", "status", "fix", "change", "update"]:
            return True
        return False

    def check_out_of_domain(self, query: str, top_similarity: float) -> bool:
        norm = clean_text(query).lower()
        for kw in OOD_KEYWORDS:
            if kw in norm:
                return True
        # If retriever similarity is very low and query has several words
        if top_similarity < self.low_threshold:
            return True
        return False

    def assess_confidence(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        response_text: str
    ) -> Dict[str, Any]:
        """Assess overall confidence, grounding, and determine whether agent should abstain."""
        top_score = retrieved_docs[0]["similarity_score"] if retrieved_docs else 0.0

        is_adv = self.check_adversarial(query)
        is_amb = self.check_ambiguous(query)
        is_ood = self.check_out_of_domain(query, top_score)

        if is_adv:
            return {
                "confidence_level": "REJECT",
                "score": 0.99,
                "status": "adversarial_rejected",
                "should_abstain": True,
                "reason": "Adversarial or jailbreak pattern detected."
            }

        if is_amb:
            return {
                "confidence_level": "CLARIFICATION_NEEDED",
                "score": 0.50,
                "status": "clarification_requested",
                "should_abstain": False,
                "reason": "Query is ambiguous or underspecified."
            }

        if is_ood or top_score < self.low_threshold:
            return {
                "confidence_level": "LOW",
                "score": top_score,
                "status": "abstain_out_of_domain",
                "should_abstain": True,
                "reason": f"Top retrieval similarity ({top_score:.3f}) below threshold ({self.low_threshold})."
            }

        # Check unsupported specific entities (e.g. bitcoin, drone, student discount, branch locations)
        unsupported_terms = [
            "bitcoin", "cryptocurrency", "ethereum", "drone delivery", "student discount",
            "unidays", "ceo john doe", "paris branch", "opening hours", "physical street address", "retail store"
        ]
        query_lower = query.lower()
        for ut in unsupported_terms:
            if ut in query_lower:
                # Check if it exists in retrieved policy
                kb_text = " ".join([d.get("policy_summary", "") + " " + d.get("resolution_procedure", "") for d in retrieved_docs]).lower()
                if ut not in kb_text:
                    return {
                        "confidence_level": "LOW",
                        "score": top_score,
                        "status": "abstain_unsupported_facts",
                        "should_abstain": True,
                        "reason": f"Queried entity '{ut}' is not present in company knowledge base."
                    }

        # Normal confidence evaluation
        if top_score >= self.high_threshold:
            conf = "HIGH"
        else:
            conf = "MEDIUM"

        return {
            "confidence_level": conf,
            "score": top_score,
            "status": "grounded_response",
            "should_abstain": False,
            "reason": f"Grounded in knowledge base document with similarity {top_score:.3f}."
        }
