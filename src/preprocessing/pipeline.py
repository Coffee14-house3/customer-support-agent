"""
Complete data preprocessing pipeline for customer support tickets.
"""
import os
import csv
import json
import random
from collections import Counter
from typing import Dict, Any, List, Tuple
from src.preprocessing.cleaner import clean_text, is_valid_query, normalize_for_comparison
from src.preprocessing.leakage_detector import LeakageDetector

RAW_FILE = "data/raw/customer_support_tickets.csv"
PROCESSED_DIR = "data/processed"
TRAIN_FILE = os.path.join(PROCESSED_DIR, "train.csv")
TEST_FILE = os.path.join(PROCESSED_DIR, "test.csv")
KB_FILE = os.path.join(PROCESSED_DIR, "knowledge_base.json")
STATS_FILE = os.path.join(PROCESSED_DIR, "preprocessing_stats.json")
LEAKAGE_FILE = os.path.join(PROCESSED_DIR, "leakage_report.json")

def load_raw_data(file_path: str = RAW_FILE) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw dataset not found at {file_path}")
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows

def analyze_raw_dataset(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Perform exploratory analysis on raw rows."""
    total_count = len(rows)
    columns = list(rows[0].keys()) if rows else []
    
    missing_values = {col: 0 for col in columns}
    intent_counts = Counter()
    category_counts = Counter()
    empty_queries = []
    short_ambiguous_queries = []

    for idx, r in enumerate(rows):
        query = r.get("customer_query", "")
        intent = r.get("intent", "unknown")
        category = r.get("category", "unknown")
        
        intent_counts[intent] += 1
        category_counts[category] += 1

        for col in columns:
            val = r.get(col, "")
            if val is None or str(val).strip() == "":
                missing_values[col] += 1

        cleaned_q = clean_text(query)
        if not cleaned_q:
            empty_queries.append({"row": idx, "ticket_id": r.get("ticket_id", "")})
        elif len(cleaned_q.split()) <= 2:
            short_ambiguous_queries.append({
                "ticket_id": r.get("ticket_id", ""),
                "query": query,
                "intent": intent
            })

    detector = LeakageDetector()
    dup_report = detector.find_internal_duplicates(rows, text_field="customer_query")

    return {
        "total_records": total_count,
        "columns": columns,
        "missing_values": missing_values,
        "unique_intents_count": len(intent_counts),
        "intent_distribution": dict(intent_counts),
        "category_distribution": dict(category_counts),
        "empty_queries_count": len(empty_queries),
        "empty_queries": empty_queries,
        "short_ambiguous_count": len(short_ambiguous_queries),
        "short_ambiguous_queries": short_ambiguous_queries,
        "exact_duplicates": dup_report["exact_duplicates"],
        "near_duplicates": dup_report["near_duplicates"]
    }

def run_preprocessing(test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
    """Clean data, remove noise, split train/test stratifying by intent, and construct knowledge base."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    raw_rows = load_raw_data()
    raw_stats = analyze_raw_dataset(raw_rows)

    # Filtering & deduplication
    valid_rows = []
    seen_normalized = set()
    dropped_empty = 0
    dropped_duplicates = 0

    for r in raw_rows:
        q = r.get("customer_query", "")
        if not is_valid_query(q):
            dropped_empty += 1
            continue
        norm_q = normalize_for_comparison(q)
        if norm_q in seen_normalized:
            dropped_duplicates += 1
            continue
        seen_normalized.add(norm_q)
        
        # Cleaned record
        clean_r = dict(r)
        clean_r["customer_query"] = clean_text(q)
        clean_r["policy_reference"] = clean_text(r.get("policy_reference", ""))
        clean_r["resolution_steps"] = clean_text(r.get("resolution_steps", ""))
        valid_rows.append(clean_r)

    # Stratified Train / Test split
    by_intent: Dict[str, List[Dict[str, Any]]] = {}
    for r in valid_rows:
        by_intent.setdefault(r["intent"], []).append(r)

    train_rows: List[Dict[str, Any]] = []
    test_rows: List[Dict[str, Any]] = []
    rng = random.Random(random_state)

    for intent in sorted(by_intent.keys()):
        intent_records = list(by_intent[intent])
        rng.shuffle(intent_records)
        split_idx = int(len(intent_records) * (1 - test_size))
        train_rows.extend(intent_records[:split_idx])
        test_rows.extend(intent_records[split_idx:])

    # Write train and test CSVs
    fieldnames = list(valid_rows[0].keys())
    with open(TRAIN_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(train_rows)

    with open(TEST_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_rows)

    # Construct Knowledge Base strictly from training data policy references & standard resolutions
    # We group by intent to avoid redundancy and ensure clean retrieval documents
    kb_entries = {}
    for r in train_rows:
        intent = r["intent"]
        if intent not in kb_entries:
            kb_entries[intent] = {
                "kb_id": f"KB-{intent.upper()}",
                "intent": intent,
                "category": r.get("category", "General"),
                "title": intent.replace("_", " ").title(),
                "policy_summary": r.get("policy_reference", ""),
                "resolution_procedure": r.get("resolution_steps", ""),
                "example_queries": []
            }
        if len(kb_entries[intent]["example_queries"]) < 5:
            kb_entries[intent]["example_queries"].append(r["customer_query"])

    knowledge_base = list(kb_entries.values())
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2)

    # Verify no leakage between train and test
    detector = LeakageDetector()
    cross_leakage = detector.check_cross_leakage(
        reference_records=train_rows,
        eval_records=test_rows,
        ref_field="customer_query",
        eval_field="customer_query"
    )

    with open(LEAKAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(cross_leakage, f, indent=2)

    stats = {
        "raw_analysis": raw_stats,
        "clean_total_count": len(valid_rows),
        "dropped_empty_count": dropped_empty,
        "dropped_duplicate_count": dropped_duplicates,
        "train_count": len(train_rows),
        "test_count": len(test_rows),
        "train_intent_distribution": dict(Counter([r["intent"] for r in train_rows])),
        "test_intent_distribution": dict(Counter([r["intent"] for r in test_rows])),
        "kb_articles_count": len(knowledge_base),
        "leakage_audit": cross_leakage
    }

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    return stats

if __name__ == "__main__":
    s = run_preprocessing()
    print("Preprocessing completed successfully!")
    print(f"Raw records: {s['raw_analysis']['total_records']}")
    print(f"Clean records: {s['clean_total_count']} (Train: {s['train_count']}, Test: {s['test_count']})")
    print(f"Knowledge base documents: {s['kb_articles_count']}")
    print(f"Train/Test leakage detected: {s['leakage_audit']['has_leakage']}")
