from datetime import datetime
from app.extensions import db


class Recommendation(db.Model):
    __tablename__ = 'recommendation'

    recommendation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'),
                           nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.opportunity_id'),
                               nullable=False, index=True)
    similarity_score = db.Column(db.Numeric(4, 3), nullable=False, default=0)
    eligibility_status = db.Column(db.Boolean, nullable=False, default=False)
    eligibility_reason = db.Column(db.String(255), nullable=True)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    notification = db.relationship(
        'Notification', backref='recommendation', uselist=False,
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('student_id', 'opportunity_id',
                            name='uq_student_opportunity'),
    )

    def __repr__(self):
        return f'<Rec s={self.student_id} o={self.opportunity_id} score={self.similarity_score}>'