import json
from oop_engine.core import BacktestEngine, MomentumStrategy, generate_synthetic_prices

panel = generate_synthetic_prices(assets=8, periods=504, seed=7)
result = BacktestEngine(MomentumStrategy(20, 3, 5), cost_bps=5.0).run(panel)
print(json.dumps(result['metrics'], indent=2))
