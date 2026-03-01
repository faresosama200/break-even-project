"""
Input Validators
================
Server-side validation for all user inputs.
"""

import re


def validate_registration(username: str, email: str, password: str, confirm_password: str) -> list:
    """Validate user registration inputs. Returns list of error messages."""
    errors = []

    # Username
    if not username or len(username.strip()) < 3:
        errors.append('Username must be at least 3 characters.')
    elif len(username) > 80:
        errors.append('Username must not exceed 80 characters.')
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append('Username can only contain letters, numbers, and underscores.')

    # Email
    if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        errors.append('Please provide a valid email address.')

    # Password
    if not password or len(password) < 8:
        errors.append('Password must be at least 8 characters.')
    elif len(password) > 128:
        errors.append('Password must not exceed 128 characters.')

    if password != confirm_password:
        errors.append('Passwords do not match.')

    return errors


def validate_financial_input(data: dict) -> list:
    """Validate financial input data. Returns list of error messages."""
    errors = []
    required_fields = {
        'fixed_costs': 'Fixed Costs',
        'variable_cost_per_unit': 'Variable Cost per Unit',
        'selling_price_per_unit': 'Selling Price per Unit',
        'expected_production_volume': 'Expected Production Volume',
    }

    for field, label in required_fields.items():
        val = data.get(field)
        if val is None or val == '':
            errors.append(f'{label} is required.')
            continue
        try:
            num = float(val)
            if num < 0:
                errors.append(f'{label} cannot be negative.')
        except (ValueError, TypeError):
            errors.append(f'{label} must be a valid number.')

    # Business logic validations
    try:
        selling = float(data.get('selling_price_per_unit', 0))
        variable = float(data.get('variable_cost_per_unit', 0))
        if selling > 0 and variable > 0 and selling <= variable:
            errors.append('Selling price must be greater than variable cost per unit.')
    except (ValueError, TypeError):
        pass

    try:
        volume = data.get('expected_production_volume')
        if volume is not None and volume != '':
            vol_int = int(float(volume))
            if vol_int < 1:
                errors.append('Expected production volume must be at least 1.')
    except (ValueError, TypeError):
        pass

    return errors


def validate_project(name: str, description: str = '') -> list:
    """Validate project creation inputs."""
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append('Project name must be at least 2 characters.')
    elif len(name) > 200:
        errors.append('Project name must not exceed 200 characters.')
    if description and len(description) > 2000:
        errors.append('Description must not exceed 2000 characters.')
    return errors


def sanitize_string(value: str) -> str:
    """Sanitize a string input by stripping and escaping."""
    if not value:
        return ''
    return value.strip()
