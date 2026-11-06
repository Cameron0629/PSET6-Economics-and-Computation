#!/usr/bin/env python3

"""Regression tests for the supplied GSP implementation."""

from gsp import GSP


def test_mechanism():
    slot_clicks = [1] * 4
    bids = list(zip(range(1, 6), [10, 12, 18, 14, 20]))

    allocation, payments = GSP.compute(slot_clicks, 0, bids)
    assert allocation == [5, 3, 4, 2]
    assert payments == [18, 14, 12, 10]

    allocation, payments = GSP.compute(slot_clicks, 11, bids)
    assert allocation == [5, 3, 4, 2]
    assert payments == [18, 14, 12, 11]

    allocation, payments = GSP.compute(slot_clicks, 14, bids)
    assert allocation == [5, 3, 4]
    assert payments == [18, 14, 14]

    allocation, payments = GSP.compute(slot_clicks, 15, bids)
    assert allocation == [5, 3]
    assert payments == [18, 15]

    allocation, payments = GSP.compute(slot_clicks, 19, bids)
    assert allocation == [5]
    assert payments == [19]

    allocation, payments = GSP.compute(slot_clicks, 22, bids)
    assert allocation == []
    assert payments == []


def test_bid_ranges():
    slot_clicks = [1] * 4
    bids = list(zip(range(1, 6), [10, 12, 18, 14, 20]))

    def bid_range(slot, reserve):
        return GSP.bid_range_for_slot(slot, slot_clicks, reserve, bids)

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
    print("All GSP tests passed.")


if __name__ == "__main__":
    main()
