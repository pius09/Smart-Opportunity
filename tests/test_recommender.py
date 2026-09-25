"""Tests for the recommendation engine."""
from datetime import date, timedelta
from app.extensions import db
from app.models.student import Student
from app.models.administrator import Administrator
from app.models.opportunity import Opportunity
from app.services.recommender import generate_recommendations_for


def _setup_data():
    """Helper: create admin, student, and two opportunities.

    NOTE: assumes an application context is already active (it is, thanks
    to the pytest `app` fixture). Returns ORM objects still bound to the
    current session.
    """
    a = Administrator(full_name='Admin', email='a@a.com')
    a.set_password('pw')
    db.session.add(a)
    db.session.commit()

    s = Student(
        full_name='Aliyu',
        email='s@s.com',
        department='Computer Science',
        level='400',
        cgpa=4.5,
        skills='python, machine learning, data analysis',
        interests='artificial intelligence, research',
    )
    s.set_password('pw')
    db.session.add(s)
    db.session.commit()

    # Opportunity 1: strongly matches student's interests
    o1 = Opportunity(
        title='AI Research Scholarship',
        category='scholarship',
        description='For students interested in artificial intelligence '
                    'and machine learning research',
        provider='ABC Foundation',
        deadline=date.today() + timedelta(days=30),
        min_cgpa=3.5,
        eligible_department='Computer Science',
        eligible_level='300, 400',
        admin_id=a.admin_id,
    )

    # Opportunity 2: poor match (wrong domain)
    o2 = Opportunity(
        title='Law Essay Competition',
        category='competition',
        description='Annual essay competition for law students on '
                    'constitutional law topics',
        provider='Nigerian Bar Association',
        deadline=date.today() + timedelta(days=45),
        min_cgpa=4.0,
        eligible_department='Law',
        eligible_level='200, 300',
        admin_id=a.admin_id,
    )

    db.session.add(o1)
    db.session.add(o2)
    db.session.commit()

    return s, o1, o2


def test_recommendations_are_generated(app):
    s, o1, o2 = _setup_data()
    recs = generate_recommendations_for(s)
    assert len(recs) == 2


def test_matching_opportunity_scores_higher(app):
    s, o1, o2 = _setup_data()
    recs = generate_recommendations_for(s)

    ai_rec = next(r for r in recs
                  if r.opportunity.title == 'AI Research Scholarship')
    law_rec = next(r for r in recs
                   if r.opportunity.title == 'Law Essay Competition')

    # AI scholarship should have higher similarity to a CS student
    assert float(ai_rec.similarity_score) > float(law_rec.similarity_score)


def test_eligibility_flags_are_correct(app):
    s, o1, o2 = _setup_data()
    recs = generate_recommendations_for(s)

    ai_rec = next(r for r in recs
                  if r.opportunity.title == 'AI Research Scholarship')
    law_rec = next(r for r in recs
                   if r.opportunity.title == 'Law Essay Competition')

    assert ai_rec.eligibility_status is True
    assert law_rec.eligibility_status is False
    assert 'Restricted to' in (law_rec.eligibility_reason or '')


def test_notifications_created_for_eligible_matches(app):
    from app.models.notification import Notification

    s, o1, o2 = _setup_data()
    generate_recommendations_for(s)

    notifs = Notification.query.filter_by(student_id=s.student_id).all()
    # Should create notifications for at least the eligible match
    assert len(notifs) >= 1
    assert any('AI Research Scholarship' in n.message for n in notifs)