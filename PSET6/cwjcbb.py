#!/usr/bin/env python3
"""Balanced bidding for the Cameron and Justin team."""

from gsp import GSP
from util import argmax_index


class Cwjcbb:
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value

    def slot_info(self, t, history, reserve):
        prev = history.round(t - 1)
        others = [(aid, bid) for aid, bid in prev.bids if aid != self.id]
        slots = len(prev.clicks)
        result = []
        for slot in range(slots):
            minimum, maximum = GSP.bid_range_for_slot(
                slot, prev.clicks, reserve, others
            )
            if maximum is None:
                maximum = 2 * minimum
            result.append((slot, minimum, maximum))
        return result

    def expected_utils(self, t, history, reserve):
        """Expected utility by slot under the previous round's bids."""
        prev = history.round(t - 1)
        return [
            clicks * (self.value - minimum)
            for clicks, (_, minimum, _) in zip(prev.clicks, self.slot_info(t, history, reserve))
        ]

    def target_slot(self, t, history, reserve):
        return self.slot_info(t, history, reserve)[
            argmax_index(self.expected_utils(t, history, reserve))
        ]

    def bid(self, t, history, reserve):
        prev = history.round(t - 1)
        slot, price, _ = self.target_slot(t, history, reserve)
        if price >= self.value or slot == 0:
            return self.value
        # Indifference between the target and the slot immediately above it.
        unrounded = self.value - (prev.clicks[slot] / prev.clicks[slot - 1]) * (self.value - price)
        return max(0, min(self.value, int(unrounded)))

    def __repr__(self):
        return f"Cwjcbb(id={self.id}, value={self.value})"
