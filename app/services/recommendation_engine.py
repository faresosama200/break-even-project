"""
Recommendation Service
======================
Generates intelligent, context-aware business recommendations
based on financial analysis results and risk assessment.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates actionable business recommendations from analysis data."""

    @classmethod
    def generate(cls, financial_data: dict, analysis: dict,
                 risk_info: dict, feasibility_info: dict) -> List[Dict]:
        """
        Generate recommendations based on all analysis facets.
        Returns a list of recommendation dicts.
        """
        recs = []

        recs.extend(cls._cost_recommendations(financial_data, analysis))
        recs.extend(cls._pricing_recommendations(financial_data, analysis))
        recs.extend(cls._production_recommendations(financial_data, analysis))
        recs.extend(cls._risk_alerts(risk_info, analysis))
        recs.extend(cls._general_recommendations(financial_data, analysis, feasibility_info))

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recs.sort(key=lambda r: priority_order.get(r['priority'], 2))

        return recs

    @staticmethod
    def _cost_recommendations(fin: dict, analysis: dict) -> List[Dict]:
        recs = []
        fc = fin.get('fixed_costs', 0)
        vc = fin.get('variable_cost_per_unit', 0)
        sp = fin.get('selling_price_per_unit', 0)
        vol = fin.get('expected_production_volume', 0)

        total_variable = vc * vol
        total_cost = fc + total_variable

        # High fixed-cost ratio
        if total_cost > 0 and fc / total_cost > 0.6:
            recs.append({
                'category': 'cost_reduction',
                'title': 'High Fixed Cost Ratio Detected',
                'description': (
                    f'Fixed costs represent {fc / total_cost * 100:.0f}% of total costs. '
                    'Consider negotiating leases, outsourcing non-core functions, or '
                    'sharing fixed resources to bring this below 50%.'
                ),
                'priority': 'high',
                'impact_score': 75,
            })

        # Variable cost too close to selling price
        if sp > 0 and vc / sp > 0.7:
            recs.append({
                'category': 'cost_reduction',
                'title': 'Variable Costs Near Selling Price',
                'description': (
                    f'Variable cost per unit (${vc:,.2f}) is {vc / sp * 100:.0f}% of the selling price. '
                    'Explore bulk purchasing, alternative suppliers, or process optimization '
                    'to reduce per-unit costs.'
                ),
                'priority': 'high',
                'impact_score': 80,
            })

        # Break-even too high
        bep = analysis.get('break_even_units')
        if bep and vol > 0 and bep / vol > 0.7:
            target_fc = fc * 0.85
            recs.append({
                'category': 'cost_reduction',
                'title': 'Reduce Fixed Costs to Improve Break-Even',
                'description': (
                    f'A 15% fixed cost reduction (to ${target_fc:,.0f}) would significantly '
                    f'lower your break-even point and increase the safety margin.'
                ),
                'priority': 'medium',
                'impact_score': 60,
            })

        return recs

    @staticmethod
    def _pricing_recommendations(fin: dict, analysis: dict) -> List[Dict]:
        recs = []
        sp = fin.get('selling_price_per_unit', 0)
        vc = fin.get('variable_cost_per_unit', 0)
        cm_ratio = analysis.get('contribution_margin_ratio', 0)
        margin = analysis.get('profit_margin')

        if cm_ratio is not None and cm_ratio < 0.3 and sp > 0:
            ideal_price = vc / 0.6  # Target 40% CM ratio
            recs.append({
                'category': 'pricing',
                'title': 'Low Contribution Margin — Consider Price Increase',
                'description': (
                    f'Contribution margin ratio is only {cm_ratio * 100:.1f}%. '
                    f'Raising the unit price to ${ideal_price:,.2f} would achieve a 40% margin, '
                    'improving profitability and break-even speed.'
                ),
                'priority': 'high',
                'impact_score': 70,
            })

        if margin is not None and margin < 10 and margin >= 0:
            recs.append({
                'category': 'pricing',
                'title': 'Thin Profit Margin',
                'description': (
                    f'Profit margin is only {margin:.1f}%. Small cost increases or demand '
                    'drops could push the project into losses. Consider value-based pricing '
                    'or adding premium features to justify higher prices.'
                ),
                'priority': 'medium',
                'impact_score': 55,
            })

        return recs

    @staticmethod
    def _production_recommendations(fin: dict, analysis: dict) -> List[Dict]:
        recs = []
        vol = fin.get('expected_production_volume', 0)
        bep = analysis.get('break_even_units')
        safety_pct = analysis.get('safety_margin_percentage')

        if bep and vol > 0:
            if vol < bep:
                needed = int(bep * 1.2)  # 20% above BEP
                recs.append({
                    'category': 'production',
                    'title': 'Increase Production Volume',
                    'description': (
                        f'Current volume ({vol:,}) is below the break-even point ({bep:,.0f}). '
                        f'Target at least {needed:,} units to achieve profitability with a safety cushion.'
                    ),
                    'priority': 'critical',
                    'impact_score': 90,
                })
            elif safety_pct is not None and safety_pct < 20:
                target = int(bep * 1.3)
                recs.append({
                    'category': 'production',
                    'title': 'Safety Margin Below Target',
                    'description': (
                        f'Safety margin is only {safety_pct:.1f}%. '
                        f'Increasing production to {target:,} units would improve your buffer '
                        'against demand fluctuations.'
                    ),
                    'priority': 'medium',
                    'impact_score': 50,
                })

        if vol > 10000:
            recs.append({
                'category': 'production',
                'title': 'Explore Economies of Scale',
                'description': (
                    'At high volumes, negotiate volume discounts with suppliers, '
                    'invest in automation, and optimize your supply chain for cost savings.'
                ),
                'priority': 'low',
                'impact_score': 40,
            })

        return recs

    @staticmethod
    def _risk_alerts(risk_info: dict, analysis: dict) -> List[Dict]:
        recs = []
        level = risk_info.get('risk_level', 'medium')
        score = risk_info.get('risk_score', 50)

        if level == 'critical':
            recs.append({
                'category': 'risk_alert',
                'title': 'Critical Risk — Reconsider Project Viability',
                'description': (
                    f'Risk score is {score}. This project faces fundamental viability challenges. '
                    'Before proceeding, dramatically restructure costs, pricing, or target market. '
                    'Consider a pivot or phased launch strategy.'
                ),
                'priority': 'critical',
                'impact_score': 95,
            })
        elif level == 'high':
            recs.append({
                'category': 'risk_alert',
                'title': 'High Risk — Mitigation Required',
                'description': (
                    f'Risk score is {score}. Implement cost controls, secure advance orders, '
                    'and maintain cash reserves. Build contingency plans for demand shortfalls.'
                ),
                'priority': 'high',
                'impact_score': 75,
            })

        bep = analysis.get('break_even_units')
        if bep is None:
            recs.append({
                'category': 'risk_alert',
                'title': 'Break-Even Impossible at Current Pricing',
                'description': (
                    'The selling price does not exceed the variable cost per unit. '
                    'The project will incur a loss on every unit sold. '
                    'You must increase the selling price or reduce the variable cost.'
                ),
                'priority': 'critical',
                'impact_score': 100,
            })

        return recs

    @staticmethod
    def _general_recommendations(fin: dict, analysis: dict,
                                  feasibility: dict) -> List[Dict]:
        recs = []
        feas_score = feasibility.get('feasibility_score', 50)
        roi = analysis.get('roi_percentage')

        if feas_score >= 75:
            recs.append({
                'category': 'general',
                'title': 'Strong Feasibility — Scale Confidently',
                'description': (
                    f'Feasibility score of {feas_score:.0f} indicates strong potential. '
                    'Consider investing in marketing and scaling production to maximize returns.'
                ),
                'priority': 'low',
                'impact_score': 45,
            })

        if roi is not None and roi > 100:
            recs.append({
                'category': 'general',
                'title': 'Exceptional ROI Potential',
                'description': (
                    f'Projected ROI of {roi:.0f}% is exceptional. '
                    'Ensure demand projections are realistic and consider reinvesting '
                    'profits for growth.'
                ),
                'priority': 'low',
                'impact_score': 40,
            })

        return recs
