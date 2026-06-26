# Tennis Predictor: AI tool for predicting tennis tournaments and hypothetical matchups

🎾 Machine learning powered website with access to decades of tennis data that outputs full tournament and head-to-head matchup simulations.

## Overview

*Technologies: Python, XGBoost, scikit-learn, pandas, Next.js, Tailwind CSS*

- Built a **machine learning pipeline** that trains on decades of historical ATP match data to predict match outcomes, with **no data leakage** — every model only sees matches that happened *before* the event it is predicting.
- Engineered **gap-based features** per match (ELO, surface ELO, head-to-head, serve stats, recent form, days rest), all computed in strict chronological order.
- Implemented a **Monte Carlo simulator** that runs 1,000+ tournament simulations to turn individual match predictions into probabilistic bracket outcomes.
- Designed an interactive **Next.js** frontend with three selectable models — **XGBoost, Random Forest, Logistic Regression** — and a fully configurable feature set.

## What It Can Do

Two simulation modes, selectable from the home screen.

---

### 🏆 Tournament Simulation

Pick a Grand Slam and the app simulates the entire draw 1,000+ times, returning the predicted champion, each player's chance of reaching every round, and the most common bracket.

<!-- 📸 Screenshot: tournament result — winner %, win-probability chart, predicted bracket -->

**Choosing features:** before running, pick exactly which features the model trains and tests on — toggle them one by one or select all at once. This makes it easy to see how much each signal (ELO, serve stats, form…) actually moves the prediction.

<!-- 📸 Screenshot: feature panel with ALL features selected -->
<!-- 📸 Screenshot: feature panel with NO features selected -->

### ⚔️ Matchup Simulation

Pit any two players head-to-head for a win probability. **Year sliders** let you choose which season of each player to use, so you can run **Djokovic (2015) vs Sinner (2026)** — and the model correctly uses *only each player's data up to that year*, enabling fair cross-era comparisons.

<!-- 📸 Screenshot: matchup — Djokovic 2015 vs Sinner 2026 with the year sliders -->

---

## Built-in Explanations

Hover the **?** icons throughout the app for plain-English explanations of the trickier parts — for example, why later-round percentages don't add up to 100%, or which first-round players had no prior data and fell back to a coin-flip.

<!-- 📸 Screenshot: an expanded ? tooltip -->
