# Customer Support Agent - Failure & Reliability Analysis

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

### Category: Ambiguous (Failure Count: 2)
- **Query**: "It isn't working."
  - **Expected Behavior**: `clarify`
  - **Agent Response**: "Could you provide more details about what isn't working, such as whether you are having trouble logging in, experiencing a website error, or having an issue with a product?"
  - **Root Cause**: Expected clarify, but agent generated standard response.
  - **Mitigation Strategy**: Improve intent thresholding or expand query synonym mappings.

- **Query**: "Can I change something on my account?"
  - **Expected Behavior**: `clarify`
  - **Agent Response**: "Accounts locked due to multiple failed logins unlock automatically after 30 minutes, or can be unlocked via two-factor authentication (2FA) verification. Verify customer identity via 2FA security code, check account lock flags, and reset session tokens if necessary."
  - **Root Cause**: Expected clarify, but agent generated standard response.
  - **Mitigation Strategy**: Improve intent thresholding or expand query synonym mappings.

## 3. Reliability Principles Implemented in this Agent

1. **Zero Hallucination Guardrail**:
   - System prompts and deterministic fallback synthesis explicitly forbid generating facts outside the retrieved knowledge base.
2. **Explicit Confidence Gating**:
   - Cosine similarity below threshold (0.22) automatically triggers a safe abstention rather than an extrapolated answer.
3. **Dedicated Ambiguity Disambiguator**:
   - Queries with <= 2 words lacking a named entity trigger a clarification dialogue.
4. **Adversarial Input Sanitization**:
   - Prompt injections and jailbreak patterns are intercepted prior to knowledge retrieval, preserving prompt integrity.
