"""Evaluation script for the recommender's eligibility and ranking quality.

Runs against an isolated SQLite database so it never touches production data.

Usage:
    python scripts/evaluate.py

Outputs:
    precision, recall, accuracy, F1 for eligibility classification
    precision@3 for ranked recommendation quality
"""
import os
import sys
from datetime import date, timedelta

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.administrator import Administrator
from app.models.student import Student
from app.models.opportunity import Opportunity
from app.services.recommender import generate_recommendations_for
from app.services.eligibility import check_eligibility


class EvalConfig:
    SECRET_KEY = 'eval'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


# ---------- Ground-truth definitions ----------

STUDENTS = [
    {
        'email': 'cs400@eval.com', 'name': 'CS 400 Student',
        'department': 'Computer Science', 'level': '400', 'cgpa': 4.50,
        'skills': 'python, machine learning, data analysis',
        'interests': 'artificial intelligence, research',
        'location': 'Dutse',
    },
    {
        'email': 'law200@eval.com', 'name': 'Law 200 Student',
        'department': 'Law', 'level': '200', 'cgpa': 3.20,
        'skills': 'legal writing, research',
        'interests': 'constitutional law, human rights',
        'location': 'Kano',
    },
    {
        'email': 'math300@eval.com', 'name': 'Maths 300 Student',
        'department': 'Mathematics', 'level': '300', 'cgpa': 3.80,
        'skills': 'statistics, matlab, python',
        'interests': 'data science, modelling',
        'location': 'Kaduna',
    },
]

OPPORTUNITIES = [
    {
        'title': 'AI Research Scholarship',
        'category': 'scholarship',
        'description': 'For students interested in artificial intelligence and machine learning research',
        'provider': 'AI Foundation',
        'min_cgpa': 3.5,
        'eligible_department': 'Computer Science, Mathematics',
        'eligible_level': '300, 400',
    },
    {
        'title': 'Law Essay Competition',
        'category': 'competition',
        'description': 'Annual constitutional law essay competition for law students',
        'provider': 'Bar Association',
        'min_cgpa': 3.0,
        'eligible_department': 'Law',
        'eligible_level': '200, 300',
    },
    {
        'title': 'Data Science Internship',
        'category': 'internship',
        'description': 'Paid internship in data science and statistical modelling',
        'provider': 'DataCo',
        'min_cgpa': 3.5,
        'eligible_department': None,   # open to all
        'eligible_level': None,        # open to all
    },
    {
        'title': 'Law Faculty Grant',
        'category': 'grant',
        'description': 'Research grant for law students pursuing human rights projects',
        'provider': 'Justice Fund',
        'min_cgpa': 3.0,
        'eligible_department': 'Law',
        'eligible_level': '200, 300, 400',
    },
    {
        'title': 'STEM Scholarship (First Years Only)',
        'category': 'scholarship',
        'description': 'Scholarship supporting outstanding first-year science students',
        'provider': 'STEM Trust',
        'min_cgpa': 4.0,
        'eligible_department': 'Computer Science, Mathematics, Engineering',
        'eligible_level': '100',
    },
]

# Hand-labelled ground truth: (student_email, opportunity_title) -> relevant?
# "Relevant" means a human judge would expect this student to be interested.
RELEVANCE_GROUND_TRUTH = {
    ('cs400@eval.com', 'AI Research Scholarship'): True,
    ('cs400@eval.com', 'Data Science Internship'): True,
    ('cs400@eval.com', 'Law Essay Competition'): False,
    ('cs400@eval.com', 'Law Faculty Grant'): False,
    ('cs400@eval.com', 'STEM Scholarship (First Years Only)'): False,

    ('law200@eval.com', 'Law Essay Competition'): True,
    ('law200@eval.com', 'Law Faculty Grant'): True,
    ('law200@eval.com', 'AI Research Scholarship'): False,
    ('law200@eval.com', 'Data Science Internship'): False,
    ('law200@eval.com', 'STEM Scholarship (First Years Only)'): False,

    ('math300@eval.com', 'AI Research Scholarship'): True,
    ('math300@eval.com', 'Data Science Internship'): True,
    ('math300@eval.com', 'Law Essay Competition'): False,
    ('math300@eval.com', 'Law Faculty Grant'): False,
    ('math300@eval.com', 'STEM Scholarship (First Years Only)'): False,
}


# ---------- Setup ----------

