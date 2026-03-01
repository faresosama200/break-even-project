"""
Financial Input Model
=====================
Stores the financial parameters for each project analysis.
"""

from datetime import datetime, timezone
from app.models.database import db


class FinancialInput(db.Model):
    """Financial data inputs for break-even calculation."""

    __tablename__ = 'financial_inputs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    # Core financial inputs
    fixed_costs = db.Column(db.Float, nullable=False)
    variable_cost_per_unit = db.Column(db.Float, nullable=False)
    selling_price_per_unit = db.Column(db.Float, nullable=False)
    expected_production_volume = db.Column(db.Integer, nullable=False)

    # Optional extended inputs
    initial_investment = db.Column(db.Float, default=0.0)
    monthly_overhead = db.Column(db.Float, default=0.0)
    marketing_budget = db.Column(db.Float, default=0.0)
    target_profit = db.Column(db.Float, default=0.0)
    time_horizon_months = db.Column(db.Integer, default=12)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<FinancialInput project_id={self.project_id}>'
