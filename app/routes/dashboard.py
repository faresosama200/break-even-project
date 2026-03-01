"""
Dashboard Routes
================
Main dashboard with overview metrics and recent projects.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.analysis_result import AnalysisResult
from app.models.database import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard page."""
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.updated_at.desc()).all()

    total_projects = len(projects)
    analyzed_projects = sum(1 for p in projects if p.status == 'analyzed')

    # Aggregate analytics
    risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    avg_feasibility = 0
    profitable_count = 0

    for project in projects:
        result = project.analysis_results.order_by(AnalysisResult.created_at.desc()).first()
        if result:
            level = result.risk_level or 'medium'
            if level in risk_distribution:
                risk_distribution[level] += 1
            if result.feasibility_score:
                avg_feasibility += result.feasibility_score
            if result.expected_profit and result.expected_profit > 0:
                profitable_count += 1

    if analyzed_projects > 0:
        avg_feasibility = round(avg_feasibility / analyzed_projects, 1)

    recent_projects = projects[:5]

    return render_template('dashboard/index.html',
                           projects=projects,
                           recent_projects=recent_projects,
                           total_projects=total_projects,
                           analyzed_projects=analyzed_projects,
                           risk_distribution=risk_distribution,
                           avg_feasibility=avg_feasibility,
                           profitable_count=profitable_count)
