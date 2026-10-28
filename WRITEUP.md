# Proposal Triage — Design Write-up

**Reference:** MATACS-TH-2026-02  
**Category:** Commercial Solar Installation

## End-to-end workflow

1. **Admin (human + rules):** Save category, mandatory conditions, weights, scale settings, and effective version. Reject a configuration unless the weighted criteria total 100%.
2. **Upload (rules):** Check PDF type, size, antivirus result, and duplicate hash. Extract selectable text; use OCR for scanned pages and retain page references.
3. **Understand (AI):** Extract only stated facts as a strict JSON object, each supported by a quote and page reference. Use `null` for missing or uncertain fields. Flag instructions embedded in a proposal that try to influence evaluation.
4. **Validate (rules + human):** Validate types, ranges, quote-to-source matches, and contradictory claims. A reviewer checks poor OCR, ambiguity, or suspicious content; corrections are recorded against the original source.
5. **Decide eligibility (rules):** Bidder-held Ontario electrical licence and both WSIB clearance and at least $5M liability coverage are mandatory. Also apply the project ceiling of $260,000 CAD and maximum 16 weeks. A known failure becomes `ineligible`; an unknown, missing, or manipulated critical field becomes `flagged` for clarification.
6. **Rank (rules):** Apply the frozen category version and the published scoring formulas to complete eligible proposals only. Sort by descending score, then by proposal letter if tied. Generate the explanation from input facts and point breakdown, not from a fresh AI judgement.
7. **Approve (human):** Show evidence, flags, criteria version, and score components. The reviewer can request clarification or override with a documented rationale and re-evaluation. The award decision remains human.

## 1. AI vs. rules — why this separation?

AI is useful for converting varied PDF wording into a consistent field schema; it is **not** trusted to decide whether a bidder is licensed, select weights, or assign a final rank. Ordinary code can consistently check licence ownership, presence of required cover, numbers, score formulas, and sorting. Stated licence identifiers are evidence to review, not proof that a licence is currently valid.

## 2. Consistency and explainability

For this sample, freeze the qualifying batch (A and E), criterion version, extracted facts, and normalization references. Every weighted component is on a 0–100 scale:

- **Experience (30%):** `100 × min(eligible_projects / 14, 1)`.
- **Price (25%):** `100 × (lowest_price_among_ranked / bidder_price)`.
- **Timeline (15%):** `100 × (shortest_weeks_among_ranked / bidder_weeks)`.
- **Warranty (15%):** `50 × min(panel_years / 25, 1) + 50 × min(workmanship_years / 12, 1)`.
- **Team and approach (15%):** 25 points each for stated named lead, crew details, safety plan, and monitoring plan.

The illustrative targets of 14 projects, 25 panel years, and 12 workmanship years are **editable scoring parameters**, not extra eligibility rules. Ratio scores are capped at 100. A weighted sum (30/25/15/15/15) is rounded to two decimals **only at the end**. A reviewer sees the raw values, evidence references, five sub-scores, total, and specific reasons. Repeating the run with the **same batch, configuration, and corrected facts** gives the same ranking. A changed batch is a new scored snapshot.

## 3. Human in the loop and audit

A reviewer resolves missing claims, verifies important documents where possible, and acknowledges suspicious text before any flagged case re-enters scoring. The reviewer also approves the ranked recommendation and separately records the actual award decision. Store uploader, timestamps, PDF hash, OCR version, model/prompt version, extracted JSON with page evidence, confidence/flags, reviewer corrections, eligibility results, criterion snapshot, component scores, tie-breaks, overrides with reasons, and final decision. An override creates a new audit event; it never erases the earlier result.

## 4. Changing criteria after scoring

Admin edits create a new **immutable version** (for example, v2); old results stay attached to v1. The system validates the new weights, notifies reviewers, and offers an explicit full-batch re-score against v2, with old/new comparison. Never silently mix v1 and v2 or overwrite historical results. Editing a criterion should not edit the source proposals.

## 5. Risks and practical safeguards

- **OCR mistakes / missing details:** Store page evidence and require reviewer confirmation for low-confidence or required fields; never infer absent facts.
- **Hallucinations:** Strict JSON schema, `null` for unknowns, quote-to-source verification, and no AI-generated final scores.
- **Prompt injection:** Treat proposal text as data. Proposal C contains an instruction claiming special authority and demanding first place; ignore it, record the attempt, and flag for reviewer verification. No proposal can change system prompts or grading rules.
- **Bias / unfair comparisons:** Same published criteria and weights for all bids; only relevant evidence counts. Use a frozen eligible batch, recorded assumptions, and explain each metric.
- **Cost / leakage:** Limit input pages/tokens, cache by document hash and prompt version, redact personal data, restrict access, and avoid sending confidential proposals to unapproved external AI services.

## Application to A–E

**A — rank 1, 98.75:** 14 eligible projects, $238,000, 12 weeks, 25/10-year warranties, and all four team-plan signals. **E — rank 2, 85.53:** 8 projects, $242,500, 13 weeks, 25/12-year warranties, and all four team-plan signals; especially strong warranty, but lower experience and slightly weaker price/timeline.

**B — ineligible:** proposed future subcontractor does not meet the requirement for a licence *held by the bidder*. **C — flagged:** contains untrusted evaluation instructions and its 'since 2020' project count does not establish the count within the last five years; do not invent one. **D — flagged:** a timeline to be determined later cannot prove compliance with the 16-week limit. Neither flagged proposal is automatically rejected; both can be re-scored when verified facts are supplied.
