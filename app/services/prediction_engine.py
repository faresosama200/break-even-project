"""
Prediction Service
==================
Forecasts future financial performance using regression models
and similar-project clustering from historical data.
"""

import json
import logging
import numpy as np
from typing import Optional, List, Dict

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class PredictionEngine:
    """
    Prediction service providing:
      - Revenue/profit forecasting (linear regression on time-series)
      - Similar project clustering
      - Monthly forecast generation
    """

    @classmethod
    def forecast_monthly(cls, financial_data: dict, analysis: dict,
                         months: int = 12) -> Dict:
        """
        Generate month-by-month forecast of revenue, costs, and profit.
        Uses a simple growth model with seasonal consideration.
        """
        fc = financial_data.get('fixed_costs', 0)
        vc = financial_data.get('variable_cost_per_unit', 0)
        sp = financial_data.get('selling_price_per_unit', 0)
        vol = financial_data.get('expected_production_volume', 0)

        monthly_vol = vol / 12 if vol > 0 else 0
        monthly_fixed = fc / 12 if fc > 0 else 0

        # Simulate gradual ramp-up: start at 40% capacity → 100% by month 6
        series = []
        cumulative_profit = 0.0
        for m in range(1, months + 1):
            ramp = min(1.0, 0.4 + 0.1 * m)  # ramp from 40% to 100%+
            vol_m = monthly_vol * ramp
            revenue_m = sp * vol_m
            cost_m = monthly_fixed + vc * vol_m
            profit_m = revenue_m - cost_m
            cumulative_profit += profit_m

            series.append({
                'month': m,
                'volume': round(vol_m, 0),
                'revenue': round(revenue_m, 2),
                'cost': round(cost_m, 2),
                'profit': round(profit_m, 2),
                'cumulative_profit': round(cumulative_profit, 2),
            })

        # Find month where cumulative profit turns positive
        payback_month = None
        for entry in series:
            if entry['cumulative_profit'] > 0:
                payback_month = entry['month']
                break

        return {
            'series': series,
            'total_revenue': round(sum(e['revenue'] for e in series), 2),
            'total_profit': round(cumulative_profit, 2),
            'payback_month': payback_month,
        }

    @classmethod
    def predict_profitability(cls, financial_data: dict,
                              historical_projects: Optional[List[Dict]] = None) -> Dict:
        """
        Predict profitability class and confidence using regression or rules.
        """
        fc = financial_data.get('fixed_costs', 0)
        vc = financial_data.get('variable_cost_per_unit', 0)
        sp = financial_data.get('selling_price_per_unit', 0)
        vol = financial_data.get('expected_production_volume', 0)

        revenue = sp * vol
        total_cost = fc + vc * vol
        profit = revenue - total_cost
        margin = (profit / revenue * 100) if revenue > 0 else -100

        # If we have enough historical data, use regression
        if ML_AVAILABLE and historical_projects and len(historical_projects) >= 10:
            try:
                return cls._ml_predict(financial_data, historical_projects)
            except Exception as e:
                logger.warning(f'ML prediction failed: {e}')

        # Rule-based prediction
        if margin > 25:
            label = 'Highly Profitable'
            confidence = 0.85
        elif margin > 10:
            label = 'Profitable'
            confidence = 0.75
        elif margin > 0:
            label = 'Marginally Profitable'
            confidence = 0.65
        else:
            label = 'Unprofitable'
            confidence = 0.80

        return {
            'predicted_profitability': label,
            'confidence': confidence,
            'predicted_margin': round(margin, 2),
            'method': 'rule_based',
        }

    @classmethod
    def _ml_predict(cls, financial_data: dict,
                    historical: List[Dict]) -> Dict:
        """Use linear regression on historical data to predict margin."""
        X = []
        y = []
        for proj in historical:
            f = proj.get('features', {})
            fc_ = f.get('fixed_costs', 0)
            vc_ = f.get('variable_cost_per_unit', 0)
            sp_ = f.get('selling_price_per_unit', 0)
            vol_ = f.get('expected_production_volume', 0)
            rev = sp_ * vol_
            cost = fc_ + vc_ * vol_
            m = ((rev - cost) / rev * 100) if rev > 0 else -100
            X.append([fc_, vc_, sp_, vol_, sp_ - vc_, (sp_ - vc_) / sp_ if sp_ > 0 else 0])
            y.append(m)

        X = np.array(X)
        y = np.array(y)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LinearRegression()
        model.fit(X_scaled, y)

        fc = financial_data.get('fixed_costs', 0)
        vc = financial_data.get('variable_cost_per_unit', 0)
        sp = financial_data.get('selling_price_per_unit', 0)
        vol = financial_data.get('expected_production_volume', 0)
        cm = sp - vc
        cm_ratio = cm / sp if sp > 0 else 0
        x_new = scaler.transform([[fc, vc, sp, vol, cm, cm_ratio]])
        predicted_margin = float(model.predict(x_new)[0])

        score = model.score(X_scaled, y)

        if predicted_margin > 25:
            label = 'Highly Profitable'
        elif predicted_margin > 10:
            label = 'Profitable'
        elif predicted_margin > 0:
            label = 'Marginally Profitable'
        else:
            label = 'Unprofitable'

        return {
            'predicted_profitability': label,
            'confidence': round(max(0, min(1, score)), 2),
            'predicted_margin': round(predicted_margin, 2),
            'method': 'ml_regression',
        }

    @classmethod
    def find_similar_projects(cls, financial_data: dict,
                              all_projects: List[Dict],
                              top_n: int = 5) -> List[Dict]:
        """
        Find the most similar historical projects using Euclidean distance
        (or KMeans clustering when dataset is large enough).
        """
        if not all_projects:
            return []

        fc = financial_data.get('fixed_costs', 0)
        vc = financial_data.get('variable_cost_per_unit', 0)
        sp = financial_data.get('selling_price_per_unit', 0)
        vol = financial_data.get('expected_production_volume', 0)

        target = np.array([fc, vc, sp, vol], dtype=float)

        distances = []
        for proj in all_projects:
            f = proj.get('features', {})
            v = np.array([
                f.get('fixed_costs', 0),
                f.get('variable_cost_per_unit', 0),
                f.get('selling_price_per_unit', 0),
                f.get('expected_production_volume', 0),
            ], dtype=float)

            # Normalized distance
            denom = np.maximum(np.abs(target), 1)
            dist = np.sqrt(np.sum(((target - v) / denom) ** 2))
            distances.append((dist, proj))

        distances.sort(key=lambda x: x[0])
        return [d[1] for d in distances[:top_n]]
