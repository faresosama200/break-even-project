"""
Project Routes
==============
CRUD operations for projects and financial inputs, triggers analysis pipeline.
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.database import db
from app.models.project import Project
from app.models.financial_input import FinancialInput
from app.models.analysis_result import AnalysisResult
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.services.financial_engine import FinancialEngine
from app.services.ai_engine import AIAnalysisEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.prediction_engine import PredictionEngine
from app.utils.validators import validate_project, validate_financial_input, sanitize_string

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


@projects_bp.route('/')
@login_required
def index():
    """List all projects for the current user."""
    projects = Project.query.filter_by(user_id=current_user.id)\
        .order_by(Project.updated_at.desc()).all()
    return render_template('projects/index.html', projects=projects)


@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new project with financial inputs."""
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name', ''))
        description = sanitize_string(request.form.get('description', ''))
        industry = sanitize_string(request.form.get('industry', ''))
        currency = sanitize_string(request.form.get('currency', 'USD'))

        errors = validate_project(name, description)

        # Financial inputs
        fin_data = {
            'fixed_costs': request.form.get('fixed_costs', ''),
            'variable_cost_per_unit': request.form.get('variable_cost_per_unit', ''),
            'selling_price_per_unit': request.form.get('selling_price_per_unit', ''),
            'expected_production_volume': request.form.get('expected_production_volume', ''),
            'initial_investment': request.form.get('initial_investment', '0'),
            'monthly_overhead': request.form.get('monthly_overhead', '0'),
            'marketing_budget': request.form.get('marketing_budget', '0'),
            'target_profit': request.form.get('target_profit', '0'),
            'time_horizon_months': request.form.get('time_horizon_months', '12'),
        }
        errors.extend(validate_financial_input(fin_data))

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('projects/create.html', form=request.form)

        # Create project
        project = Project(
            user_id=current_user.id,
            name=name,
            description=description or None,
            industry=industry or None,
            currency=currency,
            status='analyzed',
        )
        db.session.add(project)
        db.session.flush()

        # Create financial input
        fin_input = FinancialInput(
            project_id=project.id,
            fixed_costs=float(fin_data['fixed_costs']),
            variable_cost_per_unit=float(fin_data['variable_cost_per_unit']),
            selling_price_per_unit=float(fin_data['selling_price_per_unit']),
            expected_production_volume=int(float(fin_data['expected_production_volume'])),
            initial_investment=float(fin_data['initial_investment'] or 0),
            monthly_overhead=float(fin_data['monthly_overhead'] or 0),
            marketing_budget=float(fin_data['marketing_budget'] or 0),
            target_profit=float(fin_data['target_profit'] or 0),
            time_horizon_months=int(fin_data['time_horizon_months'] or 12),
        )
        db.session.add(fin_input)
        db.session.flush()

        # Run analysis pipeline
        _run_analysis_pipeline(project, fin_input)
        db.session.commit()

        flash('Project created and analyzed successfully!', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))

    return render_template('projects/create.html', form={})


