# Methodology Notes — Regime Shift

*These are living notes. Expect updates, crossed-out ideas, and the occasional "wait, that was wrong".*

---

## 1. The Problem (In Plain English)

A "regime" in markets just means: what mode is the market in right now?

Some examples of distinct regimes:
- **Risk-on trending**: equities up, vol low, credit spreads tight, momentum works
- **Risk-off crash**: equities down hard, vol spikes, correlations go to 1, everything breaks
- **Choppy/mean-reverting**: no clear trend, range-bound, momentum strategies lose money
- **Stagflationary**: equities struggle, bonds struggle too, commodities outperform

The problem is that you can't *directly observe* which regime you're in. You can only infer it from the data. That's what makes this interesting.

---

## 2. Why Standard Portfolios Fail at Regime Boundaries

Most portfolio construction (MPT, risk parity, etc.) assumes:
- Returns are somewhat stationary
- Correlations between assets are stable
- Volatility is roughly predictable from recent history

None of these hold during regime transitions. In March 2020:
- 30-day realized vol on SPY went from ~12% to ~80%
- Equity-bond correlations flipped positive (both sold off)
- The "safe" 60/40 portfolio dropped ~25% in weeks

The insight: if you can detect the regime change *early enough*, you can shift allocations *before* the full damage hits.

---

## 3. Approaches to Regime Detection

### 3a. Hidden Markov Models (HMM)

The cleanest probabilistic framing. Core idea: there's a hidden state (the regime) that generates the observed returns. We don't see the state directly, but we can estimate it.

**How it works:**
- Fit a Gaussian HMM to return series (or return + vol features)
- The model learns K hidden states and the transition probabilities between them
- At each time step, we get P(state = k) — a probability distribution over regimes

**Pros:** Proper probabilistic framework, handles smooth transitions, well-studied  
**Cons:** Assumes Markov property (next state only depends on current state), sensitive to K choice, can overfit

**Plan:** Start with K=2 (bull/bear), then try K=3 (add sideways/crisis)

### 3b. Structural Break Detection

Different framing: instead of modeling regimes as a generative process, just find the *breakpoints* where the statistical properties of the series change.

Libraries to try:
- `ruptures` — multiple algorithms (Pelt, Binseg, BottomUp), works well on financial series
- Manual CUSUM — good for online detection (detecting breaks in real time)
- Bai-Perron test — more academic, good for validating breaks statistically

**Pros:** Nonparametric, doesn't assume a model, good for validation  
**Cons:** Mostly retrospective (better at finding past breaks than predicting future ones)

### 3c. Macro Indicator Signals (rule-based layer)

Some regime shifts are *telegraphed* by macro data before they show up in price:
- Yield curve inversion → recession risk rising
- Credit spread widening → risk-off regime approaching
- VIX term structure (contango vs backwardation) → vol regime signal
- PMI / ISM data → growth regime signal

Plan: build a composite "regime score" from these, use it as a feature alongside the statistical models.

---

## 4. Portfolio Construction Given Regime

Once we have a regime estimate, the allocation logic changes:

| Regime | Allocation Tilt |
|---|---|
| Bull / Risk-on | Equities overweight, momentum factor, low cash |
| Bear / Risk-off | Bonds, gold, cash, defensive sectors |
| High vol / Crisis | Max diversification, low beta, vol targeting |
| Stagflationary | Commodities, TIPS, real assets |

This isn't a black-box model — it's a rule-based overlay on top of the regime signal. The regime detection does the hard work; the allocation is relatively explicit.

**Alternative:** Use the regime probabilities as soft weights, not hard switches. If P(bear) = 0.6, tilt 60% toward defensive allocation. Smoother, less whipsaw.

---

## 5. Backtesting Plan

Key questions to answer:
1. Does regime detection actually *lead* price moves, or does it lag?
2. How much does transaction cost + slippage eat into the gains from switching?
3. Does the strategy outperform a simple buy-and-hold on a risk-adjusted basis?

Metrics:
- Sharpe ratio, Sortino ratio
- Max drawdown + drawdown duration
- Calmar ratio
- Turnover (to estimate real transaction cost impact)

**Benchmark:** 60/40 SPY/TLT rebalanced monthly

**Lookback:** 2005–2024 (captures GFC, COVID crash, 2022 bear)

---

## 6. Open Questions (Things I'm Still Figuring Out)

- How to handle the *look-ahead bias* problem properly in backtesting
- Whether to use daily or weekly data (weekly = less noise, daily = more responsive)
- How to choose K in HMM without overfitting (BIC? cross-val on held-out periods?)
- Whether the macro signals add genuine predictive power or just add noise
- How to present results honestly — a backtest that looks great is easy to construct, harder to trust

---

## 7. References & Resources

- Ang & Timmermann (2012) — "Regime Changes and Financial Markets" (foundational paper)
- Lopez de Prado (2018) — *Advances in Financial Machine Learning* (chapter on HMM regimes)
- `hmmlearn` docs — https://hmmlearn.readthedocs.io
- `ruptures` docs — https://centre-borelli.github.io/ruptures-docs/
- Quantopian lecture series on regime detection (archived on GitHub)
- Patrick Boyle's YouTube — surprisingly good intuition-building for macro regimes

---

*Last updated: May 2026*
