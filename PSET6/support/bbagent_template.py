#!/usr/bin/env python3

"""Starter template for balanced-bidding and budget-aware agents."""

from gsp import GSP
from util import argmax_index


class BBAgent:
    """Balanced-bidding agent starter class."""

    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        # Bids are measured in integer cents throughout the simulator.
        return self.value // 2

    def slot_info(self, t, history, reserve):
        """Compute bid ranges for every slot using the previous round's bids.

        Returns ``[(slot_id, min_bid, max_bid), ...]``. ``min_bid`` is the
        bid needed to tie the competing bid for that slot. For the top slot,
        where there is no natural upper endpoint, ``max_bid`` is set to twice
        ``min_bid`` for convenience.
        """
        prev_round = history.round(t - 1)
        other_bids = [
            agent_bid for agent_bid in prev_round.bids if agent_bid[0] != self.id
        ]

        clicks = prev_round.clicks

        def compute(slot):
            min_bid, max_bid = GSP.bid_range_for_slot(
                slot, clicks, reserve, other_bids
            )
            if max_bid is None:
                max_bid = 2 * min_bid
            return slot, min_bid, max_bid

        return [compute(slot) for slot in range(len(clicks))]

    def expected_utils(self, t, history, reserve):
        """Return expected utility from targeting each slot.

        Assume all other agents keep their bids from the previous round.
        """
        # TODO: Fill this in.
        utilities = []
        return utilities

    def target_slot(self, t, history, reserve):
        """Return the bid-range tuple for the utility-maximizing slot."""
        index = argmax_index(self.expected_utils(t, history, reserve))
        return self.slot_info(t, history, reserve)[index]

    def bid(self, t, history, reserve):
        """Return the balanced-bidding bid for period ``t``.

        Given the other agents' previous bids, target the slot maximizing
        ``clicks_s * (value - price_s)``. If the target is not the top slot,
        choose a bid satisfying

            clicks_s * (value - price_s)
                = clicks_{s-1} * (value - bid).

        The returned bid should be an integer number of cents and should not
        exceed the agent's value.
        """
        prev_round = history.round(t - 1)
        slot, min_bid, max_bid = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        bid = 0
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__,
            self.id,
            self.value,
        )