@projects_bp.route('/<int:project_id>')
@login_required
def detail(project_id):
    """View project details with analysis results."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    fin_input = project.financial_inputs.order_by(FinancialInput.created_at.desc()).first()
    analysis = project.analysis_results.order_by(AnalysisResult.created_at.desc()).first()
    predictions = project.predictions.order_by(Prediction.created_at.desc()).all()
    recommendations = project.recommendations.order_by(Recommendation.priority.asc()).all()

    # Generate chart data
    chart_data = {}
    if fin_input:
        chart_data = FinancialEngine.generate_cost_revenue_data(
            fin_input.fixed_costs,
            fin_input.variable_cost_per_unit,
            fin_input.selling_price_per_unit,
        )

    # Get forecast series
    forecast = None
    for p in predictions:
        if p.prediction_type == 'monthly_forecast' and p.forecast_series:
            try:
                forecast = json.loads(p.forecast_series)
            except json.JSONDecodeError:
                pass
            break

    return render_template('projects/detail.html',
                           project=project,
                           fin_input=fin_input,
                           analysis=analysis,
                           predictions=predictions,
                           recommendations=recommendations,
                           chart_data=json.dumps(chart_data),
                           forecast=json.dumps(forecast) if forecast else 'null')


@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """Edit project financial inputs and re-run analysis."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    fin_input = project.financial_inputs.order_by(FinancialInput.created_at.desc()).first()

    if request.method == 'POST':
        name = sanitize_string(request.form.get('name', ''))
        description = sanitize_string(request.form.get('description', ''))
        industry = sanitize_string(request.form.get('industry', ''))
        currency = sanitize_string(request.form.get('currency', 'USD'))

        errors = validate_project(name, description)

        fin_data = {
            'fixed_costs': request.form.get('fixed_costs', ''),
            'variable_cost_per_unit': request.form.get('variable_cost_per_unit', ''),
            'selling_price_per_unit': request.form.get('selling_price_per_unit', ''),
            'expected_production_volume': request.form.get('expected_production_volume', ''),
            'initial_investment': request.form.get('initial_investment', '0'),
            'monthly_overhead': request.form.get('monthly_overhead', '0'),
            'marketing_budget': request.form.get('marketing_budget', '0'),
            'target_profit': request.form.get('target_profit', '0'),
            'time_horizon_months': request.form.get('time_horizon_months', '12'),
        }
        errors.extend(validate_financial_input(fin_data))

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('projects/edit.html', project=project,
                                   fin_input=fin_input, form=request.form)

        project.name = name
        project.description = description or None
        project.industry = industry or None
        project.currency = currency
        project.status = 'analyzed'

        # Create new financial input (keeps history)
        new_fin = FinancialInput(
            project_id=project.id,
            fixed_costs=float(fin_data['fixed_costs']),
            variable_cost_per_unit=float(fin_data['variable_cost_per_unit']),
            selling_price_per_unit=float(fin_data['selling_price_per_unit']),
            expected_production_volume=int(float(fin_data['expected_production_volume'])),
            initial_investment=float(fin_data['initial_investment'] or 0),
            monthly_overhead=float(fin_data['monthly_overhead'] or 0),
            marketing_budget=float(fin_data['marketing_budget'] or 0),
            target_profit=float(fin_data['target_profit'] or 0),
            time_horizon_months=int(fin_data['time_horizon_months'] or 12),
        )
        db.session.add(new_fin)
        db.session.flush()

        _run_analysis_pipeline(project, new_fin)
        db.session.commit()

        flash('Project updated and re-analyzed.', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))

    return render_template('projects/edit.html', project=project,
                           fin_input=fin_input, form={})


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete(project_id):
    """Delete a project and all related data."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('projects.index'))


@projects_bp.route('/<int:project_id>/api/chart-data')
@login_required
def chart_data_api(project_id):
    """API endpoint for chart data (AJAX)."""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    fin_input = project.financial_inputs.order_by(FinancialInput.created_at.desc()).first()
    if not fin_input:
        return jsonify({'error': 'No financial data'}), 404
    data = FinancialEngine.generate_cost_revenue_data(
        fin_input.fixed_costs,
        fin_input.variable_cost_per_unit,
        fin_input.selling_price_per_unit,
    )
    return jsonify(data)


def _run_analysis_pipeline(project, fin_input):
    """Execute the full analysis pipeline: financial → AI → predictions → recommendations."""
    fin_data = {
        'fixed_costs': fin_input.fixed_costs,
        'variable_cost_per_unit': fin_input.variable_cost_per_unit,
        'selling_price_per_unit': fin_input.selling_price_per_unit,
        'expected_production_volume': fin_input.expected_production_volume,
        'initial_investment': fin_input.initial_investment,
    }

    # 1. Financial calculations
    analysis = FinancialEngine.full_analysis(
        fin_data['fixed_costs'],
        fin_data['variable_cost_per_unit'],
        fin_data['selling_price_per_unit'],
        fin_data['expected_production_volume'],
        fin_data['initial_investment'],
    )

    # 2. AI risk & feasibility
    from flask import current_app
    model_dir = current_app.config.get('MODEL_DIR', 'data/models')
    ai = AIAnalysisEngine(model_dir=model_dir)
    risk_info = ai.classify_risk(fin_data, analysis)
    feasibility_info = ai.evaluate_feasibility(fin_data, analysis)

    # 3. Save analysis results
    result = AnalysisResult(
        project_id=project.id,
        break_even_units=analysis['break_even_units'] or 0,
        break_even_revenue=analysis['break_even_revenue'] or 0,
        contribution_margin=analysis['contribution_margin'],
        contribution_margin_ratio=analysis['contribution_margin_ratio'] or 0,
        profit_margin=analysis['profit_margin'],
        expected_profit=analysis['expected_profit'],
        expected_revenue=analysis['expected_revenue'],
        roi_percentage=analysis['roi_percentage'],
        risk_level=risk_info['risk_level'],
        risk_score=risk_info['risk_score'],
        feasibility_score=feasibility_info['feasibility_score'],
        safety_margin=analysis['safety_margin'],
        safety_margin_percentage=analysis['safety_margin_percentage'],
    )
    db.session.add(result)

    # 4. Predictions
    forecast_data = PredictionEngine.forecast_monthly(
        fin_data, analysis, fin_input.time_horizon_months or 12
    )
    pred_forecast = Prediction(
        project_id=project.id,
        prediction_type='monthly_forecast',
        predicted_value=forecast_data['total_profit'],
        confidence_score=0.7,
        time_period_months=fin_input.time_horizon_months or 12,
        model_name='ramp_up_simulation',
        forecast_series=json.dumps(forecast_data['series']),
    )
    db.session.add(pred_forecast)

    # Profitability prediction
    prof_pred = PredictionEngine.predict_profitability(fin_data)
    pred_prof = Prediction(
        project_id=project.id,
        prediction_type='profitability',
        predicted_value=prof_pred['predicted_margin'],
        confidence_score=prof_pred['confidence'],
        model_name=prof_pred['method'],
    )
    db.session.add(pred_prof)

    # 5. Recommendations
    recs = RecommendationEngine.generate(fin_data, analysis, risk_info, feasibility_info)
    for rec in recs:
        r = Recommendation(
            project_id=project.id,
            category=rec['category'],
            title=rec['title'],
            description=rec['description'],
            priority=rec['priority'],
            impact_score=rec.get('impact_score'),
        )
        db.session.add(r)
