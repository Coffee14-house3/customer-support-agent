"""
Classical Baseline: TF-IDF Vectorizer + Logistic Regression Classifier and Cosine Retriever.
"""
import os
import json
import csv
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import classification_report, accuracy_score, f1_score

class TfidfBaseline:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.classifier = LogisticRegression(max_iter=500, random_state=42, C=1.0)
        self.kb_documents = []
        self.kb_vectors = None
        self.is_trained = False

    def train(self, train_csv_path: str = "data/processed/train.csv", kb_json_path: str = "data/processed/knowledge_base.json"):
        """Train classifier on train split and index knowledge base documents."""
        queries = []
        intents = []

        with open(train_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                queries.append(row["customer_query"])
                intents.append(row["intent"])

        X_train = self.vectorizer.fit_transform(queries)
        self.classifier.fit(X_train, intents)

        # Index Knowledge Base
        with open(kb_json_path, "r", encoding="utf-8") as f:
            self.kb_documents = json.load(f)

        kb_texts = [
            f"{doc['title']} {doc['policy_summary']} {doc['resolution_procedure']} {' '.join(doc.get('example_queries', []))}"
            for doc in self.kb_documents
        ]
        self.kb_vectors = self.vectorizer.transform(kb_texts)
        self.is_trained = True

    def predict_intent(self, query: str) -> Tuple[str, float]:
        """Predict intent and confidence score."""
        if not self.is_trained:
            raise RuntimeError("Baseline model has not been trained yet.")
        vec = self.vectorizer.transform([query])
        probs = self.classifier.predict_proba(vec)[0]
        max_idx = np.argmax(probs)
        pred_intent = self.classifier.classes_[max_idx]
        confidence = float(probs[max_idx])
        return pred_intent, confidence

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top-k knowledge base articles based on cosine similarity."""
        if not self.is_trained:
            raise RuntimeError("Baseline model has not been trained yet.")
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.kb_vectors)[0]
        top_indices = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = dict(self.kb_documents[idx])
            doc["similarity_score"] = float(round(sims[idx], 4))
            results.append(doc)
        return results

    def evaluate_test_set(self, test_csv_path: str = "data/processed/test.csv") -> Dict[str, Any]:
        """Evaluate baseline on held-out test data."""
        test_queries = []
        true_intents = []
        with open(test_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_queries.append(row["customer_query"])
                true_intents.append(row["intent"])

        pred_intents = []
        retrieval_at_1 = 0
        retrieval_at_3 = 0
        mrr_sum = 0.0

        for q, true_intent in zip(test_queries, true_intents):
            pred_intent, _ = self.predict_intent(q)
            pred_intents.append(pred_intent)

            retrieved = self.retrieve(q, top_k=3)
            retrieved_intents = [doc["intent"] for doc in retrieved]

            if retrieved_intents and retrieved_intents[0] == true_intent:
                retrieval_at_1 += 1
            if true_intent in retrieved_intents:
                retrieval_at_3 += 1
                rank = retrieved_intents.index(true_intent) + 1
                mrr_sum += 1.0 / rank

        n = len(test_queries)
        acc = accuracy_score(true_intents, pred_intents)
        macro_f1 = f1_score(true_intents, pred_intents, average="macro", zero_division=0)
        report = classification_report(true_intents, pred_intents, output_dict=True, zero_division=0)

        return {
            "model": "TF-IDF + Logistic Regression Baseline",
            "test_sample_count": n,
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "recall_at_1": round(retrieval_at_1 / n, 4) if n > 0 else 0,
            "recall_at_3": round(retrieval_at_3 / n, 4) if n > 0 else 0,
            "mrr": round(mrr_sum / n, 4) if n > 0 else 0,
            "per_class_report": report
        }

if __name__ == "__main__":
    baseline = TfidfBaseline()
    baseline.train()
    results = baseline.evaluate_test_set()
    print("Baseline Evaluation Results:")
    print(f"Accuracy: {results['accuracy']}")
    print(f"Macro F1: {results['macro_f1']}")
    print(f"Retrieval Recall@1: {results['recall_at_1']}")
    print(f"Retrieval Recall@3: {results['recall_at_3']}")
    print(f"Retrieval MRR: {results['mrr']}")
