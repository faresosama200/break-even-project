#!/usr/bin/env python3
"""
Database Seed Script
====================
Populates the database with sample data for testing and demonstration.
Run with: python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.database import db
from app.models.user import User
from app.models.project import Project
from app.models.financial_input import FinancialInput
from app.routes.projects import _run_analysis_pipeline


SAMPLE_PROJECTS = [
    {
        'name': 'Organic Soap Production',
        'description': 'Small-batch artisan soap manufacturing for local markets.',
        'industry': 'Manufacturing',
        'currency': 'USD',
        'financials': {
            'fixed_costs': 15000,
            'variable_cost_per_unit': 3.50,
            'selling_price_per_unit': 12.00,
            'expected_production_volume': 5000,
            'initial_investment': 25000,
            'time_horizon_months': 12,
        },
    },
    {
        'name': 'Coffee Shop Startup',
        'description': 'Specialty coffee shop in a suburban area.',
        'industry': 'Food & Beverage',
        'currency': 'USD',
        'financials': {
            'fixed_costs': 45000,
            'variable_cost_per_unit': 2.20,
            'selling_price_per_unit': 5.50,
            'expected_production_volume': 20000,
            'initial_investment': 80000,
            'time_horizon_months': 12,
        },
    },
    {
        'name': 'Mobile App Development',
        'description': 'SaaS mobile application for task management.',
        'industry': 'Technology',
        'currency': 'USD',
        'financials': {
            'fixed_costs': 60000,
            'variable_cost_per_unit': 0.50,
            'selling_price_per_unit': 9.99,
            'expected_production_volume': 10000,
            'initial_investment': 100000,
            'time_horizon_months': 18,
        },
    },
    {
        'name': 'Handmade Jewelry',
        'description': 'Custom handmade jewelry sold through an online store.',
        'industry': 'Handcraft',
        'currency': 'USD',
        'financials': {
            'fixed_costs': 5000,
            'variable_cost_per_unit': 15.00,
            'selling_price_per_unit': 55.00,
            'expected_production_volume': 500,
            'initial_investment': 8000,
            'time_horizon_months': 12,
        },
    },
    {
        'name': 'Urban Farming Microgreens',
        'description': 'Indoor microgreens farm supplying restaurants.',
        'industry': 'Agriculture',
        'currency': 'USD',
        'financials': {
            'fixed_costs': 8000,
            'variable_cost_per_unit': 1.20,
            'selling_price_per_unit': 4.00,
            'expected_production_volume': 8000,
            'initial_investment': 15000,
            'time_horizon_months': 12,
        },
    },
    {
        'name': 'Risky Gadget Venture',
        'description': 'Consumer electronics gadget with high costs and tight margins.',
        'industry': 'Technology',
        'currency': 'USD',
        'financials': {
            'fixed_costs': 120000,
            'variable_cost_per_unit': 45.00,
            'selling_price_per_unit': 50.00,
            'expected_production_volume': 3000,
            'initial_investment': 200000,
            'time_horizon_months': 12,
        },
    },
]


def seed():
    """Seed the database with demo user and sample projects."""
    app = create_app('development')

    with app.app_context():
        # Check if already seeded
        if User.query.filter_by(username='demo').first():
            print('Database already seeded. Skipping.')
            return

        # Create demo user
        user = User(
            username='demo',
            email='demo@smartbep.com',
            full_name='Demo User',
            company_name='SmartBEP Demo',
        )
        user.set_password('demo1234')
        db.session.add(user)
        db.session.flush()
        print(f'Created demo user: demo / demo1234')

        # Create sample projects with full analysis
        for proj_data in SAMPLE_PROJECTS:
            project = Project(
                user_id=user.id,
                name=proj_data['name'],
                description=proj_data['description'],
                industry=proj_data['industry'],
                currency=proj_data['currency'],
                status='analyzed',
            )
            db.session.add(project)
            db.session.flush()

            fin = FinancialInput(
                project_id=project.id,
                fixed_costs=proj_data['financials']['fixed_costs'],
                variable_cost_per_unit=proj_data['financials']['variable_cost_per_unit'],
                selling_price_per_unit=proj_data['financials']['selling_price_per_unit'],
                expected_production_volume=proj_data['financials']['expected_production_volume'],
                initial_investment=proj_data['financials'].get('initial_investment', 0),
                time_horizon_months=proj_data['financials'].get('time_horizon_months', 12),
            )
            db.session.add(fin)
            db.session.flush()

            _run_analysis_pipeline(project, fin)
            print(f'  Created project: {project.name}')

        db.session.commit()
        print(f'\nSeeding complete! {len(SAMPLE_PROJECTS)} projects created.')
        print('Login: demo / demo1234')


if __name__ == '__main__':
    seed()
