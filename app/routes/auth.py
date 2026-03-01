"""
Authentication Routes
=====================
User registration, login, logout, and profile management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.database import db
from app.models.user import User
from app.utils.validators import validate_registration, sanitize_string

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = sanitize_string(request.form.get('username', ''))
        email = sanitize_string(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = sanitize_string(request.form.get('full_name', ''))
        company_name = sanitize_string(request.form.get('company_name', ''))

        errors = validate_registration(username, email, password, confirm_password)

        # Check uniqueness
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html',
                                   username=username, email=email,
                                   full_name=full_name, company_name=company_name)

        user = User(
            username=username,
            email=email,
            full_name=full_name or None,
            company_name=company_name or None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = sanitize_string(request.form.get('username', ''))
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page or url_for('dashboard.index'))

        flash('Invalid username or password.', 'danger')
        return render_template('auth/login.html', username=username)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update user profile."""
    if request.method == 'POST':
        full_name = sanitize_string(request.form.get('full_name', ''))
        company_name = sanitize_string(request.form.get('company_name', ''))
        current_user.full_name = full_name or None
        current_user.company_name = company_name or None
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
