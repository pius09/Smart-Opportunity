from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    __tablename__ = 'notification'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'),
                           nullable=False, index=True)
    recommendation_id = db.Column(db.Integer,
                                  db.ForeignKey('recommendation.recommendation_id'),
                                  nullable=True)
    message = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Notif s={self.student_id} read={self.is_read}>'