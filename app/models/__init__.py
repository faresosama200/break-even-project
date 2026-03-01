"""
Database Models Package
=======================
SQLAlchemy ORM models for the break-even analysis system.
"""

from app.models.database import db
from app.models.user import User
from app.models.project import Project
from app.models.financial_input import FinancialInput
from app.models.analysis_result import AnalysisResult
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation

__all__ = [
    'db', 'User', 'Project', 'FinancialInput',
    'AnalysisResult', 'Prediction', 'Recommendation'
]
