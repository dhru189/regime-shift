# Regime Shift — Capital Markets Project

> FEC IIT Guwahati · DIY Projects 2026 · Capital Domain

---

## What is this?

Markets aren't static. They cycle through different *regimes* — trending, mean-reverting, high-vol, low-vol — and a strategy that works brilliantly in one regime can bleed out in another.

This project tries to answer a deceptively simple question: **can we detect when a regime shift is happening in real time, and adjust a portfolio accordingly — before the damage is done?**

---

## The Core Idea

Most retail and even institutional portfolios are built assuming relatively stable market conditions. When the environment changes (think: 2008, March 2020, 2022 rate hike cycle), these portfolios get caught flat-footed.

The hypothesis here is that by combining:
- **Statistical regime detection** (Hidden Markov Models, structural break tests)
- **Macro indicator signals** (yield curve, volatility surface, credit spreads)
- **Portfolio construction logic** (factor tilts, dynamic allocation)

...we can build a system that *adapts* rather than just *reacts*.

---

## Project Structure

```
regime-shift/
│
├── data/
│   ├── raw/            # untouched downloads — never edit these
│   └── processed/      # cleaned, feature-engineered datasets
│
├── notebooks/          # exploration & analysis (numbered sequentially)
│   ├── 01_data_collection.ipynb
│   ├── 02_eda_and_regime_labeling.ipynb
│   ├── 03_model_experiments.ipynb
│   └── 04_portfolio_backtest.ipynb
│
├── src/
│   ├── data/           # data fetching & cleaning scripts
│   ├── analysis/       # regime detection models
│   ├── visualization/  # reusable plotting functions
│   └── utils/          # helpers, config, constants
│
├── reports/
│   ├── figures/        # saved plots for writeup
│   └── methodology.md  # written explanation of approach
│
├── tests/              # basic sanity checks
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Tech Stack

| Purpose | Library |
|---|---|
| Data fetching | `yfinance`, `pandas-datareader` |
| Analysis | `pandas`, `numpy`, `scipy` |
| Regime detection | `hmmlearn`, `ruptures` |
| Portfolio math | `PyPortfolioOpt` |
| Visualization | `matplotlib`, `seaborn`, `plotly` |
| Backtesting | `vectorbt` |

---

## Getting Started

```bash
# clone the repo
git clone https://github.com/YOUR_USERNAME/regime-shift.git
cd regime-shift

# set up environment
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# open notebooks
jupyter lab
```

Start with `notebooks/01_data_collection.ipynb` — it walks through pulling historical price data and macro indicators.

---

## Current Progress

- [x] Project setup & repo structure
- [x] Data pipeline (price + macro data)
- [ ] EDA & visual regime labeling
- [ ] HMM regime detection model
- [ ] Structural break detection (CUSUM / Bai-Perron)
- [ ] Dynamic portfolio construction
- [ ] Backtesting & performance attribution
- [ ] Final report + pitch deck

---

## Methodology

See [`reports/methodology.md`](reports/methodology.md) for the full written breakdown — intuition, math, and decisions made along the way.

---

## Mentorship

Built under the FEC IIT Guwahati DIY Projects 2026 program. Huge thanks to the mentors for the structured framework — having someone to gut-check ideas with makes a real difference.

---

## License

MIT — use it, fork it, build on it.
