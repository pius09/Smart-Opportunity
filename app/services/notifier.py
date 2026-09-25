"""Notification generator for new matches and approaching deadlines."""
from datetime import date, timedelta
from flask import current_app
from app.extensions import db
from app.models.notification import Notification


def create_match_notifications(student, results, top_k=3):
    """Notify a student about their top new eligible matches.

    Avoids creating duplicate notifications for the same recommendation.
    """
    already_notified = {
        n.recommendation_id
        for n in Notification.query.filter_by(student_id=student.student_id).all()
    }

    eligible_sorted = sorted(
        [r for r in results if r[0].eligibility_status],
        key=lambda x: x[2], reverse=True
    )[:top_k]

    for rec, opp, _score in eligible_sorted:
        if rec.recommendation_id in already_notified:
            continue
        msg = f"New match: {opp.title} — deadline {opp.deadline}."
        db.session.add(Notification(
            student_id=student.student_id,
            recommendation_id=rec.recommendation_id,
            message=msg[:255],
        ))
    db.session.commit()


def scan_deadlines():
    """Periodic job: alert students about soon-to-close matched opportunities."""
    days = current_app.config.get('DEADLINE_ALERT_DAYS', 7)
    cutoff = date.today() + timedelta(days=days)

    from app.models.recommendation import Recommendation

    # Find eligible recommendations whose opportunity closes on the cutoff date
    upcoming = (Recommendation.query
                .filter_by(eligibility_status=True)
                .join(Recommendation.opportunity)
                .filter(Recommendation.opportunity.has(deadline=cutoff))
                .all())

    for rec in upcoming:
        # Skip if we've already sent a "closing" alert for this recommendation
        existing = (Notification.query
                    .filter_by(student_id=rec.student_id,
                               recommendation_id=rec.recommendation_id)
                    .filter(Notification.message.like('%closing%'))
                    .first())
        if existing:
            continue

        msg = f"{rec.opportunity.title} is closing on {rec.opportunity.deadline}."
        db.session.add(Notification(
            student_id=rec.student_id,
            recommendation_id=rec.recommendation_id,
            message=msg[:255],
        ))
    db.session.commit()