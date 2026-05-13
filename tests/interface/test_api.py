import io
import csv
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

from smart_delivery_routing.interface.api import app

client = TestClient(app)

VALID_PAYLOAD = {
    "orders": [
        {"order_id": "ORD-001", "lat": 10.78, "lng": 106.70, "weight": 50.0, "volume": 0.3},
        {"order_id": "ORD-002", "lat": 10.80, "lng": 106.72, "weight": 80.0, "volume": 0.4},
    ],
    "vehicles": [
        {"vehicle_id": "VEH-001", "max_weight": 500.0, "max_volume": 2.0, "start_lat": 10.98, "start_lng": 106.65},
    ],
}


def _make_csv(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode()


# --- POST /optimize ---

def test_optimize_returns_200():
    response = client.post("/optimize", json=VALID_PAYLOAD)
    assert response.status_code == 200


def test_optimize_response_has_results():
    response = client.post("/optimize", json=VALID_PAYLOAD)
    body = response.json()
    assert "results" in body
    assert len(body["results"]) > 0
    for result in body["results"]:
        assert "solver" in result
        assert "routes" in result
        assert "kpi" in result
        assert "unassigned_orders" in result


def test_optimize_all_solvers_present():
    response = client.post("/optimize", json=VALID_PAYLOAD)
    solver_names = {r["solver"] for r in response.json()["results"]}
    assert "nearest_neighbor" in solver_names
    assert "ortools" in solver_names


def test_optimize_all_orders_assigned():
    response = client.post("/optimize", json=VALID_PAYLOAD)
    for result in response.json()["results"]:
        assigned = {s["order_id"] for r in result["routes"] for s in r["stops"]}
        assert assigned == {"ORD-001", "ORD-002"}, f"solver={result['solver']}"


def test_optimize_kpi_fields():
    response = client.post("/optimize", json=VALID_PAYLOAD)
    for result in response.json()["results"]:
        kpi = result["kpi"]
        assert "total_distance_km" in kpi
        assert "vehicles_used" in kpi
        assert "average_fill_rate_weight" in kpi
        assert "average_fill_rate_volume" in kpi


def test_optimize_invalid_lat_returns_422():
    payload = {**VALID_PAYLOAD, "orders": [{**VALID_PAYLOAD["orders"][0], "lat": 999.0}]}
    response = client.post("/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_negative_weight_returns_422():
    payload = {**VALID_PAYLOAD, "orders": [{**VALID_PAYLOAD["orders"][0], "weight": -1.0}]}
    response = client.post("/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_empty_orders_returns_422():
    payload = {**VALID_PAYLOAD, "orders": []}
    response = client.post("/optimize", json=payload)
    assert response.status_code == 422


def test_optimize_empty_vehicles_returns_422():
    payload = {**VALID_PAYLOAD, "vehicles": []}
    response = client.post("/optimize", json=payload)
    assert response.status_code == 422


# --- POST /optimize/upload ---

def test_optimize_upload_returns_200():
    orders_csv = _make_csv([
        {"order_id": "ORD-001", "lat": 10.78, "lng": 106.70, "weight": 50.0, "volume": 0.3},
    ])
    vehicles_csv = _make_csv([
        {"vehicle_id": "VEH-001", "max_weight": 500.0, "max_volume": 2.0, "start_lat": 10.98, "start_lng": 106.65},
    ])
    response = client.post(
        "/optimize/upload",
        files={
            "orders_file": ("orders.csv", orders_csv, "text/csv"),
            "vehicles_file": ("vehicles.csv", vehicles_csv, "text/csv"),
        },
    )
    assert response.status_code == 200


def test_optimize_upload_missing_column_returns_400():
    bad_csv = _make_csv([{"order_id": "ORD-001", "lat": 10.78}])  # missing lng, weight, volume
    vehicles_csv = _make_csv([
        {"vehicle_id": "VEH-001", "max_weight": 500.0, "max_volume": 2.0, "start_lat": 10.98, "start_lng": 106.65},
    ])
    response = client.post(
        "/optimize/upload",
        files={
            "orders_file": ("orders.csv", bad_csv, "text/csv"),
            "vehicles_file": ("vehicles.csv", vehicles_csv, "text/csv"),
        },
    )
    assert response.status_code == 400