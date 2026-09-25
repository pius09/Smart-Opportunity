from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.student import bp
from app.student.forms import ProfileForm
from app.extensions import db


@bp.before_request
@login_required
def require_login():
    if current_user.role != 'student':
        flash('Access restricted to students.', 'warning')
        return redirect(url_for('auth.login'))


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.department = form.department.data.strip()
        current_user.level = form.level.data
        current_user.cgpa = form.cgpa.data
        current_user.skills = (form.skills.data or '').strip()
        current_user.interests = (form.interests.data or '').strip()
        current_user.location = (form.location.data or '').strip()
        db.session.commit()

        # Generate fresh recommendations based on the updated profile
        from app.services.recommender import generate_recommendations_for
        generate_recommendations_for(current_user)

        flash('Profile saved and recommendations updated.', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/profile.html', form=form, title='My Profile')


@bp.route('/dashboard')
def dashboard():
    from app.models.recommendation import Recommendation

    recs = (Recommendation.query
            .filter_by(student_id=current_user.student_id)
            .order_by(Recommendation.similarity_score.desc())
            .all())

    profile_complete = bool(
        current_user.department
        and current_user.level
        and current_user.cgpa
        and float(current_user.cgpa) > 0
    )

    return render_template('student/dashboard.html',
                           recommendations=recs,
                           profile_complete=profile_complete,
                           title='Dashboard')


@bp.route('/notifications')
def notifications():
    from app.models.notification import Notification

    notifs = (Notification.query
              .filter_by(student_id=current_user.student_id)
              .order_by(Notification.sent_at.desc())
              .all())

    # Mark all as read
    for n in notifs:
        if not n.is_read:
            n.is_read = True
    db.session.commit()

    return render_template('student/notifications.html',
                           notifications=notifs,
                           title='Alerts')