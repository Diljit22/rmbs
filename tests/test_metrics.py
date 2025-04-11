import pytest
import numpy as np
from src.metrics import calculate_yield, calculate_wal


def test_calculate_yield():
    # Suppose we invest 100 at time 0
    # We get 10 for 10 months
    cfs = np.array([10] * 10)
    price = 100.0
    y = calculate_yield(cfs, price)
    assert 0 <= y < 1.0  # IRR less than 100%


def test_calculate_wal():
    cfs = np.array([10, 10, 10])
    wal = calculate_wal(cfs)
    # Weighted sum = (1/12)*10 + (2/12)*10 + (3/12)*10 = (6/12)*10 = 5
    # total CF = 30
    # WAL = 5 / 30 = 0.1666.. years
    assert abs(wal - 0.1667) < 0.01
