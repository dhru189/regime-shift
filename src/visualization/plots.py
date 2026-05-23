"""
src/visualization/plots.py

Reusable plotting functions for regime analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# consistent style
plt.rcParams.update({
    "figure.facecolor": "#0f0f0f",
    "axes.facecolor":   "#1a1a1a",
    "axes.edgecolor":   "#444",
    "axes.labelcolor":  "#ccc",
    "xtick.color":      "#888",
    "ytick.color":      "#888",
    "text.color":       "#eee",
    "grid.color":       "#2a2a2a",
    "grid.linestyle":   "--",
    "font.family":      "monospace",
})

REGIME_COLORS = ["#00d4aa", "#ff6b6b", "#ffd166", "#a8dadc"]


def plot_regime_overlay(
    prices: pd.Series,
    regimes: pd.Series,
    title: str = "Price with Regime Overlay",
    save_path: str = None
):
    """
    Plot price series with colored background showing detected regimes.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    gridspec_kw={"height_ratios": [3, 1]},
                                    sharex=True)
    
    # price
    ax1.plot(prices.index, prices.values, color="#00d4aa", linewidth=1.2, alpha=0.9)
    ax1.set_ylabel("Price")
    ax1.set_title(title, fontsize=13, pad=12)
    
    # regime shading
    unique_regimes = sorted(regimes.unique())
    for regime_id in unique_regimes:
        mask = regimes == regime_id
        ax1.fill_between(
            regimes.index, ax1.get_ylim()[0], ax1.get_ylim()[1],
            where=mask, alpha=0.15,
            color=REGIME_COLORS[regime_id % len(REGIME_COLORS)],
            label=f"Regime {regime_id}"
        )
    
    ax1.legend(loc="upper left", framealpha=0.3)
    
    # regime bar
    ax2.scatter(regimes.index, regimes.values,
                c=[REGIME_COLORS[r % len(REGIME_COLORS)] for r in regimes],
                s=1.5, alpha=0.8)
    ax2.set_ylabel("Regime")
    ax2.set_xlabel("Date")
    ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved → {save_path}")
    plt.show()


def plot_regime_probs(
    probs: pd.DataFrame,
    prices: pd.Series,
    save_path: str = None
):
    """
    Plot regime posterior probabilities alongside price.
    """
    n_regimes = probs.shape[1]
    fig, axes = plt.subplots(n_regimes + 1, 1, figsize=(14, 4 + 2 * n_regimes),
                              sharex=True)
    
    axes[0].plot(prices.index, prices.values, color="#00d4aa", linewidth=1)
    axes[0].set_ylabel("Price")
    axes[0].set_title("Regime Posterior Probabilities", fontsize=13)
    
    for i, col in enumerate(probs.columns):
        axes[i + 1].fill_between(
            probs.index, 0, probs[col],
            color=REGIME_COLORS[i % len(REGIME_COLORS)],
            alpha=0.7
        )
        axes[i + 1].set_ylim(0, 1)
        axes[i + 1].set_ylabel(f"P(R={i})", fontsize=9)
    
    axes[-1].set_xlabel("Date")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_drawdown(portfolio_value: pd.Series, benchmark: pd.Series = None,
                  save_path: str = None):
    """
    Plot portfolio drawdown chart with optional benchmark comparison.
    """
    def _drawdown(series):
        rolling_max = series.cummax()
        return (series - rolling_max) / rolling_max * 100

    fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
    
    # cumulative value
    axes[0].plot(portfolio_value.index, portfolio_value.values,
                 color="#00d4aa", linewidth=1.5, label="Strategy")
    if benchmark is not None:
        bench_norm = benchmark / benchmark.iloc[0]
        axes[0].plot(bench_norm.index, bench_norm.values,
                     color="#888", linewidth=1, linestyle="--", label="Benchmark (60/40)", alpha=0.7)
    axes[0].set_ylabel("Portfolio Value")
    axes[0].set_title("Strategy Performance", fontsize=13)
    axes[0].legend(framealpha=0.3)
    
    # drawdown
    dd = _drawdown(portfolio_value)
    axes[1].fill_between(dd.index, dd.values, 0, color="#ff6b6b", alpha=0.6)
    axes[1].plot(dd.index, dd.values, color="#ff6b6b", linewidth=0.8)
    axes[1].set_ylabel("Drawdown (%)")
    axes[1].set_xlabel("Date")
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
