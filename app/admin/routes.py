from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.admin import bp
from app.admin.forms import OpportunityForm
from app.extensions import db
from app.models.opportunity import Opportunity
from app.models.student import Student
from app.models.recommendation import Recommendation


@bp.before_request
@login_required
def admin_only():
    if current_user.role != 'admin':
        abort(403)


@bp.route('/dashboard')
def dashboard():
    stats = {
        'students': Student.query.count(),
        'opportunities': Opportunity.query.count(),
        'recommendations': Recommendation.query.count(),
        'active': Opportunity.query.filter_by(is_active=True).count(),
    }
    return render_template('admin/dashboard.html', stats=stats,
                           title='Admin Dashboard')


@bp.route('/opportunities')
def opportunities():
    items = Opportunity.query.order_by(Opportunity.deadline.asc()).all()
    return render_template('admin/opportunities.html', items=items,
                           title='Manage Opportunities')


@bp.route('/opportunities/new', methods=['GET', 'POST'])
def new_opportunity():
    form = OpportunityForm()
    if form.validate_on_submit():
        opp = Opportunity(
            title=form.title.data.strip(),
            category=form.category.data,
            description=form.description.data.strip(),
            provider=form.provider.data.strip(),
            min_cgpa=form.min_cgpa.data,
            eligible_department=(form.eligible_department.data or '').strip() or None,
            eligible_level=(form.eligible_level.data or '').strip() or None,
            deadline=form.deadline.data,
            admin_id=current_user.admin_id,
        )
        db.session.add(opp)
        db.session.commit()
        flash('Opportunity created.', 'success')
        return redirect(url_for('admin.opportunities'))
    return render_template('admin/opportunity_form.html', form=form,
                           title='New Opportunity')


@bp.route('/opportunities/<int:opp_id>/edit', methods=['GET', 'POST'])
def edit_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    form = OpportunityForm(obj=opp)
    if form.validate_on_submit():
        form.populate_obj(opp)
        db.session.commit()
        flash('Opportunity updated.', 'success')
        return redirect(url_for('admin.opportunities'))
    return render_template('admin/opportunity_form.html', form=form,
                           title='Edit Opportunity')


@bp.route('/opportunities/<int:opp_id>/delete', methods=['POST'])
def delete_opportunity(opp_id):
    opp = Opportunity.query.get_or_404(opp_id)
    db.session.delete(opp)
    db.session.commit()
    flash('Opportunity deleted.', 'info')
    return redirect(url_for('admin.opportunities'))


@bp.route('/scan-deadlines')
def trigger_scan():
    """Manual trigger for the deadline alert job (for demo/testing)."""
    from app.services.notifier import scan_deadlines
    scan_deadlines()
    flash('Deadline scan complete.', 'info')
    return redirect(url_for('admin.dashboard'))


@bp.route('/stats/categories')
def stats_categories():
    """JSON endpoint for the dashboard chart (used in Phase 8)."""
    from flask import jsonify
    from sqlalchemy import func
    rows = (db.session.query(Opportunity.category,
                             func.count(Opportunity.opportunity_id))
            .group_by(Opportunity.category).all())
    return jsonify({
        'labels': [r[0] for r in rows],
        'values': [r[1] for r in rows],
    })