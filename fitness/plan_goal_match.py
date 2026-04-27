"""
Heuristic parsing of free-text 7-day plans and profile goals for a simple goal-match score.
Avoids overfitting to one Markdown shape: uses day-like headers, keyword density, and numeric hints.
"""

from __future__ import annotations

import re
import statistics
from typing import Any

DAY_HEADER = re.compile(
    r"(?mi)^#{1,3}\s*(?:"
    r"day\s*\d+|monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    r")\b.*$"
)
WORKOUT_KW = re.compile(
    r"\b(workouts?|training|cardio|strength|lift(?:ing)?|gym|hiit|run(?:ning)?|jog|walk(?:ing)?|"
    r"exercise|reps?|sets?|squats?|deadlifts?|push[\s-]?ups?|yoga|mobility)\b",
    re.I,
)
MEAL_KW = re.compile(
    r"\b(meals?|breakfast|lunch|dinner|snacks?|recipe|eat|food|nutrition|"
    r"smoothie|oatmeal|chicken|salad|rice|vegetables?)\b",
    re.I,
)
CAL_NUM = re.compile(
    r"(?:~|around|about|approx\.?)?\s*(\d{3,4})\s*(?:kcal|calories?|\bcals?\b)(?!\s*mg)",
    re.I,
)
CAL_NUM_REVERSE = re.compile(r"(?:kcal|calories?|\bcals?\b)\s*[:\-]?\s*(\d{3,4})", re.I)
PROTEIN_G = re.compile(r"(\d{2,3})\s*(?:g|grams?)\s*(?:of\s*)?protein", re.I)
PROTEIN_MENTION = re.compile(r"\b(high[\s-]?protein|protein|grams?\s*protein|g\s*protein)\b", re.I)
RECOVERY_KW = re.compile(r"\b(rest|recovery|sleep|stretch|foam roll|active recovery)\b", re.I)


def extract_profile_targets(goals_text: str) -> dict[str, int]:
    """Pull optional numeric targets from free-form fitness_goals."""
    t = (goals_text or "").strip()
    if not t:
        return {}
    low = t.lower()
    out: dict[str, int] = {}

    for pattern in (
        r"(?:target|eat|aim|around|~|at)\s*(\d{3,4})\s*(?:kcal|\bcal\b|calories?)\b",
        r"(\d{3,4})\s*(?:kcal|daily calories?|calories?\s*(?:per\s*day|a\s*day)?)\b",
    ):
        m = re.search(pattern, low)
        if m:
            val = int(m.group(1))
            if 800 <= val <= 7000:
                out["target_calories"] = val
                break

    for pattern in (
        r"(\d{2,3})\s*(?:g|grams?)\s*(?:of\s*)?(?:daily\s*)?protein",
        r"protein\s*(?:target|goal)?\s*[:\-]?\s*(\d{2,3})\s*g?",
        r"(\d{2,3})\s*g\s*protein",
    ):
        m = re.search(pattern, low)
        if m:
            val = int(m.group(1))
            if 40 <= val <= 400:
                out["target_protein_g"] = val
                break

    for pattern in (
        r"(\d)\s*(?:day|days|time|times|x)?\s*(?:per|a|\/)\s*week",
        r"(\d)\s*(?:workouts?|training sessions?)\s*(?:per|a|\/)\s*week",
        r"(?:workouts?|training)\s*[:\-]?\s*(\d)\s*(?:x|\*|per)\s*week",
        r"(\d)\s*x\s*(?:per\s*)?week",
    ):
        m = re.search(pattern, low)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 7:
                out["workouts_per_week"] = val
                break

    return out


def resolve_profile_targets(profile: Any) -> dict[str, int]:
    """
    Merge free-text `fitness_goals` with optional structured profile fields.
    Structured values override parsed numbers when set.
    """
    parsed = extract_profile_targets(getattr(profile, "fitness_goals", None) or "")
    out = dict(parsed)
    gc = getattr(profile, "goal_calories", None)
    if gc is not None:
        out["target_calories"] = int(gc)
    gp = getattr(profile, "goal_protein_g", None)
    if gp is not None:
        out["target_protein_g"] = int(gp)
    gw = getattr(profile, "goal_workouts_per_week", None)
    if gw is not None:
        out["workouts_per_week"] = int(gw)
    return out


def _day_blocks(plan_text: str) -> list[str]:
    """Split on markdown headings that look like a day section."""
    lines = plan_text.splitlines()
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if DAY_HEADER.match(line) and current:
            blocks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    if len(blocks) <= 1 and plan_text.strip():
        return [plan_text]
    return blocks


def parse_plan_estimates(plan_text: str) -> dict[str, Any]:
    text = plan_text or ""
    low = text.lower()
    blocks = _day_blocks(text)

    workout_day_indices: list[int] = []
    meal_day_indices: list[int] = []
    for i, block in enumerate(blocks):
        if WORKOUT_KW.search(block):
            workout_day_indices.append(i)
        if MEAL_KW.search(block):
            meal_day_indices.append(i)

    day_headers = len(DAY_HEADER.findall(text))
    numbered_day_heads = len(re.findall(r"(?mi)^#{2,3}\s*day\s*[1-7]\b", text))
    structured_days = max(day_headers, len(blocks) if blocks else 0, min(7, numbered_day_heads))
    structured_days = min(7, structured_days) if structured_days else 0

    cal_vals: list[int] = []
    for pat in (CAL_NUM, CAL_NUM_REVERSE):
        for m in pat.finditer(low):
            v = int(m.group(1))
            if 800 <= v <= 7000:
                cal_vals.append(v)
    cal_median = int(statistics.median(cal_vals)) if cal_vals else None

    protein_grams_in_plan: list[int] = []
    for m in PROTEIN_G.finditer(text):
        v = int(m.group(1))
        if 40 <= v <= 400:
            protein_grams_in_plan.append(v)
    protein_sample = int(statistics.median(protein_grams_in_plan)) if protein_grams_in_plan else None

    return {
        "structured_day_count": structured_days,
        "day_block_count": len(blocks),
        "workout_day_count": len(set(workout_day_indices)),
        "meal_day_count": len(set(meal_day_indices)),
        "calorie_numbers_found": sorted(set(cal_vals))[:8],
        "implied_calories_median": cal_median,
        "protein_mentions": bool(PROTEIN_MENTION.search(low)),
        "protein_grams_sample": protein_sample,
        "recovery_mentioned": bool(RECOVERY_KW.search(low)),
    }


