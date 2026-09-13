from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class PricePanel:
    prices: pd.DataFrame
    def __post_init__(self) -> None:
        if self.prices.empty or self.prices.isna().any().any() or (self.prices <= 0).any().any():
            raise ValueError('prices must be non-empty, complete and positive')
    @property
    def returns(self) -> pd.DataFrame:
        return self.prices.pct_change().fillna(0.0)

class Strategy(ABC):
    @abstractmethod
    def target_weights(self, prices: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

@dataclass(frozen=True)
class MomentumStrategy(Strategy):
    lookback: int = 20
    top_n: int = 3
    rebalance_every: int = 5
    def target_weights(self, prices: pd.DataFrame) -> pd.DataFrame:
        momentum = prices / prices.shift(self.lookback) - 1.0
        weights = pd.DataFrame(float('nan'), index=prices.index, columns=prices.columns)
        for i in range(self.lookback, len(prices), self.rebalance_every):
            winners = momentum.iloc[i - 1].nlargest(self.top_n).index
            weights.loc[weights.index[i], :] = 0.0
            weights.loc[weights.index[i], winners] = 1.0 / self.top_n
        return weights.ffill().fillna(0.0).astype(float)

@dataclass(frozen=True)
class RiskEngine:
    periods_per_year: int = 252
    def summary(self, returns: pd.Series) -> dict[str, float]:
        r = returns.dropna()
        mean, std = float(r.mean()), float(r.std(ddof=1))
        annual_return = mean * self.periods_per_year
        annual_vol = std * np.sqrt(self.periods_per_year)
        wealth = (1.0 + r).cumprod()
        drawdown = wealth / wealth.cummax() - 1.0
        return {
            'annualized_return': annual_return,
            'annualized_volatility': annual_vol,
            'sharpe_ratio': annual_return / annual_vol if annual_vol > 0 else 0.0,
            'max_drawdown': float(drawdown.min()),
            'daily_var_95': float(np.quantile(r, 0.05)),
        }

@dataclass
class BacktestEngine:
    strategy: Strategy
    cost_bps: float = 5.0
    risk_engine: RiskEngine = RiskEngine()
    def run(self, panel: PricePanel) -> dict[str, object]:
        target = self.strategy.target_weights(panel.prices)
        held = target.shift(1).fillna(0.0)
        gross = (held * panel.returns).sum(axis=1)
        turnover = target.diff().abs().sum(axis=1).fillna(target.abs().sum(axis=1))
        costs = turnover * self.cost_bps / 10000.0
        net = gross - costs
        metrics = self.risk_engine.summary(net)
        metrics['average_daily_turnover'] = float(turnover.mean())
        metrics['total_transaction_cost'] = float(costs.sum())
        return {'returns': net, 'weights': target, 'turnover': turnover, 'metrics': metrics}

def generate_synthetic_prices(assets: int = 8, periods: int = 504, seed: int = 7) -> PricePanel:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2024-01-02', periods=periods)
    vol = 0.22
    drift = np.linspace(0.02, 0.16, assets)
    dt = 1 / 252
    shocks = rng.standard_normal((periods - 1, assets))
    log_ret = (drift - 0.5 * vol**2) * dt + vol * np.sqrt(dt) * shocks
    log_price = np.vstack([np.zeros(assets), np.cumsum(log_ret, axis=0)])
    prices = 100.0 * np.exp(log_price)
    return PricePanel(pd.DataFrame(prices, index=dates, columns=[f'Asset_{i+1}' for i in range(assets)]))
