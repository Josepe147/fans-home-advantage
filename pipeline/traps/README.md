# Traps: historical diagnostics

These two scripts are kept as the record of two biases found while building the learning model. **Their estimates are not supported results. Do not quote them.** They are not part of the normal run and nothing downstream reads their output.

## What each one shows

**`leak_check2.py`: whole-season leakage.** The first month-by-month estimate of the market's priced home advantage (layer 1 in `model.py`) fitted team strengths on a whole season of prices. Prices after a match react to its result, so a month's estimate partly contains that month's results. This script refits each month using only prices up to the end of that month and compares the revision-weight test both ways. It shows how much of the apparent "the market's revisions carry no information" result came from the leak.

Successor: the Kalman filter in `kf.py`, which only uses earlier prices.

**`learn_checks.py`: fixed-effects bias.** Estimates the weight the market's month-to-month revisions deserve, using the whole-season layer-1 values and grouping by league or league-season. Demeaning within a season uses later values of a regressor that reacts to past results, which biases the estimate downwards. It also runs the same test season by season. (Its docstring mentions a second check, B, that is not implemented.)

Successor: `kappa_clean.py` section F, which uses the filter's real-time values with no fixed effects (0.97, se 0.33).

The numbers these scripts print reflect those biases. They were not altered or invented. They were what the flawed methods produced, which is why the methods were replaced.

## Running them

Both read `work/model.pkl` and `work/H.pkl` with relative paths, so they must be run from the `pipeline/` folder after `model_data.py` and `model.py`:

```
cd pipeline
python traps/leak_check2.py   # also writes work/H_past.pkl
python traps/learn_checks.py
```

Their earlier console output is in `pipeline/work/leak_check2.txt` and `learn_checks.txt` (not in the repository).
