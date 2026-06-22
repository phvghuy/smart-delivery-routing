import pytest

from smart_delivery_routing.domain.shared import Location
from smart_delivery_routing.infrastructure.haversine import HaversineDistanceCalculator

HANOI = Location(lat=21.0285, lng=105.8542)
HCMC = Location(lat=10.8231, lng=106.6297)
KNOWN_HANOI_HCMC_KM = 1137.0

calculator = HaversineDistanceCalculator()


def test_same_location_is_zero():
    matrix = calculator.compute_matrix([HANOI, HANOI])
    assert matrix[0][0] == 0.0
    assert matrix[1][1] == 0.0
    assert matrix[0][1] == pytest.approx(0.0, abs=1e-6)


def test_known_distance_hanoi_hcmc():
    matrix = calculator.compute_matrix([HANOI, HCMC])
    assert matrix[0][1] == pytest.approx(KNOWN_HANOI_HCMC_KM, rel=0.01)


def test_matrix_is_symmetric():
    locations = [HANOI, HCMC, Location(lat=16.0678, lng=108.2208)]
    matrix = calculator.compute_matrix(locations)
    n = len(locations)
    for i in range(n):
        for j in range(n):
            assert matrix[i][j] == pytest.approx(matrix[j][i], rel=1e-9)


def test_matrix_size():
    locations = [HANOI, HCMC, Location(lat=16.0678, lng=108.2208)]
    matrix = calculator.compute_matrix(locations)
    assert len(matrix) == 3
    assert all(len(row) == 3 for row in matrix)


def test_single_location_returns_1x1_zero():
    matrix = calculator.compute_matrix([HANOI])
    assert matrix == [[0.0]]


def test_triangle_inequality():
    da_nang = Location(lat=16.0678, lng=108.2208)
    matrix = calculator.compute_matrix([HANOI, da_nang, HCMC])
    assert matrix[0][2] <= matrix[0][1] + matrix[1][2] + 1e-6
