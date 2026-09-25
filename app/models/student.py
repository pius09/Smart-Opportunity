from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class Student(UserMixin, db.Model):
    __tablename__ = 'student'

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100), nullable=False, default='')
    level = db.Column(db.String(20), nullable=False, default='')
    cgpa = db.Column(db.Numeric(3, 2), nullable=False, default=0)
    skills = db.Column(db.Text, nullable=True)
    interests = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recommendations = db.relationship(
        'Recommendation', backref='student', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    notifications = db.relationship(
        'Notification', backref='student', lazy='dynamic',
        cascade='all, delete-orphan'
    )

    role = 'student'

    def get_id(self):
        return f"student-{self.student_id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def profile_text(self):
        parts = [
            self.department or '',
            self.level or '',
            self.skills or '',
            self.interests or '',
            self.location or '',
        ]
        return ' '.join(parts).strip().lower()

    def unread_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f'<Student {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('student-'):
        return Student.query.get(int(user_id.split('-')[1]))
    if user_id.startswith('admin-'):
        from app.models.administrator import Administrator
        return Administrator.query.get(int(user_id.split('-')[1]))
    return None