"""
Analysis Result Model
=====================
Stores computed analysis outputs: break-even point, margins, ROI, risk.
"""

from datetime import datetime, timezone
from app.models.database import db


class AnalysisResult(db.Model):
    """Computed financial analysis results."""

    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    # Break-even metrics
    break_even_units = db.Column(db.Float, nullable=False)
    break_even_revenue = db.Column(db.Float, nullable=False)

    # Profitability
    contribution_margin = db.Column(db.Float, nullable=False)
    contribution_margin_ratio = db.Column(db.Float, nullable=False)
    profit_margin = db.Column(db.Float, nullable=True)
    expected_profit = db.Column(db.Float, nullable=True)
    expected_revenue = db.Column(db.Float, nullable=True)

    # ROI
    roi_percentage = db.Column(db.Float, nullable=True)

    # Risk assessment (AI-generated)
    risk_level = db.Column(db.String(20), nullable=True)  # low, medium, high, critical
    risk_score = db.Column(db.Float, nullable=True)  # 0-100
    feasibility_score = db.Column(db.Float, nullable=True)  # 0-100

    # Safety margin
    safety_margin = db.Column(db.Float, nullable=True)
    safety_margin_percentage = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<AnalysisResult project_id={self.project_id} BEP={self.break_even_units}>'