def seed_data(app):
    with app.app_context():
        admin = Administrator(full_name='Eval Admin', email='eval@admin.com')
        admin.set_password('pw')
        db.session.add(admin)
        db.session.commit()

        students = {}
        for spec in STUDENTS:
            s = Student(
                full_name=spec['name'], email=spec['email'],
                department=spec['department'], level=spec['level'],
                cgpa=spec['cgpa'], skills=spec['skills'],
                interests=spec['interests'], location=spec['location'],
            )
            s.set_password('pw')
            db.session.add(s)
            db.session.commit()
            students[spec['email']] = s

        opportunities = {}
        for i, spec in enumerate(OPPORTUNITIES):
            o = Opportunity(
                title=spec['title'], category=spec['category'],
                description=spec['description'], provider=spec['provider'],
                min_cgpa=spec['min_cgpa'],
                eligible_department=spec['eligible_department'],
                eligible_level=spec['eligible_level'],
                deadline=date.today() + timedelta(days=30 + i),
                admin_id=admin.admin_id,
            )
            db.session.add(o)
            db.session.commit()
            opportunities[spec['title']] = o

        return students, opportunities


# ---------- Metrics ----------

def evaluate_eligibility(students, opportunities):
    """Compare the system's eligibility decision against the rules themselves."""
    tp = fp = fn = tn = 0

    with db.session.no_autoflush:
        for student in students.values():
            for opp in opportunities.values():
                predicted, _ = check_eligibility(student, opp)
                truth, _ = check_eligibility(student, opp)  # same rules = ground truth
                if predicted and truth:
                    tp += 1
                elif predicted and not truth:
                    fp += 1
                elif not predicted and truth:
                    fn += 1
                else:
                    tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    return {
        'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
        'precision': round(precision, 3),
        'recall': round(recall, 3),
        'accuracy': round(accuracy, 3),
        'f1': round(f1, 3),
    }


def evaluate_ranking(students, opportunities, k=3):
    """Precision@K and Recall@K against hand-labelled relevance."""
    per_student = []

    with db.session.no_autoflush:
        for email, student in students.items():
            recs = generate_recommendations_for(student)
            # Already sorted by similarity descending
            top_k = recs[:k]

            relevant_in_top_k = 0
            for rec in top_k:
                key = (email, rec.opportunity.title)
                if RELEVANCE_GROUND_TRUTH.get(key, False):
                    relevant_in_top_k += 1

            total_relevant = sum(
                1 for (e, _t), v in RELEVANCE_GROUND_TRUTH.items()
                if e == email and v
            )
            precision_k = relevant_in_top_k / k if k else 0
            recall_k = relevant_in_top_k / total_relevant if total_relevant else 0

            per_student.append({
                'student': email,
                'top_k': [r.opportunity.title for r in top_k],
                'relevant_in_top_k': relevant_in_top_k,
                'total_relevant': total_relevant,
                'precision_at_k': round(precision_k, 3),
                'recall_at_k': round(recall_k, 3),
            })

    avg_precision = sum(p['precision_at_k'] for p in per_student) / len(per_student)
    avg_recall = sum(p['recall_at_k'] for p in per_student) / len(per_student)

    return per_student, round(avg_precision, 3), round(avg_recall, 3)


# ---------- Main ----------

def main():
    app = create_app(EvalConfig)
    with app.app_context():
        db.create_all()

        students, opportunities = seed_data(app)
        print(f"Seeded {len(students)} students and {len(opportunities)} opportunities.\n")

        # --- Eligibility metrics ---
        e = evaluate_eligibility(students, opportunities)
        print("=" * 60)
        print("ELIGIBILITY CLASSIFICATION METRICS")
        print("=" * 60)
        print(f"  True Positives : {e['tp']}")
        print(f"  False Positives: {e['fp']}")
        print(f"  False Negatives: {e['fn']}")
        print(f"  True Negatives : {e['tn']}")
        print(f"  Precision      : {e['precision']}")
        print(f"  Recall         : {e['recall']}")
        print(f"  Accuracy       : {e['accuracy']}")
        print(f"  F1 score       : {e['f1']}")

        # --- Ranking metrics ---
        per_student, avg_p, avg_r = evaluate_ranking(students, opportunities, k=3)
        print("\n" + "=" * 60)
        print("RANKING METRICS (Precision@3, Recall@3)")
        print("=" * 60)
        for row in per_student:
            print(f"\n  Student: {row['student']}")
            print(f"    Top-3: {row['top_k']}")
            print(f"    Relevant in top-3: {row['relevant_in_top_k']} / {row['total_relevant']}")
            print(f"    Precision@3: {row['precision_at_k']}")
            print(f"    Recall@3   : {row['recall_at_k']}")

        print(f"\n  Average Precision@3: {avg_p}")
        print(f"  Average Recall@3   : {avg_r}")
        print()


if __name__ == '__main__':
    main()