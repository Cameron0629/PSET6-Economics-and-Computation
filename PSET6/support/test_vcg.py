#!/usr/bin/env python3

"""Tests for the VCG payment-rule TODO in vcg.py."""

import math

from vcg import VCG


def assert_payments_close(actual, expected):
    assert len(actual) == len(expected)
    for observed, target in zip(actual, expected):
        assert math.isclose(observed, target, rel_tol=1e-12, abs_tol=1e-12), (
            f"Expected payment {target}, got {observed}."
        )


def test_mechanism():
    slot_clicks = [4, 3, 2, 1]
    bids = list(zip(range(1, 6), [10, 12, 18, 14, 20]))

    def norm(totals):
        return [total / clicks for total, clicks in zip(totals, slot_clicks)]

    allocation, payments = VCG.compute(slot_clicks, 0, bids)
    assert allocation == [5, 3, 4, 2]
    assert_payments_close(payments, norm([54, 36, 22, 10]))

    allocation, payments = VCG.compute(slot_clicks, 11, bids)
    assert allocation == [5, 3, 4, 2]
    assert_payments_close(payments, norm([55, 37, 23, 11]))

    allocation, payments = VCG.compute(slot_clicks, 14, bids)
    assert allocation == [5, 3, 4]
    assert_payments_close(payments, norm([60, 42, 28]))

    allocation, payments = VCG.compute(slot_clicks, 15, bids)
    assert allocation == [5, 3]
    assert_payments_close(payments, norm([63, 45]))

    allocation, payments = VCG.compute(slot_clicks, 19, bids)
    assert allocation == [5]
    assert_payments_close(payments, norm([76]))

    allocation, payments = VCG.compute(slot_clicks, 22, bids)
    assert allocation == []
    assert payments == []


def test_bid_ranges():
    slot_clicks = [4, 3, 2, 1]
    bids = list(zip(range(1, 6), [10, 12, 18, 14, 20]))

    def bid_range(slot, reserve):
        return VCG.bid_range_for_slot(slot, slot_clicks, reserve, bids)

    assert bid_range(0, 0) == (20, None)
    assert bid_range(1, 0) == (18, 20)
    assert bid_range(2, 0) == (14, 18)
    assert bid_range(3, 0) == (12, 14)
    assert bid_range(4, 0) == (10, 12)
    assert bid_range(7, 0) == (0, 10)

    assert bid_range(0, 15) == (20, None)
    assert bid_range(1, 15) == (18, 20)
    assert bid_range(2, 15) == (15, 18)
    assert bid_range(3, 15) == (15, 18)
    assert bid_range(7, 15) == (15, 18)

    assert bid_range(0, 22) == (22, None)
    assert bid_range(1, 22) == (22, 22)
    assert bid_range(2, 22) == (22, 22)


def main():
    test_mechanism()
    test_bid_ranges()
    print("All VCG tests passed.")


if __name__ == "__main__":
    main()
