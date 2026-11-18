# BTC race — November 18, 2026

Offline, deterministic, long-only cbBTC/USDC paper trading entry for
`btc-race-24h-20261118-1444`. Python standard library only; MIT licensed.
No live orders, network calls, leverage, paid services, or wall-clock inputs.

## Strategy

The sole strategy change from the prior bot is widening the entry discount
from 0.75% to 1.25%. At each completed bar, include its close in a rolling
60-bar arithmetic mean. Once 60 closes exist, buy with all available cash
when flat and `close < mean * 0.9875`. Sell the full position when
`close > mean * 1.0075` and at least 30 sequence steps have elapsed since
the first batch reporting the filled holding. Comparisons use integers.
Every order has `max_slippage_bps = 100`. Orders execute at the next open
under the replay harness. No orders during warm-up.

New entries halt permanently for the run if marked equity falls strictly
below 94% of its running peak. This is an entry halt, not a liquidation
stop, and does not cap losses on an existing holding. Existing exit logic
continues. The harness liquidates any final position.

## Validation and limitations

The new dev window declined 2.800343%; both halves declined. A small sweep
compared the original rule with entry discounts of 1.00%, 1.25%, and 1.50%,
30/120-bar means, a 240-bar trend filter, and smaller exit premiums.
The chosen single-parameter change meets the full-window dev gate, but
**all dev profit comes from one first-half round trip**. The second half
and the old window each have zero trades and zero PnL. This is a tiny
in-sample population, not evidence of a statistically established edge.
No claim of profitability on future data is made.

Measured with the supplied `local_grade.py` integer fill engine:

| Window | Net PnL (USDC) | Fills | Max drawdown magnitude |
| --- | ---: | ---: | ---: |
| New full dev | +10.447012 | 2 | 1.496356% |
| First 720 bars, fresh start | +10.447012 | 2 | 1.496356% |
| Last 720 bars, fresh start | 0 | 0 | 0% |
| Prior dev, sanity check | 0 | 0 | 0% |

Two identical-input runs produced byte-identical action logs. The tested
1.50% entry discount produced the same fills. Doubling both fee and
slippage rates in the replay engine left +9.236052 USDC. These checks are
sensitivity tests on the published dev data, not out-of-sample validation.
The two fills are one buy and one sell, not two round trips.

## Run and grade

The runtime command is `python3 -P -s /bot/main.py`, with
`PYTHONHASHSEED=0`. It consumes agent-fun/bars-replay/v1 NDJSON on stdin and
writes one reply per batch on stdout. The SDK in `vendor/makefun_bars.py`
is a byte-for-byte copy made with `cp` from this competition kit.

```sh
python3 /home/hatch/workspace/makefun/btc-race-24h-20261117-0603-analysis/local_grade.py \
  --bot . --runtime python \
  --bars-file /home/hatch/workspace/makefun/btc-race-24h-20261118-1444-kit/btc-race-24h-20261118-1444-kit/dataset/bars/CBBTC.ndjson.gz
```

Append `--half first` or `--half second` to test fresh-start halves.
The external grader-sim is a legacy file-output smoke test that supplies
no replay messages; its outcome is recorded in `reports/` separately.

Packaging is for review only. No submission is authorized or performed.
