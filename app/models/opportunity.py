from datetime import datetime, date
from app.extensions import db


class Opportunity(db.Model):
    __tablename__ = 'opportunity'

    opportunity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(150), nullable=False)
    min_cgpa = db.Column(db.Numeric(3, 2), nullable=True)
    eligible_department = db.Column(db.String(100), nullable=True)
    eligible_level = db.Column(db.String(20), nullable=True)
    deadline = db.Column(db.Date, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('administrator.admin_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    recommendations = db.relationship(
        'Recommendation', backref='opportunity', lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def attribute_text(self):
        parts = [
            self.title or '',
            self.category or '',
            self.description or '',
            self.provider or '',
            self.eligible_department or '',
            self.eligible_level or '',
        ]
        return ' '.join(parts).strip().lower()

    def days_remaining(self):
        return (self.deadline - date.today()).days

    def __repr__(self):
        return f'<Opportunity {self.title}>'