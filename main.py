"""Deterministic, long-only BTC mean reversion for paper trading."""

from collections import deque
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
import makefun_bars


closes = deque(maxlen=60)
peak_equity = 0
entries_halted = False
entry_seq = None


def on_batch(state, batch):
    global peak_equity, entries_halted, entry_seq

    peak_equity = max(peak_equity, state.equity)
    if state.equity * 100 < peak_equity * 94:
        entries_halted = True

    holding = state.positions.get("CBBTC")
    if holding is not None and holding.qty > 0:
        if entry_seq is None:
            entry_seq = state.seq
    else:
        holding = None
        entry_seq = None

    close = state.close("CBBTC")
    if close is None:
        return []
    closes.append(close)
    if state.warming_up or len(closes) < 60:
        return []

    # Compare raw price units exactly; the common hello price scale cancels.
    total = sum(closes)
    if holding is not None:
        if state.seq - entry_seq >= 30 and close * 60 * 10000 > total * 10075:
            return [{"side": "sell", "symbol": "CBBTC",
                     "qty": holding.qty, "max_slippage_bps": 100}]
    elif not entries_halted and state.cash > 0:
        if close * 60 * 10000 < total * 9875:
            return [{"side": "buy", "symbol": "CBBTC",
                     "notional_quote_units": state.cash, "max_slippage_bps": 100}]
    return []


if __name__ == "__main__":
    makefun_bars.run(on_batch)
