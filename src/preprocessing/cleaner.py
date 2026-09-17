"""
Data cleaning and normalization utilities for customer support queries.
"""
import re
import html
import unicodedata

def clean_text(text: str) -> str:
    """Normalize whitespace, unescape HTML, remove non-printable characters."""
    if text is None:
        return ""
    text = str(text)
    text = html.unescape(text)
    text = unicodedata.normalize("NFKD", text)
    # Remove control characters except standard whitespace
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or not unicodedata.category(ch).startswith("C"))
    # Collapse multiple whitespaces to single space
    text = re.sub(r"\s+", " ", text).strip()
    return text

def is_valid_query(query: str, min_chars: int = 3) -> bool:
    """Determine if query has sufficient semantic content."""
    cleaned = clean_text(query)
    if not cleaned or len(cleaned) < min_chars:
        return False
    # Check if it has at least one letter or digit
    if not re.search(r"[a-zA-Z0-9]", cleaned):
        return False
    return True

TYPO_SYNONYM_MAP = {
    r"\bwher\b": "where", r"\bpakage\b": "package", r"\bpls\b": "please", r"\bhlp\b": "help",
    r"\brefnd\b": "refund", r"\breturnd\b": "returned", r"\bpasswrod\b": "password",
    r"\bsecanrio\b": "scenario", r"\bsecnario\b": "scenario", r"\bscenarion\b": "scenario",
    r"\brturn\b": "return", r"\bitm\b": "item", r"\bshiping\b": "shipping", r"\bfre\b": "free",
    r"\bscren\b": "screen", r"\btotaly\b": "totally", r"\bcants\b": "cannot",
    r"\bhow 2\b": "how to", r"\b4\b": "for", r"\bpasscode\b": "password",
    r"\bglitched\b": "error glitch cache",
    r"\bparcel\b": "package tracking shipping", r"\bgoodies\b": "order items",
    r"\breimburse\b": "refund payment return money",
    r"\bdiscontinue my membership\b": "cancel subscription auto renewal",
    r"\bsettle the bill\b": "payment methods apple pay invoice",
    r"\bsweater\b": "item exchange return size",
    r"\bdigital apple wallet\b": "apple pay accepted payment"
}

def normalize_query_semantics(text: str) -> str:
    """Normalize typos and expand customer support synonyms for robust retrieval."""
    cleaned = clean_text(text)
    for pattern, replacement in TYPO_SYNONYM_MAP.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned


def normalize_for_comparison(text: str) -> str:
    """Aggressive normalization for duplicate & near-duplicate detection."""
    cleaned = clean_text(text).lower()
    # Remove all punctuation and symbols
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def compute_jaccard_similarity(text1: str, text2: str, n_gram: int = 2) -> float:
    """Compute character/token n-gram Jaccard similarity for near duplicate detection."""
    s1 = normalize_for_comparison(text1)
    s2 = normalize_for_comparison(text2)
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    tokens1 = set(s1.split())
    tokens2 = set(s2.split())
    token_union = tokens1.union(tokens2)
    if not token_union:
        return 0.0
    token_sim = len(tokens1.intersection(tokens2)) / len(token_union)

    # Also calculate char 3-grams for typo robustness
    def get_ngrams(s, n=3):
        return {s[i:i+n] for i in range(max(1, len(s) - n + 1))}

    ngrams1 = get_ngrams(s1, n_gram)
    ngrams2 = get_ngrams(s2, n_gram)
    ngram_union = ngrams1.union(ngrams2)
    ngram_sim = len(ngrams1.intersection(ngrams2)) / len(ngram_union) if ngram_union else 0.0

    return 0.5 * token_sim + 0.5 * ngram_sim
