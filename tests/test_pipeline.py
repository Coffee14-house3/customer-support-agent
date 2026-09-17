"""
Unit and integration tests for preprocessing pipeline and data integrity.
"""
import os
import csv
import json
import unittest
from src.preprocessing.cleaner import clean_text, is_valid_query, normalize_query_semantics, compute_jaccard_similarity
from src.preprocessing.pipeline import load_raw_data, analyze_raw_dataset, run_preprocessing
from src.preprocessing.leakage_detector import LeakageDetector

class TestPipeline(unittest.TestCase):
    def test_clean_text_normalizes_whitespace(self):
        raw = "  Hello   world! \t\n  Where is my   order? "
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "Hello world! Where is my order?")

    def test_is_valid_query_filters_empty(self):
        self.assertFalse(is_valid_query(""))
        self.assertFalse(is_valid_query("   "))
        self.assertFalse(is_valid_query("a"))
        self.assertTrue(is_valid_query("Where is my order?"))

    def test_normalize_query_semantics_fixes_typos(self):
        query = "wher is my pakage order #99214 pls hlp"
        normalized = normalize_query_semantics(query)
        self.assertIn("where", normalized)
        self.assertIn("package", normalized)
        self.assertIn("please", normalized)
        self.assertIn("help", normalized)

    def test_compute_jaccard_similarity(self):
        s1 = "Where is my order right now?"
        s2 = "where is my order right now???"
        sim = compute_jaccard_similarity(s1, s2)
        self.assertTrue(sim > 0.85)

    def test_raw_dataset_exists_and_has_required_schema(self):
        raw_path = "data/raw/customer_support_tickets.csv"
        self.assertTrue(os.path.exists(raw_path))
        rows = load_raw_data(raw_path)
        self.assertTrue(len(rows) > 50)
        expected_cols = ["ticket_id", "customer_query", "intent", "category", "policy_reference", "resolution_steps"]
        for col in expected_cols:
            self.assertIn(col, rows[0])

    def test_leakage_detector_identifies_exact_match(self):
        detector = LeakageDetector()
        ref = [{"customer_query": "How do I return an item?"}]
        eval_set = [{"query": "how do i return an item?"}]
        leakage = detector.check_cross_leakage(ref, eval_set)
        self.assertTrue(leakage["has_leakage"])
        self.assertEqual(leakage["exact_leak_count"], 1)

    def test_processed_split_has_zero_leakage(self):
        leakage_path = "data/processed/leakage_report.json"
        self.assertTrue(os.path.exists(leakage_path))
        with open(leakage_path) as f:
            rep = json.load(f)
        self.assertFalse(rep["has_leakage"])
        self.assertEqual(rep["exact_leak_count"], 0)
        self.assertEqual(rep["near_leak_count"], 0)

if __name__ == "__main__":
    unittest.main()
