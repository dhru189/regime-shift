# Git Commit History Guide

A reference for writing commits that tell a coherent story.
(Copy these as starting points — modify to reflect what you actually did)

---

## Suggested Initial Commits

```
git init
git add README.md
git commit -m "initial commit — project outline and structure"

git add requirements.txt .gitignore
git commit -m "add dependencies and gitignore"

git add src/data/fetch.py
git commit -m "data pipeline: yfinance + FRED macro indicators"

git add notebooks/01_data_collection.ipynb
git commit -m "notebook 01: data collection, initial exploration"

git add src/analysis/regime_detection.py
git commit -m "regime detection: HMM wrapper + structural break utils"

git add reports/methodology.md
git commit -m "methodology notes: HMM approach, macro signals, backtest plan"
```

---

## Commit Message Style

Keep it lowercase, direct, no punctuation at end.

Good:
- `fix off-by-one in rolling vol calculation`
- `add yield curve inversion signal to feature set`
- `experiment: try k=3 regimes, results mixed`
- `backtest: 2005-2024 results, sharpe 0.91 vs 0.68 benchmark`
- `rough draft: portfolio allocation logic per regime`

Avoid:
- `Update files`
- `Fixed bug`
- `WIP`

---

## Branch Strategy (optional but good practice)

```bash
git checkout -b feature/hmm-model      # main modeling work
git checkout -b feature/backtest       # backtesting logic
git checkout -b feature/viz            # charts and reporting
```

Merge into main when each piece is working.
