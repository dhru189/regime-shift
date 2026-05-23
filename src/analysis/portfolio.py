"""
src/analysis/portfolio.py

Regime-aware portfolio construction.
Switches allocation based on detected regime probabilities.
"""

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns


# ── Regime Allocation Maps ────────────────────────────────────────────────────

# Hard-coded allocation targets per regime
# Adjust these based on your regime labeling from the HMM
REGIME_ALLOCATIONS = {
    "bull": {
        "SPY": 0.40,
        "QQQ": 0.20,
        "EFA": 0.15,
        "TLT": 0.10,
        "IEF": 0.05,
        "GLD": 0.05,
        "cash": 0.05,
    },
    "bear": {
        "SPY": 0.10,
        "QQQ": 0.05,
        "EFA": 0.05,
        "TLT": 0.30,
        "IEF": 0.20,
        "GLD": 0.20,
        "cash": 0.10,
    },
    "crisis": {
        "SPY": 0.05,
        "QQQ": 0.00,
        "EFA": 0.00,
        "TLT": 0.25,
        "IEF": 0.25,
        "GLD": 0.25,
        "cash": 0.20,
    }
}


# ── Soft Allocation (Probability Weighted) ────────────────────────────────────

def soft_allocation(regime_probs: pd.Series, regime_labels: dict) -> dict:
    """
    Blend allocations using regime probabilities as weights.
    
    Args:
        regime_probs: Series with regime probabilities, e.g. {0: 0.7, 1: 0.3}
        regime_labels: dict mapping regime int → label, e.g. {0: "bull", 1: "bear"}
    
    Returns:
        dict of blended asset weights
    """
    assets = list(REGIME_ALLOCATIONS["bull"].keys())
    blended = {a: 0.0 for a in assets}
    
    for regime_int, prob in regime_probs.items():
        label = regime_labels.get(regime_int, "bull")
        alloc = REGIME_ALLOCATIONS.get(label, REGIME_ALLOCATIONS["bull"])
        for asset, weight in alloc.items():
            blended[asset] += prob * weight
    
    # normalize (should already sum to 1, but float safety)
    total = sum(blended.values())
    return {k: v / total for k, v in blended.items()}


# ── MVO-Based Allocation (Data-Driven) ───────────────────────────────────────

def mvo_allocation(prices: pd.DataFrame, method: str = "max_sharpe") -> dict:
    """
    Mean-Variance Optimization using historical prices.
    
    Args:
        prices: DataFrame of adjusted closing prices
        method: "max_sharpe" or "min_volatility"
    
    Returns:
        dict of cleaned weights
    """
    mu = expected_returns.mean_historical_return(prices)
    S  = risk_models.sample_cov(prices)
    
    ef = EfficientFrontier(mu, S)
    
    if method == "max_sharpe":
        ef.max_sharpe(risk_free_rate=0.05)
    elif method == "min_volatility":
        ef.min_volatility()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    weights = ef.clean_weights()
    performance = ef.portfolio_performance(verbose=True, risk_free_rate=0.05)
    
    return dict(weights), performance


# ── Simple Backtest ───────────────────────────────────────────────────────────

def backtest_regime_strategy(
    prices: pd.DataFrame,
    regime_series: pd.Series,
    regime_labels: dict,
    rebalance_freq: str = "M"
) -> pd.Series:
    """
    Simple vectorized backtest of regime-switching strategy.
    
    Returns:
        portfolio value series (starting at 1.0)
    """
    returns = prices.pct_change().dropna()
    
    # resample regime to rebalance frequency
    regime_resampled = regime_series.resample(rebalance_freq).last().ffill()
    
    portfolio_returns = []
    
    for date, ret_row in returns.iterrows():
        # get most recent regime estimate
        recent_regimes = regime_resampled[regime_resampled.index <= date]
        if recent_regimes.empty:
            continue
        
        current_regime_int = int(recent_regimes.iloc[-1])
        label = regime_labels.get(current_regime_int, "bull")
        alloc = REGIME_ALLOCATIONS[label]
        
        # compute weighted return (ignore cash for now)
        port_ret = sum(
            weight * ret_row.get(asset, 0.0)
            for asset, weight in alloc.items()
            if asset != "cash"
        )
        portfolio_returns.append((date, port_ret))
    
    port_series = pd.Series(
        dict(portfolio_returns),
        name="regime_strategy"
    )
    
    # compound to get portfolio value
    return (1 + port_series).cumprod()


# ── Performance Metrics ───────────────────────────────────────────────────────

def performance_summary(returns: pd.Series) -> dict:
    """Quick performance stats for a daily return series."""
    ann_return = returns.mean() * 252
    ann_vol    = returns.std() * np.sqrt(252)
    sharpe     = ann_return / ann_vol
    
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    calmar = ann_return / abs(max_dd) if max_dd != 0 else np.nan
    
    return {
        "annualized_return": round(ann_return, 4),
        "annualized_vol":    round(ann_vol, 4),
        "sharpe_ratio":      round(sharpe, 4),
        "max_drawdown":      round(max_dd, 4),
        "calmar_ratio":      round(calmar, 4),
    }
