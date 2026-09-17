"""
Leakage detection module to audit train-test separation and golden set isolation.
"""
from typing import List, Dict, Any, Tuple
from src.preprocessing.cleaner import normalize_for_comparison, compute_jaccard_similarity

class LeakageDetector:
    def __init__(self, near_duplicate_threshold: float = 0.82):
        self.near_duplicate_threshold = near_duplicate_threshold

    def find_internal_duplicates(self, records: List[Dict[str, Any]], text_field: str = "customer_query") -> Dict[str, Any]:
        """Find exact and near duplicates within a dataset."""
        exact_seen = {}
        exact_duplicates = []
        near_duplicates = []

        clean_records = []
        for idx, rec in enumerate(records):
            query = rec.get(text_field, "")
            norm = normalize_for_comparison(query)
            if not norm:
                continue
            if norm in exact_seen:
                exact_duplicates.append({
                    "original_id": exact_seen[norm]["id"],
                    "duplicate_id": rec.get("ticket_id", f"row_{idx}"),
                    "query": query,
                    "normalized": norm
                })
            else:
                exact_seen[norm] = {"id": rec.get("ticket_id", f"row_{idx}"), "query": query, "norm": norm, "record": rec}
                clean_records.append(exact_seen[norm])

        # Check near duplicates among unique records
        n = len(clean_records)
        for i in range(n):
            for j in range(i + 1, n):
                r1 = clean_records[i]
                r2 = clean_records[j]
                sim = compute_jaccard_similarity(r1["query"], r2["query"])
                if sim >= self.near_duplicate_threshold:
                    near_duplicates.append({
                        "id1": r1["id"],
                        "id2": r2["id"],
                        "query1": r1["query"],
                        "query2": r2["query"],
                        "similarity": round(sim, 4)
                    })

        return {
            "total_records": len(records),
            "exact_duplicate_count": len(exact_duplicates),
            "exact_duplicates": exact_duplicates,
            "near_duplicate_count": len(near_duplicates),
            "near_duplicates": near_duplicates
        }

    def check_cross_leakage(
        self,
        reference_records: List[Dict[str, Any]],
        eval_records: List[Dict[str, Any]],
        ref_field: str = "customer_query",
        eval_field: str = "query"
    ) -> Dict[str, Any]:
        """Check whether evaluation records leak into reference (training/knowledge) data."""
        ref_normalized = {}
        for r in reference_records:
            q = r.get(ref_field, "")
            norm = normalize_for_comparison(q)
            if norm:
                ref_normalized[norm] = r

        exact_leaks = []
        near_leaks = []

        for e in eval_records:
            e_query = e.get(eval_field, "")
            e_norm = normalize_for_comparison(e_query)
            if not e_norm:
                continue

            # Exact match
            if e_norm in ref_normalized:
                exact_leaks.append({
                    "eval_id": e.get("id", e.get("ticket_id", "unknown")),
                    "eval_query": e_query,
                    "matched_ref_query": ref_normalized[e_norm].get(ref_field, ""),
                    "leakage_type": "exact_match"
                })
                continue

            # Near match
            for norm_ref, ref_r in ref_normalized.items():
                sim = compute_jaccard_similarity(e_query, ref_r.get(ref_field, ""))
                if sim >= self.near_duplicate_threshold:
                    near_leaks.append({
                        "eval_id": e.get("id", e.get("ticket_id", "unknown")),
                        "eval_query": e_query,
                        "matched_ref_query": ref_r.get(ref_field, ""),
                        "similarity": round(sim, 4),
                        "leakage_type": "near_duplicate"
                    })

        has_leakage = (len(exact_leaks) + len(near_leaks)) > 0
        return {
            "has_leakage": has_leakage,
            "exact_leak_count": len(exact_leaks),
            "exact_leaks": exact_leaks,
            "near_leak_count": len(near_leaks),
            "near_leaks": near_leaks
        }
