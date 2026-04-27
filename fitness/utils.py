import math


def calculate_bmi(weight_kg, height_cm):
    """
    Standard BMI = kg / (m^2). Returns (bmi_value, category_label) or (None, None) if invalid.
    """
    if not weight_kg or not height_cm:
        return None, None
    try:
        w = float(weight_kg)
        h_cm = float(height_cm)
    except (TypeError, ValueError):
        return None, None
    if w <= 0 or h_cm <= 0:
        return None, None
    h_m = h_cm / 100.0
    bmi = w / (h_m * h_m)
    label = _bmi_category(bmi)
    return round(bmi, 1), label


def _bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal weight"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def _cm_to_inches(cm):
    return float(cm) / 2.54


def navy_body_fat_percent(gender, height_cm, waist_cm, neck_cm, hip_cm=None):
    """
    U.S. Navy body fat estimation. Profile stores cm; coefficients expect inches,
    so values are converted from cm to inches before applying the standard formulas.
    """
    if not all([gender, height_cm, waist_cm, neck_cm]):
        return None
    try:
        h = _cm_to_inches(height_cm)
        w = _cm_to_inches(waist_cm)
        n = _cm_to_inches(neck_cm)
    except (TypeError, ValueError):
        return None
    if h <= 0 or w <= 0 or n <= 0 or w <= n:
        return None

    g = (gender or "").lower()
    if g == "male":
        try:
            val = 86.010 * math.log10(w - n) - 70.041 * math.log10(h) + 36.76
        except (ValueError, ZeroDivisionError):
            return None
        return max(0.0, min(100.0, round(val, 1)))

    if g == "female":
        if hip_cm is None:
            return None
        try:
            hip = _cm_to_inches(hip_cm)
        except (TypeError, ValueError):
            return None
        if hip <= 0:
            return None
        try:
            val = (
                163.205 * math.log10(w + hip - n)
                - 97.684 * math.log10(h)
                - 78.387
            )
        except (ValueError, ZeroDivisionError):
            return None
        return max(0.0, min(100.0, round(val, 1)))

    return None


def estimated_calories_burned(duration_minutes, repeat_count):
    """Heuristic: duration * 5 * (repeat_count + 1)."""
    try:
        d = int(duration_minutes)
        r = int(repeat_count)
    except (TypeError, ValueError):
        return 0
    return max(0, d * 5 * (r + 1))
