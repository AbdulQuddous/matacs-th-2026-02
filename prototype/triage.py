"""Generic, deterministic evaluator of evidence-backed fields (no AI/API call).

Run from repository root: python prototype/triage.py
Thresholds, category scoring weights, and scoring methods are versioned config data.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def cap100(value: float) -> float:
    return max(0.0, min(100.0, value))


def passes(operator: str, actual, expected) -> bool:
    if operator == "eq":
        return actual == expected
    if operator == "min":
        return actual >= expected
    if operator == "max":
        return actual <= expected
    raise ValueError(f"Unsupported eligibility operator: {operator}")


def score_criterion(rule: dict, record: dict, qualified: list[dict]) -> float:
    method = rule["method"]
    if method == "ratio_to_target":
        return cap100(100 * record[rule["field"]] / rule["target"])
    if method == "ratio_to_batch_min":
        field = rule["field"]
        return cap100(100 * min(r[field] for r in qualified) / record[field])
    if method == "mean_of_capped_targets":
        ratios = [min(record[f] / target, 1) for f, target in zip(rule["fields"], rule["targets"], strict=True)]
        return cap100(100 * sum(ratios) / len(ratios))
    if method == "fraction_true":
        return cap100(100 * sum(record[f] is True for f in rule["fields"]) / len(rule["fields"]))
    raise ValueError(f"Unsupported scoring method: {method}")


def evaluate(config: dict, proposals: list[dict]) -> list[dict]:
    criteria = config["criteria"]
    if not criteria or len({c["id"] for c in criteria}) != len(criteria):
        raise ValueError("Criteria must be nonempty and have unique ids")
    if abs(sum(c["weight"] for c in criteria) - 1.0) > 1e-9 or any(c["weight"] < 0 for c in criteria):
        raise ValueError("Weights must be nonnegative and add to 1")

    ready, excluded = [], []
    for p in proposals:
        status, problems = None, []
        for check in config["eligibility_checks"]:
            actual = p.get(check["field"])
            if actual is None:
                problems.append(f"Unconfirmed eligibility field: {check['field']}.")
            elif not passes(check["operator"], actual, check["value"]):
                status = "ineligible"
                problems = [check["failure"]]
                break

        if status != "ineligible":
            if p["injection_detected"]:
                problems.append("Embedded attempt to influence ranking ignored; reviewer verification required.")
            if p["experience_date_ambiguity"]:
                problems.append("Qualifying five-year project count lacks sufficient evidence.")
            for criterion in criteria:
                fields = ([criterion["field"]] if "field" in criterion else criterion.get("fields", []))
                for field in fields:
                    if p.get(field) is None and criterion["method"] != "fraction_true":
                        problem = f"Scoring field {field} is missing or unverified."
                        if problem not in problems:
                            problems.append(problem)
                    if isinstance(p.get(field), (int, float)) and not isinstance(p.get(field), bool) and p[field] <= 0:
                        problems.append(f"Invalid nonpositive numeric value for {field}.")
            if problems:
                status = "flagged"

        if status:
            excluded.append({"proposal": p["proposal"], "rank": None,
                             "status": status, "score": None, "reason": " ".join(problems)})
        else:
            ready.append(p)

    weighted = []
    for p in ready:
        component_scores = {criterion["id"]: score_criterion(criterion, p, ready) for criterion in criteria}
        score = round(sum(component_scores[c["id"]] * c["weight"] for c in criteria), 2)
        weighted.append((score, p, component_scores))
    weighted.sort(key=lambda item: (-item[0], item[1]["proposal"]))

    ranked = []
    for rank, (score, p, component_scores) in enumerate(weighted, 1):
        project_count = p["eligible_project_count"]
        team_checks = next(c["fields"] for c in criteria if c["id"] == "team")
        team_count = sum(p[field] is True for field in team_checks)
        if rank == 1:
            reason = (f"Best qualifying price and timeline; {project_count} relevant projects "
                      f"and {team_count}/{len(team_checks)} team-plan elements.")
        else:
            reason = (f"{project_count} relevant projects; CAD {p['price_cad']:,} and {p['weeks']} "
                      f"weeks, with a {p['workmanship_warranty_years']}-year workmanship "
                      f"warranty and {team_count}/{len(team_checks)} team-plan elements.")
        ranked.append({"proposal": p["proposal"], "rank": rank, "status": "ranked",
                       "score": score, "reason": reason})

    order = {"ranked": 0, "flagged": 1, "ineligible": 2}
    return sorted(ranked + excluded, key=lambda item: (order[item["status"]], item["rank"] or 999, item["proposal"]))


def main() -> None:
    config = json.loads((ROOT / "category_config.json").read_text(encoding="utf-8"))
    facts = json.loads((ROOT / "sample_features.json").read_text(encoding="utf-8"))
    print(json.dumps(evaluate(config, facts), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
