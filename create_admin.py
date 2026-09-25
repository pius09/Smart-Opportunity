"""Run once: python create_admin.py"""
from app import create_app
from app.extensions import db
from app.models.administrator import Administrator

app = create_app()
with app.app_context():
    email = input("Admin email: ").strip().lower()
    if Administrator.query.filter_by(email=email).first():
        print("Admin already exists.")
    else:
        name = input("Admin full name: ").strip()
        pw = input("Admin password: ").strip()
        a = Administrator(full_name=name, email=email)
        a.set_password(pw)
        db.session.add(a)
        db.session.commit()
        print(f"Admin {email} created.")