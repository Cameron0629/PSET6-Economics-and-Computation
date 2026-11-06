#!/usr/bin/env python3
"""Budget-paced GSP bidder; self-contained for tournament submission."""

class Cwjcbudget:
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return min(self.value, max(reserve, self.value * 2 // 3))

    def bid(self, t, history, reserve):
        prev = history.round(t - 1)
        others = sorted(
            (bid for aid, bid in prev.bids if aid != self.id and bid >= reserve),
            reverse=True,
        )
        slots = len(prev.clicks)
        # Choose the slot with greatest one-round surplus, then compute the
        # balanced bid that makes the adjacent slot equally attractive.
        prices = [others[s] if s < len(others) else reserve for s in range(slots)]
        utilities = [clicks * (self.value - price)
                     for clicks, price in zip(prev.clicks, prices)]
        slot = max(range(slots), key=lambda s: utilities[s])
        price = prices[slot]
        if price >= self.value or slot == 0:
            base = self.value
        else:
            raw = self.value - (prev.clicks[slot] / prev.clicks[slot - 1]) * (self.value - price)
            base = max(0, min(self.value, int(raw)))

        spent = history.agents_spent[self.id]
        remaining = max(0, self.budget - spent)
        periods_left = max(1, 48 - t)
        # Hold back a small cushion for later high-traffic periods. If we are
        # ahead of the linear spending path, lower the bid proportionally.
        target_remaining = self.budget * periods_left / 48
        pace_factor = min(1.0, remaining / max(1, target_remaining))
        # Forecast cost for a position from its observed GSP price and clicks.
        # A smaller bid often shifts down a slot, so use a conservative cap.
        cap = int(self.value * min(1.0, 0.55 + 0.45 * pace_factor))
        if remaining == 0:
            return 0
        return max(min(reserve, self.value), min(base, cap, self.value))

    def __repr__(self):
        return f"Cwjcbudget(id={self.id}, value={self.value})"
