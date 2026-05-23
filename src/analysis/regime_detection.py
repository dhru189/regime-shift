"""
src/analysis/regime_detection.py

Regime detection using Hidden Markov Models and structural break tests.
"""

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
import ruptures as rpt
from typing import Optional
import warnings
warnings.filterwarnings("ignore")


# ── Feature Engineering ───────────────────────────────────────────────────────

def build_features(prices: pd.Series, window: int = 21) -> pd.DataFrame:
    """
    Build features for regime detection from a price series.
    
    Features:
    - daily log returns
    - rolling realized volatility (21d)
    - rolling return z-score (normalized recent return)
    """
    log_ret = np.log(prices / prices.shift(1)).dropna()
    
    features = pd.DataFrame(index=log_ret.index)
    features["returns"] = log_ret
    features["realized_vol"] = log_ret.rolling(window).std() * np.sqrt(252)
    features["return_zscore"] = (
        log_ret.rolling(window).mean() / log_ret.rolling(window).std()
    )
    
    return features.dropna()


# ── HMM Regime Detection ──────────────────────────────────────────────────────

class RegimeHMM:
    """
    Gaussian HMM wrapper for market regime detection.
    
    Usage:
        model = RegimeHMM(n_regimes=2)
        model.fit(features_df)
        regimes = model.predict(features_df)
        probs = model.predict_proba(features_df)
    """
    
    def __init__(self, n_regimes: int = 2, n_iter: int = 100, random_state: int = 42):
        self.n_regimes = n_regimes
        self.model = GaussianHMM(
            n_components=n_regimes,
            covariance_type="full",
            n_iter=n_iter,
            random_state=random_state
        )
        self._fitted = False
    
    def fit(self, features: pd.DataFrame) -> "RegimeHMM":
        X = features.values
        self.model.fit(X)
        self._fitted = True
        print(f"HMM fitted: {self.n_regimes} regimes, "
              f"score={self.model.score(X):.2f}")
        return self
    
    def predict(self, features: pd.DataFrame) -> pd.Series:
        """Return most likely regime at each timestep."""
        assert self._fitted, "Call .fit() first"
        states = self.model.predict(features.values)
        return pd.Series(states, index=features.index, name="regime")
    
    def predict_proba(self, features: pd.DataFrame) -> pd.DataFrame:
        """Return posterior probability of each regime at each timestep."""
        assert self._fitted, "Call .fit() first"
        probs = self.model.predict_proba(features.values)
        cols = [f"p_regime_{i}" for i in range(self.n_regimes)]
        return pd.DataFrame(probs, index=features.index, columns=cols)
    
    def regime_stats(self, features: pd.DataFrame, returns: pd.Series) -> pd.DataFrame:
        """Summary stats per regime — useful for labeling bull vs bear."""
        regimes = self.predict(features)
        df = returns.to_frame("daily_return").join(regimes)
        
        stats = df.groupby("regime")["daily_return"].agg(
            mean_return="mean",
            annualized_return=lambda x: x.mean() * 252,
            annualized_vol=lambda x: x.std() * np.sqrt(252),
            sharpe=lambda x: (x.mean() / x.std()) * np.sqrt(252),
            count="count"
        )
        return stats.round(4)


# ── Structural Break Detection ────────────────────────────────────────────────

def find_breakpoints(returns: pd.Series, model: str = "rbf", n_breaks: int = 5) -> list:
    """
    Use the PELT algorithm to detect structural breakpoints in a return series.
    
    Args:
        returns: daily return series
        model: ruptures model ("rbf", "l2", "l1")
        n_breaks: expected number of breakpoints
    
    Returns:
        list of integer indices where breaks occur
    """
    signal = returns.values.reshape(-1, 1)
    algo = rpt.Pelt(model=model).fit(signal)
    
    # pen parameter controls sensitivity — higher = fewer breaks
    # rule of thumb: pen = log(n) * sigma^2
    n = len(signal)
    sigma2 = np.var(signal)
    pen = np.log(n) * sigma2 * 3   # multiply by 3 for less sensitivity
    
    breakpoints = algo.predict(pen=pen)
    
    # convert to timestamps
    dates = returns.index
    break_dates = [dates[bp - 1] for bp in breakpoints if bp < len(dates)]
    
    print(f"Found {len(break_dates)} structural breaks")
    return break_dates


# ── Quick sanity test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # minimal smoke test with random data
    np.random.seed(0)
    idx = pd.date_range("2010-01-01", periods=500, freq="B")
    fake_prices = pd.Series(100 * np.exp(np.random.randn(500).cumsum() * 0.01), index=idx)
    
    features = build_features(fake_prices)
    print(features.tail())
    
    model = RegimeHMM(n_regimes=2)
    model.fit(features)
    
    regimes = model.predict(features)
    probs = model.predict_proba(features)
    print("\nRegime distribution:")
    print(regimes.value_counts())
    
    print("\nRegime stats:")
    returns = np.log(fake_prices / fake_prices.shift(1)).dropna()
    print(model.regime_stats(features, returns.loc[features.index]))
