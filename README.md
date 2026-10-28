# AI-Assisted Proposal Triage — Design Submission

**Candidate:** Abdul Quddous  
**Assessment reference:** MATACS-TH-2026-02  
**Time actually spent:** 48 Minutes
**Deliverable:** Design-only submission; no deployed application required.

## What this design does

An administrator defines a category's mandatory checks and weighted evaluation criteria. A reviewer uploads proposals, and an AI model extracts structured claims with supporting source locations. Deterministic code then performs eligibility checks and computes comparable scores. Incomplete or suspicious cases go to a person for review. A person, never the model, makes the award decision.

### Files

- [Process-flow diagram](diagram/triage_flow.png) — upload-to-output workflow with AI, rules, and human checkpoints.
- [Design write-up](WRITEUP.md) — answers to the five assessment questions, scoring assumptions, and sample results.
- [Exact AI prompts](PROMPTS.md) — system and user prompts for evidence-based extraction.
- [Expected ranking](ranking.json) — machine-readable results for proposals A–E.
- [Optional rule-engine demonstration](prototype/triage.py) — dependency-free reproducibility check using [structured sample features](prototype/sample_features.json) and [versioned settings](prototype/category_config.json); this does not call an AI model.

## Expected result

| Proposal | Outcome | Score / 100 | Why |
|---|---|---:|---|
| A | Rank 1 | 98.75 | Best qualifying price and timeline, with most relevant projects. |
| E | Rank 2 | 85.53 | Strong team, warranty, and monitoring; fewer qualifying projects. |
| C | Flagged | — | An embedded ranking instruction is untrusted, and the number of projects within the exact five-year window is unclear. |
| D | Flagged | — | No committed duration to verify the 16-week limit. |
| B | Ineligible | — | Does not show the required licence held by the bidder itself. |

A **flagged** proposal is paused, not rejected: a reviewer can obtain better evidence and re-run the same version of the rules. An **ineligible** proposal fails a mandatory condition or an explicit ceiling and is not scored. A reviewer cannot make an ineligible bid eligible by simply editing a score.

## How I used AI tools

I used ChatGPT to organize the workflow, draft the extraction prompt, and check that the write-up covers the assessment's questions. I reviewed the eligibility logic rather than accepting a pricing-first shortcut: treating a future subcontractor's licence as sufficient for proposal B would contradict the rule that **the bidder** must hold the licence, so the design rejects that shortcut. I also required the model to ignore proposal C's embedded ranking instruction instead of treating it as authority.

> **Before submitting:** Review these AI-use statements and edit them to match what you actually did. Replace the time-spent placeholder with your real elapsed working time; do not report an invented duration.

## Reproduce the scores (optional)

Python 3.10+ and standard library only:

```bash
python prototype/triage.py
python -m unittest discover -s prototype -p 'test_*.py'
```

The demonstration uses pre-extracted, reduced features rather than copying the source proposals. It illustrates how the rule engine works; the AI extraction stage is specified in `PROMPTS.md`, not implemented in this script.

## Assumptions

The numeric normalization and tie-break rules are **illustrative category settings**, not values prescribed in the assessment. The example treats counts explicitly described as occurring *since 2021* as meeting the five-year lookback at year-level granularity; exact completion dates should be checked before an award. Counts described only as *since 2020* do not establish the five-year count without additional evidence. The scoring batch is frozen before normalization to ensure a repeat run yields the same values.

All bid facts are claims extracted from fictional submissions, not independently verified registrations, insurance records, or project references.
