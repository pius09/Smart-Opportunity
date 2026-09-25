from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app.auth.forms import RegisterForm, LoginForm
from app.extensions import db
from app.models.student import Student
from app.models.administrator import Administrator


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if Student.query.filter_by(email=form.email.data.lower()).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        student = Student(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            department='',
            level='',
            cgpa=0,
        )
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()

        flash('Account created. Please complete your profile.', 'success')
        login_user(student)
        return redirect(url_for('student.profile'))

    return render_template('auth/register.html', form=form, title='Register')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = Student.query.filter_by(email=email).first()
        if not user:
            user = Administrator.query.filter_by(email=email).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)

        # Refresh recommendations for students with a complete profile
        if user.role == 'student':
            try:
                if (user.department and user.level
                        and user.cgpa and float(user.cgpa) > 0):
                    from app.services.recommender import generate_recommendations_for
                    generate_recommendations_for(user)
            except Exception:
                # Never block login if recommendation generation fails
                pass

        next_url = request.args.get('next')
        if user.role == 'admin':
            return redirect(next_url or url_for('admin.dashboard'))
        return redirect(next_url or url_for('student.dashboard'))

    return render_template('auth/login.html', form=form, title='Login')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))