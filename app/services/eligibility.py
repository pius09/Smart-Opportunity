"""Rule-based eligibility checker.

Compares a student's declared attributes against the explicit eligibility
criteria attached to an opportunity. Returns (is_eligible, reason_string).
"""


def _split(value):
    """Split a comma-separated string into a list of lowercase tokens."""
    if not value:
        return []
    return [v.strip().lower() for v in str(value).split(',') if v.strip()]


def check_eligibility(student, opportunity):
    """Return (eligible: bool, reason: str).

    reason is an empty string if eligible, otherwise a human-readable
    explanation of every rule the student failed.
    """
    reasons = []

    # --- CGPA check ---
    if opportunity.min_cgpa is not None and student.cgpa is not None:
        try:
            if float(student.cgpa) < float(opportunity.min_cgpa):
                reasons.append(
                    f"Minimum CGPA required: {float(opportunity.min_cgpa):.2f}"
                )
        except (TypeError, ValueError):
            pass

    # --- Department check ---
    depts = _split(opportunity.eligible_department)
    if depts and student.department:
        if student.department.strip().lower() not in depts:
            reasons.append(
                f"Restricted to: {opportunity.eligible_department}"
            )

    # --- Level of study check ---
    levels = _split(opportunity.eligible_level)
    if levels and student.level:
        if str(student.level).strip().lower() not in levels:
            reasons.append(
                f"Restricted to level: {opportunity.eligible_level}"
            )

    if reasons:
        return False, '; '.join(reasons)
    return True, ''