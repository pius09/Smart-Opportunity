# Smart Scholarship & Student Opportunity Recommendation System

A hybrid content-based and rule-based recommender that matches Nigerian
university students to scholarships, internships, grants, competitions,
conferences, and training opportunities they are eligible for.

## Final Year Project — Federal University Dutse

**Author:** [Your Name]  
**Supervisor:** [Supervisor Name]  
**Year:** 2026

---

## 🧰 Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+ / Flask 3.x |
| Database | MySQL 8.0 (via XAMPP / MariaDB) |
| ORM | SQLAlchemy + Flask-Migrate |
| Recommender | Scikit-learn (TF-IDF + cosine similarity) |
| Frontend | HTML5, CSS3, Bootstrap 5, Jinja2 |
| Authentication | Flask-Login + Werkzeug password hashing |
| Forms | Flask-WTF + CSRF protection |
| Scheduling | Flask-APScheduler |
| Testing | pytest (17 unit + integration tests) |

---

## 🏗️ Architecture

Three-tier client-server:

1. **Presentation** — Browser (Bootstrap 5 + Jinja2)
2. **Application** — Flask (routes, recommendation engine, eligibility matcher, notifier)
3. **Data** — MySQL (5 tables: student, administrator, opportunity, recommendation, notification)

The recommender uses a **switching hybrid** strategy: content-based similarity first (TF-IDF + cosine), followed by rule-based eligibility filtering.

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- XAMPP (or standalone MySQL 8.0)
- VS Code (recommended)

### 2. Clone / extract project
```bash
cd C:\Users\YourName\Documents
mkdir smart-opportunity && cd smart-opportunity
# copy project files here