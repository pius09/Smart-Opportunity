from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, mail, csrf, scheduler
from app import create_app

app = create_app()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Import models so Flask-Migrate detects them
    from app import models  # noqa: F401

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # --- Background scheduler for deadline alerts ---
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()
        scheduler.add_job(
            id='scan_deadlines',
            func=lambda: _run_with_context(app, _scan_deadlines_job),
            trigger='interval',
            hours=6,
            replace_existing=True,
        )

    return app


def _run_with_context(app, fn):
    with app.app_context():
        fn()


def _scan_deadlines_job():
    from app.services.notifier import scan_deadlines
    scan_deadlines()