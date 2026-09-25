"""Tests for database models."""
from datetime import date, timedelta
from app.extensions import db
from app.models.student import Student
from app.models.administrator import Administrator
from app.models.opportunity import Opportunity


def test_student_password_hashing(app):
    with app.app_context():
        s = Student(full_name='Test', email='t@t.com',
                    department='CS', level='400', cgpa=4.0)
        s.set_password('secret123')
        db.session.add(s)
        db.session.commit()

        assert s.password_hash != 'secret123'
        assert s.check_password('secret123') is True
        assert s.check_password('wrong') is False


def test_student_profile_text(app):
    with app.app_context():
        s = Student(full_name='A', email='a@a.com',
                    department='Computer Science', level='400',
                    cgpa=4.0, skills='python, data',
                    interests='ai, research', location='dutse')
        text = s.profile_text()
        assert 'computer science' in text
        assert 'python' in text
        assert 'ai' in text


def test_opportunity_days_remaining(app):
    with app.app_context():
        a = Administrator(full_name='Admin', email='admin@a.com')
        a.set_password('pw')
        db.session.add(a)
        db.session.commit()

        o = Opportunity(title='Test', category='scholarship',
                        description='desc', provider='prov',
                        deadline=date.today() + timedelta(days=10),
                        admin_id=a.admin_id)
        db.session.add(o)
        db.session.commit()

        assert o.days_remaining() == 10


def test_duplicate_email_rejected(app):
    with app.app_context():
        s1 = Student(full_name='A', email='same@a.com',
                     department='CS', level='400', cgpa=4.0)
        s1.set_password('pw')
        db.session.add(s1)
        db.session.commit()

        s2 = Student(full_name='B', email='same@a.com',
                     department='CS', level='400', cgpa=4.0)
        s2.set_password('pw')
        db.session.add(s2)
        try:
            db.session.commit()
            assert False, 'Duplicate email was accepted'
        except Exception:
            db.session.rollback()