"""
AI Analysis Engine
==================
Machine learning service for feasibility evaluation, risk classification,
and profitability prediction using scikit-learn.
"""

import os
import json
import logging
import numpy as np
from typing import Optional

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIAnalysisEngine:
    """
    ML-based analysis engine for risk classification and feasibility scoring.
    Uses a rule-based fallback when insufficient training data exists, then
    transitions to trained ML models as historical data accumulates.
    """

    RISK_LEVELS = ['low', 'medium', 'high', 'critical']
    MIN_TRAINING_SAMPLES = 20

    def __init__(self, model_dir: str = 'data/models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.risk_model = None
        self.feasibility_model = None
        self.scaler = None
        self._load_models()

    def _model_path(self, name: str) -> str:
        return os.path.join(self.model_dir, f'{name}.pkl')

    def _load_models(self):
        """Load persisted models if available."""
        if not ML_AVAILABLE:
            logger.warning('scikit-learn not available. Using rule-based analysis only.')
            return
        try:
            risk_path = self._model_path('risk_classifier')
            feas_path = self._model_path('feasibility_regressor')
            if os.path.exists(risk_path):
                self.risk_model = joblib.load(risk_path)
                logger.info('Risk classifier model loaded.')
            if os.path.exists(feas_path):
                self.feasibility_model = joblib.load(feas_path)
                logger.info('Feasibility regressor model loaded.')
        except Exception as e:
            logger.error(f'Error loading models: {e}')

    def _extract_features(self, financial_data: dict) -> np.ndarray:
        """Extract feature vector from financial input data."""
        fc = financial_data.get('fixed_costs', 0)
        vc = financial_data.get('variable_cost_per_unit', 0)
        sp = financial_data.get('selling_price_per_unit', 0)
        vol = financial_data.get('expected_production_volume', 0)
        inv = financial_data.get('initial_investment', fc)

        # Derived features
        cm = sp - vc if sp > vc else 0.001
        cm_ratio = cm / sp if sp > 0 else 0
        bep = fc / cm if cm > 0 else float('inf')
        bep_ratio = bep / vol if vol > 0 else float('inf')
        revenue = sp * vol
        total_cost = fc + vc * vol
        profit = revenue - total_cost
        profit_margin = profit / revenue if revenue > 0 else -1
        roi = profit / inv if inv > 0 else 0
        safety_margin = (vol - bep) / vol if vol > 0 and bep != float('inf') else -1

        features = [
            fc, vc, sp, vol,
            cm, cm_ratio,
            min(bep, 1e9),
            min(bep_ratio, 100),
            revenue, total_cost, profit,
            profit_margin, roi, safety_margin
        ]
        return np.array(features).reshape(1, -1)

    def classify_risk(self, financial_data: dict, analysis: dict) -> dict:
        """
        Classify project risk level. Uses ML model if trained, else rules.
        Returns: {risk_level, risk_score, method}
        """
        # Try ML prediction first
        if self.risk_model and ML_AVAILABLE:
            try:
                features = self._extract_features(financial_data)
                risk_idx = self.risk_model.predict(features)[0]
                probas = self.risk_model.predict_proba(features)[0]
                risk_score = round(float(probas[risk_idx]) * 100, 1)
                return {
                    'risk_level': self.RISK_LEVELS[risk_idx],
                    'risk_score': risk_score,
                    'method': 'ml_model',
                }
            except Exception as e:
                logger.warning(f'ML risk prediction failed, falling back to rules: {e}')

        # Rule-based fallback
        return self._rule_based_risk(financial_data, analysis)

    def _rule_based_risk(self, financial_data: dict, analysis: dict) -> dict:
        """Deterministic risk classification based on financial metrics."""
        score = 50  # Start neutral

        bep = analysis.get('break_even_units')
        vol = financial_data.get('expected_production_volume', 0)
        profit_margin = analysis.get('profit_margin', 0)
        safety_pct = analysis.get('safety_margin_percentage', 0)
        roi = analysis.get('roi_percentage', 0)
        cm_ratio = analysis.get('contribution_margin_ratio', 0)

        # Break-even reachability
        if bep is None:
            score += 40  # Cannot break even
        else:
            bep_ratio = bep / vol if vol > 0 else 999
            if bep_ratio > 1.0:
                score += 30
            elif bep_ratio > 0.8:
                score += 20
            elif bep_ratio > 0.5:
                score += 5
            else:
                score -= 15

        # Profit margin impact
        if profit_margin is not None:
            if profit_margin < 0:
                score += 20
            elif profit_margin < 10:
                score += 10
            elif profit_margin > 30:
                score -= 15
            else:
                score -= 5

        # Safety margin
        if safety_pct is not None:
            if safety_pct < 0:
                score += 15
            elif safety_pct < 20:
                score += 5
            elif safety_pct > 50:
                score -= 10

        # CM ratio
        if cm_ratio is not None:
            if cm_ratio < 0.2:
                score += 10
            elif cm_ratio > 0.5:
                score -= 10

        # ROI
        if roi is not None:
            if roi < 0:
                score += 15
            elif roi < 10:
                score += 5
            elif roi > 50:
                score -= 10

        score = max(0, min(100, score))

        if score >= 75:
            level = 'critical'
        elif score >= 55:
            level = 'high'
        elif score >= 35:
            level = 'medium'
        else:
            level = 'low'

        return {
            'risk_level': level,
            'risk_score': score,
            'method': 'rule_based',
        }

    def evaluate_feasibility(self, financial_data: dict, analysis: dict) -> dict:
        """
        Evaluate overall project feasibility on a 0-100 scale.
        Returns: {feasibility_score, verdict, factors}
        """
        if self.feasibility_model and ML_AVAILABLE:
            try:
                features = self._extract_features(financial_data)
                feas_score = float(self.feasibility_model.predict(features)[0])
                feas_score = max(0, min(100, feas_score))
                verdict = self._feasibility_verdict(feas_score)
                return {
                    'feasibility_score': round(feas_score, 1),
                    'verdict': verdict,
                    'method': 'ml_model',
                }
            except Exception as e:
                logger.warning(f'ML feasibility prediction failed: {e}')

        return self._rule_based_feasibility(financial_data, analysis)

    def _rule_based_feasibility(self, financial_data: dict, analysis: dict) -> dict:
        """Rule-based feasibility scoring."""
        score = 50
        factors = []

        bep = analysis.get('break_even_units')
        vol = financial_data.get('expected_production_volume', 0)
        profit = analysis.get('expected_profit', 0)
        margin = analysis.get('profit_margin')
        roi = analysis.get('roi_percentage')
        safety_pct = analysis.get('safety_margin_percentage')

        if bep is None:
            score -= 30
            factors.append('Cannot reach break-even: price too low')
        elif vol > 0:
            ratio = bep / vol
            if ratio < 0.4:
                score += 20
                factors.append('Excellent break-even ratio')
            elif ratio < 0.7:
                score += 10
                factors.append('Good break-even ratio')
            elif ratio > 1:
                score -= 20
                factors.append('Cannot reach break-even at expected volume')
            else:
                factors.append('Tight break-even margin')

        if profit > 0:
            score += 10
            factors.append('Project is profitable')
        else:
            score -= 15
            factors.append('Project shows a loss')

        if margin is not None:
            if margin > 25:
                score += 10
                factors.append('Strong profit margin')
            elif margin < 5:
                score -= 10
                factors.append('Very thin profit margin')

        if roi is not None:
            if roi > 30:
                score += 10
                factors.append('Excellent ROI')
            elif roi < 0:
                score -= 10
                factors.append('Negative ROI')

        if safety_pct is not None and safety_pct > 30:
            score += 5
            factors.append('Healthy safety margin')

        score = max(0, min(100, score))
        verdict = self._feasibility_verdict(score)

        return {
            'feasibility_score': round(score, 1),
            'verdict': verdict,
            'factors': factors,
            'method': 'rule_based',
        }

    @staticmethod
    def _feasibility_verdict(score: float) -> str:
        if score >= 75:
            return 'Highly Feasible'
        elif score >= 55:
            return 'Feasible'
        elif score >= 35:
            return 'Marginal'
        else:
            return 'Not Feasible'

    def train_models(self, training_data: list):
        """
        Train risk classifier and feasibility regressor from historical records.
        training_data: list of dicts with 'features' (dict) and 'risk_label' (str) and 'feasibility_score' (float).
        """
        if not ML_AVAILABLE:
            logger.warning('Cannot train: scikit-learn not installed.')
            return

        if len(training_data) < self.MIN_TRAINING_SAMPLES:
            logger.info(f'Insufficient data ({len(training_data)} records). Need {self.MIN_TRAINING_SAMPLES}.')
            return

        try:
            X = []
            y_risk = []
            y_feas = []

            for record in training_data:
                features = self._extract_features(record['features'])[0]
                X.append(features)
                risk_idx = self.RISK_LEVELS.index(record.get('risk_label', 'medium'))
                y_risk.append(risk_idx)
                y_feas.append(record.get('feasibility_score', 50))

            X = np.array(X)
            y_risk = np.array(y_risk)
            y_feas = np.array(y_feas)

            # Train risk classifier
            risk_pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            risk_pipeline.fit(X, y_risk)
            self.risk_model = risk_pipeline
            joblib.dump(risk_pipeline, self._model_path('risk_classifier'))

            # Train feasibility regressor
            feas_pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('reg', GradientBoostingRegressor(n_estimators=100, random_state=42))
            ])
            feas_pipeline.fit(X, y_feas)
            self.feasibility_model = feas_pipeline
            joblib.dump(feas_pipeline, self._model_path('feasibility_regressor'))

            logger.info(f'Models trained on {len(training_data)} records and saved.')
        except Exception as e:
            logger.error(f'Model training failed: {e}')
