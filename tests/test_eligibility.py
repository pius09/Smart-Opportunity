"""Tests for the rule-based eligibility checker."""
from app.services.eligibility import check_eligibility


class FakeStudent:
    def __init__(self, cgpa, department, level):
        self.cgpa = cgpa
        self.department = department
        self.level = level


class FakeOpportunity:
    def __init__(self, min_cgpa=None, eligible_department=None, eligible_level=None):
        self.min_cgpa = min_cgpa
        self.eligible_department = eligible_department
        self.eligible_level = eligible_level


def test_eligible_when_no_criteria():
    s = FakeStudent(3.0, 'Computer Science', '300')
    o = FakeOpportunity()
    eligible, reason = check_eligibility(s, o)
    assert eligible is True
    assert reason == ''


def test_ineligible_below_cgpa():
    s = FakeStudent(2.5, 'Computer Science', '300')
    o = FakeOpportunity(min_cgpa=3.5)
    eligible, reason = check_eligibility(s, o)
    assert eligible is False
    assert 'Minimum CGPA' in reason


def test_ineligible_wrong_department():
    s = FakeStudent(4.5, 'Law', '300')
    o = FakeOpportunity(eligible_department='Computer Science, Mathematics')
    eligible, reason = check_eligibility(s, o)
    assert eligible is False
    assert 'Restricted to' in reason


def test_ineligible_wrong_level():
    s = FakeStudent(4.5, 'Computer Science', '500')
    o = FakeOpportunity(eligible_level='100, 200')
    eligible, reason = check_eligibility(s, o)
    assert eligible is False
    assert 'level' in reason.lower()


def test_multiple_failures_reported_together():
    s = FakeStudent(2.0, 'Law', '500')
    o = FakeOpportunity(min_cgpa=3.5,
                        eligible_department='Computer Science',
                        eligible_level='100, 200')
    eligible, reason = check_eligibility(s, o)
    assert eligible is False
    assert 'Minimum CGPA' in reason
    assert 'Restricted to' in reason
    assert 'level' in reason.lower()