#!/usr/bin/env python3

"""Read-only simulation history exposed to bidding agents."""

from __future__ import annotations

import copy
from typing import Any


class History:
    class RoundHistory:
        """A defensive copy of the data from one completed round."""

        def __init__(
            self,
            bids: Any,
            occupants: Any,
            clicks: Any,
            per_click_payments: Any,
            slot_payments: Any,
        ) -> None:
            self.bids = copy.deepcopy(bids)
            self.occupants = copy.deepcopy(occupants)
            self.clicks = copy.deepcopy(clicks)
            self.per_click_payments = copy.deepcopy(per_click_payments)
            self.slot_payments = copy.deepcopy(slot_payments)

    def __init__(
        self,
        bids: dict,
        occupants: dict,
        clicks: dict,
        per_click_payments: dict,
        slot_payments: dict,
        n_agents: int = 3,
    ) -> None:
        self._bids = bids
        self._occupants = occupants
        self._clicks = clicks
        self._per_click_payments = per_click_payments
        self._slot_payments = slot_payments

        # Cumulative spending through the most recently completed round.
        self.agents_spent = [0 for _ in range(n_agents)]

    def round(self, t: int) -> "History.RoundHistory":
        """Return a defensive copy of round ``t``."""
        return History.RoundHistory(
            self._bids[t],
            self._occupants[t],
            self._clicks[t],
            self._per_click_payments[t],
            self._slot_payments[t],
        )

    def last_round(self) -> int:
        """Return the index of the latest completed round, or -1 if none exist."""
        return len(self._bids) - 1

    def num_rounds(self) -> int:
        """Return the number of completed rounds."""
        return len(self._bids)

    def set_agent_spent(self, agent_id: int, spent: float) -> None:
        """Update an agent's cumulative spending visible to future bids."""
        self.agents_spent[agent_id] = spent
