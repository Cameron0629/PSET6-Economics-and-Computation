#!/usr/bin/env python3

"""Regression tests for simulator infrastructure supplied to students."""

from __future__ import annotations

from types import SimpleNamespace

import auction


class TrackingAgent:
    observations = {}

    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value

    def bid(self, t, history, reserve):
        type(self).observations[(self.id, t)] = history.agents_spent[self.id]
        return self.value


class PassiveAgent:
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value

    def bid(self, t, history, reserve):
        return self.value


def make_config(agent_class, mechanism="gsp", num_rounds=2):
    name = agent_class.__name__
    return SimpleNamespace(
        mechanism=mechanism,
        reserve=0,
        budget=100_000,
        num_rounds=num_rounds,
        dropoff=0.75,
        agent_class_names=[name, name],
        agent_classes={name: agent_class},
        agent_values=[100, 50],
    )


def test_agents_see_spending_through_previous_round():
    TrackingAgent.observations = {}
    history = auction.sim(make_config(TrackingAgent, num_rounds=2))

    # In round 0, the high-value agent wins 80 clicks and pays 50 cents/click.
    assert TrackingAgent.observations[(0, 1)] == 4_000
    assert TrackingAgent.observations[(1, 1)] == 0
    assert history.agents_spent[0] >= 4_000


def test_switch_mechanism_with_odd_number_of_rounds():
    class FakeGSP:
        calls = 0

        @staticmethod
        def compute(slot_clicks, reserve, bids):
            FakeGSP.calls += 1
            return [], []

    class FakeVCG:
        calls = 0

        @staticmethod
        def compute(slot_clicks, reserve, bids):
            FakeVCG.calls += 1
            return [], []

    original_gsp, original_vcg = auction.GSP, auction.VCG
    try:
        auction.GSP, auction.VCG = FakeGSP, FakeVCG
        auction.sim(make_config(PassiveAgent, mechanism="switch", num_rounds=3))
    finally:
        auction.GSP, auction.VCG = original_gsp, original_vcg

    assert FakeGSP.calls == 1
    assert FakeVCG.calls == 2


def main():
    test_agents_see_spending_through_previous_round()
    test_switch_mechanism_with_odd_number_of_rounds()
    print("All simulator infrastructure tests passed.")


if __name__ == "__main__":
    main()
