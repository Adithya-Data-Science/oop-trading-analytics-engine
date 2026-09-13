import pandas as pd
from oop_engine.core import BacktestEngine, MomentumStrategy, RiskEngine, generate_synthetic_prices

def test_synthetic_prices_reproducible():
    pd.testing.assert_frame_equal(generate_synthetic_prices(seed=3).prices, generate_synthetic_prices(seed=3).prices)

def test_strategy_weights_sum_to_one_or_zero():
    panel = generate_synthetic_prices(assets=6, periods=80, seed=5)
    weights = MomentumStrategy(10, 2, 5).target_weights(panel.prices)
    assert (weights.sum(axis=1) <= 1.0 + 1e-12).all()
    assert (weights >= 0.0).all().all()

def test_backtest_is_cost_aware():
    panel = generate_synthetic_prices(assets=6, periods=100, seed=9)
    result = BacktestEngine(MomentumStrategy(10, 2, 5), cost_bps=7.5).run(panel)
    assert result['metrics']['total_transaction_cost'] >= 0.0
    assert result['turnover'].max() <= 2.0 + 1e-12

def test_risk_engine_reports_drawdown():
    metrics = RiskEngine().summary(pd.Series([0.01, -0.02, 0.015, 0.0, 0.005]))
    assert metrics['max_drawdown'] <= 0.0
    assert metrics['annualized_volatility'] > 0.0
