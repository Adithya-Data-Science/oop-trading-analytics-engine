# Object-Oriented Python Trading Analytics Engine

A testable quantitative research application demonstrating object-oriented Python design, strategy abstraction, transaction-cost-aware backtesting, and risk analytics.

## Architecture

- `PricePanel` validates a multi-asset price matrix and exposes returns.
- `Strategy` defines an interchangeable strategy interface.
- `MomentumStrategy` implements lagged cross-sectional ranking and scheduled rebalancing.
- `BacktestEngine` applies prior-day holdings, turnover, and proportional transaction costs without look-ahead.
- `RiskEngine` reports annualized return/volatility, Sharpe ratio, maximum drawdown, and historical 95% daily VaR.

## Reproduce

```bash
python -m venv .venv
pip install -r requirements.txt
python -m oop_engine.demo
pytest -q tests
```

## Start-to-finish workflow

1. Generate a validated multi-asset price panel.
2. Calculate lagged momentum signals through a `Strategy` implementation.
3. Convert signals into target portfolio weights at scheduled rebalance dates.
4. Apply yesterday's holdings to today's returns to avoid look-ahead.
5. Measure turnover and deduct transaction costs.
6. Compute risk and performance metrics.
7. Compare the demo output with `reference_metrics.json` and verify behavior with pytest.
8. Swap in another strategy class without changing the backtest or risk engine.

## Repository map

- `oop_engine/core.py` - validated data object, strategy abstraction, momentum strategy, backtest engine, and risk engine
- `oop_engine/demo.py` - end-to-end reproducible run
- `tests/test_core.py` - unit tests for reproducibility, portfolio constraints, costs, and risk
- `reference_metrics.json` - stored reference output
- `requirements.txt` - dependencies

The demo uses deterministic synthetic data so it can be reproduced without credentials. It is an engineering demonstration, not evidence of live alpha.
