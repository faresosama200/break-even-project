"""
Reports Routes
==============
Generate and display detailed analysis reports, historical comparison.
"""

import json
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.financial_input import FinancialInput
from app.models.analysis_result import AnalysisResult
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/<int:project_id>')
@login_required
def project_report(project_id):
    """Full analysis report for a project."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    fin_input = project.financial_inputs.order_by(FinancialInput.created_at.desc()).first()
    analysis = project.analysis_results.order_by(AnalysisResult.created_at.desc()).first()
    predictions = project.predictions.order_by(Prediction.created_at.desc()).all()
    recommendations = project.recommendations.order_by(Recommendation.priority.asc()).all()

    # Historical inputs for this project
    history = project.financial_inputs.order_by(FinancialInput.created_at.asc()).all()
    historical_data = []
    for h in history:
        ar = AnalysisResult.query.filter_by(project_id=project.id)\
            .order_by(AnalysisResult.created_at.asc()).all()
        historical_data.append({
            'date': h.created_at.strftime('%Y-%m-%d %H:%M'),
            'fixed_costs': h.fixed_costs,
            'variable_cost': h.variable_cost_per_unit,
            'selling_price': h.selling_price_per_unit,
            'volume': h.expected_production_volume,
        })

    return render_template('reports/report.html',
                           project=project,
                           fin_input=fin_input,
                           analysis=analysis,
                           predictions=predictions,
                           recommendations=recommendations,
                           historical_data=json.dumps(historical_data))


@reports_bp.route('/compare')
@login_required
def compare():
    """Compare all user projects side-by-side."""
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.created_at.desc()).all()

    comparison = []
    for project in projects:
        fin = project.financial_inputs.order_by(FinancialInput.created_at.desc()).first()
        result = project.analysis_results.order_by(AnalysisResult.created_at.desc()).first()
        if fin and result:
            comparison.append({
                'id': project.id,
                'name': project.name,
                'industry': project.industry or 'N/A',
                'fixed_costs': fin.fixed_costs,
                'variable_cost': fin.variable_cost_per_unit,
                'selling_price': fin.selling_price_per_unit,
                'volume': fin.expected_production_volume,
                'bep_units': result.break_even_units,
                'profit': result.expected_profit,
                'profit_margin': result.profit_margin,
                'roi': result.roi_percentage,
                'risk_level': result.risk_level,
                'feasibility': result.feasibility_score,
            })

    return render_template('reports/compare.html',
                           comparison=comparison,
                           comparison_json=json.dumps(comparison))


@reports_bp.route('/<int:project_id>/api/data')
@login_required
def report_data_api(project_id):
    """API: get report data as JSON for download."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    fin = project.financial_inputs.order_by(FinancialInput.created_at.desc()).first()
    analysis = project.analysis_results.order_by(AnalysisResult.created_at.desc()).first()
    predictions = project.predictions.all()
    recs = project.recommendations.all()

    data = {
        'project': {'name': project.name, 'industry': project.industry,
                     'currency': project.currency, 'status': project.status},
        'financial_inputs': {
            'fixed_costs': fin.fixed_costs if fin else None,
            'variable_cost_per_unit': fin.variable_cost_per_unit if fin else None,
            'selling_price_per_unit': fin.selling_price_per_unit if fin else None,
            'expected_production_volume': fin.expected_production_volume if fin else None,
            'initial_investment': fin.initial_investment if fin else None,
        },
        'analysis': {
            'break_even_units': analysis.break_even_units if analysis else None,
            'break_even_revenue': analysis.break_even_revenue if analysis else None,
            'contribution_margin': analysis.contribution_margin if analysis else None,
            'profit_margin': analysis.profit_margin if analysis else None,
            'expected_profit': analysis.expected_profit if analysis else None,
            'roi_percentage': analysis.roi_percentage if analysis else None,
            'risk_level': analysis.risk_level if analysis else None,
            'risk_score': analysis.risk_score if analysis else None,
            'feasibility_score': analysis.feasibility_score if analysis else None,
        },
        'predictions': [
            {'type': p.prediction_type, 'value': p.predicted_value,
             'confidence': p.confidence_score}
            for p in predictions
        ],
        'recommendations': [
            {'category': r.category, 'title': r.title,
             'description': r.description, 'priority': r.priority}
            for r in recs
        ],
    }
    return jsonify(data)
