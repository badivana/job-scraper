# Evaluation

## Purpose

To outline how we evaluate the effectiveness of our AI components, including embedding quality, matching relevance, and generated text (cover letters, emails, skill‑gap analysis).

## Contents

- Embedding Evaluation
- Matching Evaluation
- Generation Evaluation
- A/B Testing
- Monitoring Metrics
- Human-in-the-loop Feedback

## Embedding Evaluation

We assess embedding quality using:
- **Intrinsic metrics**: cosine similarity similarity benchmarks on a labeled dataset of resume‑job pairs (e.g., from annotated samples).
- **Extrinsic metrics**: impact on matching precision/recall in downstream tasks.

We maintain a validation set of manually labeled matches and compute Mean Average Precision (MAP) and Normalized Discounted Cumulative Gain (NDCG) at various thresholds.

## Matching Evaluation

Matching is evaluated by:
- **Offline**: comparing our hybrid score against ground‑truth labels (recruiter judgments) on a hold‑out set.
- **Online**: click‑through rates, application conversion rates, and user satisfaction surveys.

We track the distribution of match scores and the rate at which users interact with high‑score jobs.

## Generation Evaluation

For cover letters and cold emails, we use:
- **Automated metrics**: BLEU, ROUGE, and BERTScore against reference texts (when available).
- **Human evaluation**: fluency, relevance, tone, and correctness rated by internal annotators or via crowdsourcing.
- **A/B testing**: variant subject lines or calls‑to‑action to measure response rates.

## A/B Testing

We run controlled experiments to test changes to:
- Embedding model or preprocessing.
- Matching weight coefficients (α, β, γ, δ).
- Prompt wording or temperature for LLMs.

Experiments are gated by feature flags and analyzed with statistical significance (e.g., chi‑test or t‑test).

## Monitoring Metrics

Key metrics are logged and alerted on:
- Embedding generation latency and failure rate.
- Matching API latency and error rate.
- LLM request tokens, cost, and latency.
- Percentage of requests falling back to keyword‑only scoring.

## Human-in-the-loop Feedback

Users can provide explicit feedback (thumbs up/down) on job recommendations and generated content. This feedback is stored and periodically reviewed to:
- Retrain or fine‑tune ranking models (if we move to learned ranking).
- Improve prompt templates.
- Identify systematic biases or errors.
