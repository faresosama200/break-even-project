"""
Project Model
=============
Represents a business project submitted for feasibility analysis.
"""

from datetime import datetime, timezone
from app.models.database import db


class Project(db.Model):
    """Business project entity for break-even analysis."""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(20), default='draft')  # draft, analyzed, archived
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    financial_inputs = db.relationship('FinancialInput', backref='project',
                                       lazy='dynamic', cascade='all, delete-orphan')
    analysis_results = db.relationship('AnalysisResult', backref='project',
                                       lazy='dynamic', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='project',
                                  lazy='dynamic', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='project',
                                      lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'
