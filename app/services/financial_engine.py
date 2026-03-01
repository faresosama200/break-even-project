"""
Financial Engine Service
========================
Core financial calculations: break-even point, margins, ROI, cost analysis.
All calculations are pure functions — no side effects.
"""

import math
from typing import Optional


class FinancialEngine:
    """Stateless financial calculation engine."""

    @staticmethod
    def calculate_break_even_units(fixed_costs: float, selling_price: float,
                                    variable_cost: float) -> Optional[float]:
        """
        Calculate break-even point in units.
        BEP (units) = Fixed Costs / (Selling Price - Variable Cost)
        """
        contribution = selling_price - variable_cost
        if contribution <= 0:
            return None  # Cannot break even
        return fixed_costs / contribution

    @staticmethod
    def calculate_break_even_revenue(fixed_costs: float, selling_price: float,
                                      variable_cost: float) -> Optional[float]:
        """
        Calculate break-even point in revenue.
        BEP (revenue) = Fixed Costs / Contribution Margin Ratio
        """
        if selling_price <= 0:
            return None
        cm_ratio = (selling_price - variable_cost) / selling_price
        if cm_ratio <= 0:
            return None
        return fixed_costs / cm_ratio

    @staticmethod
    def calculate_contribution_margin(selling_price: float,
                                       variable_cost: float) -> float:
        """Contribution Margin = Selling Price - Variable Cost."""
        return selling_price - variable_cost

    @staticmethod
    def calculate_contribution_margin_ratio(selling_price: float,
                                             variable_cost: float) -> Optional[float]:
        """Contribution Margin Ratio = CM / Selling Price."""
        if selling_price <= 0:
            return None
        return (selling_price - variable_cost) / selling_price

    @staticmethod
    def calculate_expected_profit(fixed_costs: float, variable_cost: float,
                                   selling_price: float, volume: int) -> float:
        """Expected Profit = Revenue - Total Costs."""
        revenue = selling_price * volume
        total_cost = fixed_costs + (variable_cost * volume)
        return revenue - total_cost

    @staticmethod
    def calculate_expected_revenue(selling_price: float, volume: int) -> float:
        """Total Revenue = Price × Volume."""
        return selling_price * volume

    @staticmethod
    def calculate_profit_margin(profit: float, revenue: float) -> Optional[float]:
        """Profit Margin % = (Profit / Revenue) × 100."""
        if revenue <= 0:
            return None
        return (profit / revenue) * 100

    @staticmethod
    def calculate_roi(profit: float, initial_investment: float) -> Optional[float]:
        """ROI % = (Profit / Investment) × 100."""
        if initial_investment <= 0:
            return None
        return (profit / initial_investment) * 100

    @staticmethod
    def calculate_safety_margin(expected_volume: int,
                                 break_even_units: float) -> dict:
        """
        Safety Margin = Expected Volume - BEP.
        Safety Margin % = (Safety Margin / Expected Volume) × 100.
        """
        margin = expected_volume - break_even_units
        percentage = (margin / expected_volume * 100) if expected_volume > 0 else 0
        return {
            'safety_margin': margin,
            'safety_margin_percentage': percentage,
        }

    @classmethod
    def full_analysis(cls, fixed_costs: float, variable_cost: float,
                      selling_price: float, volume: int,
                      initial_investment: float = 0.0) -> dict:
        """
        Perform complete financial analysis. Returns a dictionary with all metrics.
        """
        bep_units = cls.calculate_break_even_units(fixed_costs, selling_price, variable_cost)
        bep_revenue = cls.calculate_break_even_revenue(fixed_costs, selling_price, variable_cost)
        cm = cls.calculate_contribution_margin(selling_price, variable_cost)
        cm_ratio = cls.calculate_contribution_margin_ratio(selling_price, variable_cost)
        revenue = cls.calculate_expected_revenue(selling_price, volume)
        profit = cls.calculate_expected_profit(fixed_costs, variable_cost, selling_price, volume)
        profit_margin = cls.calculate_profit_margin(profit, revenue)

        investment = initial_investment if initial_investment > 0 else fixed_costs
        roi = cls.calculate_roi(profit, investment)

        safety = cls.calculate_safety_margin(volume, bep_units) if bep_units else {
            'safety_margin': None, 'safety_margin_percentage': None
        }

        return {
            'break_even_units': round(bep_units, 2) if bep_units else None,
            'break_even_revenue': round(bep_revenue, 2) if bep_revenue else None,
            'contribution_margin': round(cm, 2),
            'contribution_margin_ratio': round(cm_ratio, 4) if cm_ratio else None,
            'expected_revenue': round(revenue, 2),
            'expected_profit': round(profit, 2),
            'profit_margin': round(profit_margin, 2) if profit_margin is not None else None,
            'roi_percentage': round(roi, 2) if roi is not None else None,
            'safety_margin': round(safety['safety_margin'], 2) if safety['safety_margin'] is not None else None,
            'safety_margin_percentage': round(safety['safety_margin_percentage'], 2) if safety['safety_margin_percentage'] is not None else None,
        }

    @staticmethod
    def generate_cost_revenue_data(fixed_costs: float, variable_cost: float,
                                    selling_price: float, max_units: int = 0,
                                    points: int = 50) -> dict:
        """
        Generate data points for Cost vs Revenue chart.
        Returns lists of {units, total_cost, total_revenue, profit}.
        """
        if max_units <= 0:
            # Auto-scale to 2x break-even
            cm = selling_price - variable_cost
            if cm > 0:
                bep = fixed_costs / cm
                max_units = int(math.ceil(bep * 2.5))
            else:
                max_units = 1000

        max_units = max(max_units, 10)
        step = max(1, max_units // points)
        data = {'units': [], 'total_cost': [], 'total_revenue': [], 'profit': []}

        for u in range(0, max_units + 1, step):
            tc = fixed_costs + variable_cost * u
            tr = selling_price * u
            data['units'].append(u)
            data['total_cost'].append(round(tc, 2))
            data['total_revenue'].append(round(tr, 2))
            data['profit'].append(round(tr - tc, 2))

        return data
