"""
Prediction Model
================
Stores ML-generated forecasts and predictions for projects.
"""

from datetime import datetime, timezone
from app.models.database import db


class Prediction(db.Model):
    """AI/ML predictions for project performance."""

    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    # Prediction data
    prediction_type = db.Column(db.String(50), nullable=False)  # profitability, revenue, risk
    predicted_value = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)  # 0-1
    time_period_months = db.Column(db.Integer, default=12)

    # Model metadata
    model_name = db.Column(db.String(100), nullable=True)
    model_version = db.Column(db.String(20), nullable=True)
    features_used = db.Column(db.Text, nullable=True)  # JSON string of features

    # Forecast series (JSON: list of {month, value})
    forecast_series = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Prediction {self.prediction_type} project_id={self.project_id}>'