def _clamp_score(x: float) -> int:
    return max(0, min(100, int(round(x))))


def _workout_score(target: int, implied_days: int) -> int:
    diff = abs(implied_days - target)
    return _clamp_score(100 - diff * 18)


def _calorie_score(target: int, median_plan: int | None) -> tuple[int, str]:
    if median_plan is None:
        return 50, "no_calorie_numbers"
    diff_pct = abs(median_plan - target) / max(target, 1) * 100
    return _clamp_score(100 - diff_pct * 2.5), "compared"


def _protein_score(target_g: int, plan_sample: int | None, mentioned: bool) -> tuple[int, str]:
    if plan_sample is not None:
        diff = abs(plan_sample - target_g)
        return _clamp_score(100 - diff * 1.2), "grams_in_plan"
    if mentioned:
        return 72, "mentioned_only"
    return 35, "weak_signal"


def _completeness_score(est: dict[str, Any]) -> int:
    s = 0
    if est["structured_day_count"] >= 6:
        s += 35
    elif est["structured_day_count"] >= 4:
        s += 22
    elif est["structured_day_count"] >= 1:
        s += 12
    if est["workout_day_count"] >= 1:
        s += 28 + min(12, est["workout_day_count"] * 2)
    if est["meal_day_count"] >= 1:
        s += 22 + min(10, est["meal_day_count"] * 2)
    if est["recovery_mentioned"]:
        s += 15
    return _clamp_score(s)


def compute_goal_match(
    plan_text: str,
    *,
    profile: Any | None = None,
    profile_goals_text: str | None = None,
) -> dict[str, Any]:
    """
    Returns goal_match dict suitable for JSON API and JSONField breakdown.

    Pass ``profile`` to use structured goal fields plus ``fitness_goals`` parsing
    (structured fields win on overlap). If ``profile`` is omitted, only
    ``profile_goals_text`` is parsed.
    """
    if profile is not None:
        targets = resolve_profile_targets(profile)
    else:
        targets = extract_profile_targets(profile_goals_text or "")
    est = parse_plan_estimates(plan_text)
    matched: list[str] = []
    missed: list[str] = []
    dimension_scores: list[float] = []
    weights: list[float] = []

    tw = targets.get("workouts_per_week")
    if tw is not None:
        implied = est["workout_day_count"]
        ws = _workout_score(tw, implied)
        dimension_scores.append(float(ws))
        weights.append(1.0)
        if ws >= 75:
            matched.append(
                f"Workouts: about {implied} day(s) in the plan look training-focused; your goal is {tw} per week."
            )
        else:
            missed.append(
                f"Workouts: the plan highlights training on about {implied} day(s); your goal is {tw} per week."
            )

    tc = targets.get("target_calories")
    if tc is not None:
        cs, mode = _calorie_score(tc, est["implied_calories_median"])
        dimension_scores.append(float(cs))
        weights.append(1.0)
        if mode == "no_calorie_numbers":
            missed.append(
                f"Calories: your target is ~{tc} kcal/day, but the plan has no clear calorie numbers to compare."
            )
        else:
            med = est["implied_calories_median"]
            if cs >= 78:
                matched.append(
                    f"Calories: plan figures (~{med} kcal) are close to your ~{tc} kcal target."
                )
            else:
                missed.append(
                    f"Calories: plan figures (~{med} kcal) drift from your ~{tc} kcal target."
                )

    tp = targets.get("target_protein_g")
    if tp is not None:
        ps, mode = _protein_score(tp, est["protein_grams_sample"], est["protein_mentions"])
        dimension_scores.append(float(ps))
        weights.append(0.85)
        if mode == "weak_signal":
            missed.append(
                f"Protein: your goal is ~{tp}g; the plan does not surface strong protein cues or gram targets."
            )
        elif mode == "mentioned_only":
            matched.append(f"Protein: your goal is ~{tp}g; the plan discusses protein (no exact gram match parsed).")
        else:
            sample = est["protein_grams_sample"]
            if ps >= 75:
                matched.append(
                    f"Protein: parsed plan hints (~{sample}g) align reasonably with your ~{tp}g target."
                )
            else:
                missed.append(
                    f"Protein: parsed plan hints (~{sample}g) are off vs your ~{tp}g target."
                )

    if weights:
        total_w = sum(weights)
        score = _clamp_score(sum(s * w for s, w in zip(dimension_scores, weights)) / total_w)
    else:
        score = _completeness_score(est)
        matched.append(
            "No numeric targets: add optional calorie / protein / workouts fields on your profile, "
            "or include numbers in fitness goals (e.g. 2000 kcal, 5×/week, 140g protein). "
            "Score reflects plan completeness instead."
        )
        if est["structured_day_count"] < 5:
            missed.append("Structure: fewer than five clear day sections — harder to verify a full week.")

    breakdown = {
        "matched": matched,
        "missed": missed,
        "plan_estimates": est,
        "profile_targets": targets,
    }
    return {"score": score, "breakdown": breakdown}
