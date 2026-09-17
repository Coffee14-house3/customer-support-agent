"""
Knowledge Retriever using pure-Python TF-IDF with Stop Words and Lexical N-Gram Matching.
"""
import os
import json
import re
import math
from collections import Counter
from typing import List, Dict, Any, Tuple, Optional
from src.preprocessing.cleaner import clean_text, normalize_for_comparison, normalize_query_semantics

ENGLISH_STOP_WORDS = {
    "a", "about", "above", "across", "after", "afterwards", "again", "against", "all", "almost",
    "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "an",
    "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around",
    "as", "at", "be", "became", "because", "become", "becomes", "becoming", "been", "before",
    "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "both",
    "but", "by", "can", "cannot", "could", "did", "do", "does", "doing", "done", "down", "during",
    "each", "either", "else", "elsewhere", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "few", "for", "from", "further", "get", "give", "go", "had", "has",
    "have", "having", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon",
    "hers", "herself", "him", "himself", "his", "how", "however", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "moreover", "most", "mostly", "my", "myself",
    "neither", "no", "nobody", "none", "nor", "not", "nothing", "now", "nowhere", "of", "off",
    "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "re", "same", "she", "should", "so", "some",
    "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such",
    "than", "that", "the", "their", "theirs", "them", "themselves", "then", "thence", "there",
    "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "this", "those",
    "through", "throughout", "thru", "thus", "to", "together", "too", "under", "until", "up",
    "upon", "us", "very", "was", "we", "were", "what", "whatever", "when", "whence", "whenever",
    "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
    "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves"
}

def extract_terms(text: str) -> List[str]:
    """Extract unigrams and bigrams excluding stop words."""
    tokens = [w for w in re.findall(r"(?u)\b\w\w+\b", text.lower()) if w not in ENGLISH_STOP_WORDS]
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
    return tokens + bigrams

class SupportRetriever:
    def __init__(self, kb_path: str = "data/processed/knowledge_base.json", train_path: str = "data/processed/train.csv"):
        self.kb_path = kb_path
        self.train_path = train_path
        self.documents: List[Dict[str, Any]] = []
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self.doc_norms: List[float] = []
        self.is_indexed = False
        self._load_and_index()

    def _load_and_index(self):
        if not os.path.exists(self.kb_path):
            return
        with open(self.kb_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        if not self.documents:
            return

        # Build corpus tokens for each document
        corpus_terms: List[Counter] = []
        doc_freq: Counter = Counter()

        for doc in self.documents:
            text = f"{doc.get('title', '')} {doc.get('policy_summary', '')} {doc.get('resolution_procedure', '')} "
            text += " ".join(doc.get("example_queries", []))
            terms = extract_terms(text)
            term_counts = Counter(terms)
            corpus_terms.append(term_counts)
            for term in term_counts.keys():
                doc_freq[term] += 1

        n_docs = len(self.documents)
        # Compute smooth IDF: log((1 + N) / (1 + df)) + 1
        self.idf = {
            term: math.log((1 + n_docs) / (1 + freq)) + 1.0
            for term, freq in doc_freq.items()
        }

        # Compute document TF-IDF vectors with sublinear TF: 1 + log(tf)
        self.doc_vectors = []
        self.doc_norms = []
        for term_counts in corpus_terms:
            vec: Dict[str, float] = {}
            for term, count in term_counts.items():
                idf_val = self.idf.get(term, 1.0)
                tf_weight = 1.0 + math.log(count) if count > 0 else 0.0
                vec[term] = tf_weight * idf_val

            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self.doc_vectors.append(vec)
            self.doc_norms.append(norm)

        self.is_indexed = True

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top_k most relevant documents for query with similarity score."""
        if not self.is_indexed:
            self._load_and_index()
            if not self.is_indexed:
                return []

        cleaned_q = clean_text(query)
        if not cleaned_q:
            return []

        sem_q = normalize_query_semantics(cleaned_q)
        q_terms = extract_terms(sem_q)
        q_counts = Counter(q_terms)

        # Build query TF-IDF vector
        q_vec: Dict[str, float] = {}
        for term, count in q_counts.items():
            if term in self.idf:
                tf_weight = 1.0 + math.log(count) if count > 0 else 0.0
                q_vec[term] = tf_weight * self.idf[term]

        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0

        # Token match bonus for exact keywords
        norm_q = normalize_for_comparison(cleaned_q)
        q_tokens = set([w for w in norm_q.split() if len(w) > 2])

        ranked = []
        for idx, d_vec in enumerate(self.doc_vectors):
            doc = self.documents[idx]
            d_norm = self.doc_norms[idx]

            # Cosine similarity
            dot = sum(q_weight * d_vec.get(term, 0.0) for term, q_weight in q_vec.items())
            base_score = dot / (q_norm * d_norm) if (q_norm * d_norm) > 0 else 0.0

            doc_norm_str = normalize_for_comparison(f"{doc.get('title', '')} {doc.get('policy_summary', '')}")
            doc_tokens = set(doc_norm_str.split())

            # Keyword overlap boost for informative words
            overlap = len(q_tokens.intersection(doc_tokens))
            keyword_boost = overlap * 0.04

            final_score = float(round(base_score + keyword_boost, 4))
            res_doc = dict(doc)
            res_doc["similarity_score"] = final_score
            ranked.append(res_doc)

        ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
        return ranked[:top_k]

    def get_top_document(self, query: str) -> Tuple[Optional[Dict[str, Any]], float]:
        results = self.retrieve(query, top_k=1)
        if results and results[0]["similarity_score"] > 0:
            return results[0], results[0]["similarity_score"]
        return None, 0.0
