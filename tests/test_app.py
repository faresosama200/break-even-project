#!/usr/bin/env python3
"""
Test Suite
==========
Comprehensive tests for models, services, routes, and AI engine.
Run with: python -m pytest tests/ -v
"""

import json
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models.database import db
from app.models.user import User
from app.models.project import Project
from app.models.financial_input import FinancialInput
from app.services.financial_engine import FinancialEngine
from app.services.ai_engine import AIAnalysisEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.prediction_engine import PredictionEngine


class BaseTestCase(unittest.TestCase):
    """Base test case with app context and test database."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self, username='testuser', password='password123'):
        user = User(username=username, email=f'{username}@test.com')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def login(self, username='testuser', password='password123'):
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password,
        }, follow_redirects=True)


class TestUserModel(BaseTestCase):
    """Tests for User model."""

    def test_password_hashing(self):
        user = User(username='test', email='test@test.com')
        user.set_password('secret')
        self.assertFalse(user.check_password('wrong'))
        self.assertTrue(user.check_password('secret'))
        self.assertNotEqual(user.password_hash, 'secret')

    def test_user_creation(self):
        user = self.create_user()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)


class TestFinancialEngine(BaseTestCase):
    """Tests for FinancialEngine calculations."""

    def test_break_even_units(self):
        bep = FinancialEngine.calculate_break_even_units(10000, 50, 20)
        self.assertAlmostEqual(bep, 333.33, places=2)

    def test_break_even_impossible(self):
        bep = FinancialEngine.calculate_break_even_units(10000, 20, 25)
        self.assertIsNone(bep)

    def test_contribution_margin(self):
        cm = FinancialEngine.calculate_contribution_margin(50, 20)
        self.assertEqual(cm, 30)

    def test_expected_profit(self):
        profit = FinancialEngine.calculate_expected_profit(10000, 20, 50, 1000)
        self.assertEqual(profit, 20000)  # 50000 - 30000

    def test_roi(self):
        roi = FinancialEngine.calculate_roi(20000, 50000)
        self.assertAlmostEqual(roi, 40.0)

    def test_full_analysis(self):
        result = FinancialEngine.full_analysis(
            fixed_costs=15000,
            variable_cost=3.50,
            selling_price=12.00,
            volume=5000,
            initial_investment=25000,
        )
        self.assertIsNotNone(result['break_even_units'])
        self.assertGreater(result['expected_profit'], 0)
        self.assertGreater(result['contribution_margin'], 0)
        self.assertIsNotNone(result['roi_percentage'])

    def test_chart_data_generation(self):
        data = FinancialEngine.generate_cost_revenue_data(10000, 20, 50)
        self.assertIn('units', data)
        self.assertIn('total_cost', data)
        self.assertIn('total_revenue', data)
        self.assertGreater(len(data['units']), 0)


class TestAIEngine(BaseTestCase):
    """Tests for AI Analysis Engine."""

    def test_risk_classification_low(self):
        ai = AIAnalysisEngine(model_dir=os.path.join(self.app.config['MODEL_DIR']))
        fin_data = {
            'fixed_costs': 5000,
            'variable_cost_per_unit': 5,
            'selling_price_per_unit': 50,
            'expected_production_volume': 5000,
        }
        analysis = FinancialEngine.full_analysis(5000, 5, 50, 5000)
        risk = ai.classify_risk(fin_data, analysis)
        self.assertIn(risk['risk_level'], ['low', 'medium'])
        self.assertIn('risk_score', risk)

    def test_risk_classification_high(self):
        ai = AIAnalysisEngine(model_dir=os.path.join(self.app.config['MODEL_DIR']))
        fin_data = {
            'fixed_costs': 100000,
            'variable_cost_per_unit': 45,
            'selling_price_per_unit': 50,
            'expected_production_volume': 1000,
        }
        analysis = FinancialEngine.full_analysis(100000, 45, 50, 1000)
        risk = ai.classify_risk(fin_data, analysis)
        self.assertIn(risk['risk_level'], ['high', 'critical'])

    def test_feasibility_evaluation(self):
        ai = AIAnalysisEngine(model_dir=os.path.join(self.app.config['MODEL_DIR']))
        fin_data = {
            'fixed_costs': 10000,
            'variable_cost_per_unit': 10,
            'selling_price_per_unit': 50,
            'expected_production_volume': 2000,
        }
        analysis = FinancialEngine.full_analysis(10000, 10, 50, 2000)
        feas = ai.evaluate_feasibility(fin_data, analysis)
        self.assertIn('feasibility_score', feas)
        self.assertIn('verdict', feas)
        self.assertGreaterEqual(feas['feasibility_score'], 0)
        self.assertLessEqual(feas['feasibility_score'], 100)


class TestRecommendationEngine(BaseTestCase):
    """Tests for Recommendation Engine."""

    def test_generates_recommendations(self):
        fin_data = {
            'fixed_costs': 50000,
            'variable_cost_per_unit': 40,
            'selling_price_per_unit': 50,
            'expected_production_volume': 2000,
        }
        analysis = FinancialEngine.full_analysis(50000, 40, 50, 2000)
        risk = {'risk_level': 'high', 'risk_score': 65}
        feas = {'feasibility_score': 40, 'verdict': 'Marginal'}
        recs = RecommendationEngine.generate(fin_data, analysis, risk, feas)
        self.assertGreater(len(recs), 0)
        self.assertIn('category', recs[0])
        self.assertIn('title', recs[0])

    def test_critical_recommendation_for_impossible_bep(self):
        fin_data = {
            'fixed_costs': 50000,
            'variable_cost_per_unit': 60,
            'selling_price_per_unit': 50,
            'expected_production_volume': 1000,
        }
        analysis = FinancialEngine.full_analysis(50000, 60, 50, 1000)
        risk = {'risk_level': 'critical', 'risk_score': 90}
        feas = {'feasibility_score': 10, 'verdict': 'Not Feasible'}
        recs = RecommendationEngine.generate(fin_data, analysis, risk, feas)
        critical = [r for r in recs if r['priority'] == 'critical']
        self.assertGreater(len(critical), 0)


class TestPredictionEngine(BaseTestCase):
    """Tests for Prediction Engine."""

    def test_monthly_forecast(self):
        fin_data = {
            'fixed_costs': 12000,
            'variable_cost_per_unit': 5,
            'selling_price_per_unit': 20,
            'expected_production_volume': 6000,
        }
        analysis = FinancialEngine.full_analysis(12000, 5, 20, 6000)
        forecast = PredictionEngine.forecast_monthly(fin_data, analysis, months=12)
        self.assertEqual(len(forecast['series']), 12)
        self.assertIn('total_revenue', forecast)
        self.assertIn('payback_month', forecast)

    def test_profitability_prediction(self):
        fin_data = {
            'fixed_costs': 10000,
            'variable_cost_per_unit': 10,
            'selling_price_per_unit': 40,
            'expected_production_volume': 2000,
        }
        pred = PredictionEngine.predict_profitability(fin_data)
        self.assertIn('predicted_profitability', pred)
        self.assertIn('confidence', pred)


class TestAuthRoutes(BaseTestCase):
    """Tests for authentication routes."""

    def test_register_page(self):
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Account', response.data)

    def test_login_page(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign in', response.data)

    def test_register_and_login(self):
        # Register
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Login
        response = self.login('newuser', 'password123')
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        self.create_user()
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword',
        }, follow_redirects=True)
        self.assertIn(b'Invalid', response.data)


class TestProjectRoutes(BaseTestCase):
    """Tests for project CRUD routes."""

    def test_create_project(self):
        self.create_user()
        self.login()

        response = self.client.post('/projects/new', data={
            'name': 'Test Project',
            'industry': 'Technology',
            'currency': 'USD',
            'fixed_costs': '10000',
            'variable_cost_per_unit': '5',
            'selling_price_per_unit': '25',
            'expected_production_volume': '2000',
            'initial_investment': '20000',
            'time_horizon_months': '12',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Project', response.data)

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Sign in', response.data)


if __name__ == '__main__':
    unittest.main()
