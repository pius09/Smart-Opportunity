"""Content-based recommendation engine.

Implements the hybrid architecture described in Chapter 2 of the project:
a TF-IDF + cosine similarity stage (content-based filtering) followed by a
rule-based eligibility filter.
"""
from datetime import date, datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.extensions import db
from app.models.opportunity import Opportunity
from app.models.recommendation import Recommendation
from app.services.eligibility import check_eligibility


def _active_opportunities():
    """Only currently open opportunities are recommended."""
    return (Opportunity.query
            .filter_by(is_active=True)
            .filter(Opportunity.deadline >= date.today())
            .all())


def generate_recommendations_for(student, top_n=50):
    """Regenerate recommendations for a single student.

    Returns a list of Recommendation objects ordered by similarity score.
    """
    profile_text = student.profile_text()
    if not profile_text.strip():
        return []

    opportunities = _active_opportunities()
    if not opportunities:
        return []

    # Build the corpus: [student_text, opp1_text, opp2_text, ...]
    corpus = [profile_text] + [o.attribute_text() for o in opportunities]

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Happens if every document is empty after stop-word removal
        return []

    # Cosine similarity between the student vector and every opportunity vector
    sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    # Wipe this student's previous recommendations so we can regenerate fresh
    Recommendation.query.filter_by(student_id=student.student_id).delete()

    results = []
    for opp, score in zip(opportunities, sims):
        eligible, reason = check_eligibility(student, opp)
        rec = Recommendation(
            student_id=student.student_id,
            opportunity_id=opp.opportunity_id,
            similarity_score=round(float(score), 3),
            eligibility_status=eligible,
            eligibility_reason=reason or None,
            date_generated=datetime.utcnow(),
        )
        db.session.add(rec)
        results.append((rec, opp, float(score)))

    db.session.commit()

    # Notify on new eligible matches (top 3)
    from app.services.notifier import create_match_notifications
    create_match_notifications(student, results)

    # Sort by similarity descending, return top N
    results.sort(key=lambda x: x[2], reverse=True)
    return [r[0] for r in results[:top_n]]