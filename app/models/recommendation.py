"""
Recommendation Model
====================
Stores AI-generated recommendations for each project.
"""

from datetime import datetime, timezone
from app.models.database import db


class Recommendation(db.Model):
    """AI-generated business recommendations."""

    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    category = db.Column(db.String(50), nullable=False)
    # cost_reduction, pricing, production, risk_alert, general
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    impact_score = db.Column(db.Float, nullable=True)  # 0-100

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Recommendation {self.category}: {self.title[:30]}>'
