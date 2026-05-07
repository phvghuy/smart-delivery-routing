"""Generate sample orders and vehicles CSV for TP.HCM area."""

import random
import pandas as pd
from pathlib import Path

SEED = 42
random.seed(SEED)

# TP.HCM bounding box
LAT_MIN, LAT_MAX = 10.65, 10.90
LNG_MIN, LNG_MAX = 106.60, 106.90

# Depot: kho hàng tại Bình Dương (cửa ngõ vào TP.HCM)
DEPOT_LAT = 10.9800
DEPOT_LNG = 106.6500

OUTPUT_DIR = Path(__file__).parent


def generate_orders(n: int = 150) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "order_id": f"ORD-{i:04d}",
            "lat": round(random.uniform(LAT_MIN, LAT_MAX), 6),
            "lng": round(random.uniform(LNG_MIN, LNG_MAX), 6),
            "weight": round(random.uniform(5.0, 150.0), 2),   # kg
            "volume": round(random.uniform(0.01, 0.80), 3),   # m³
        })
    return pd.DataFrame(rows)


def generate_vehicles(n: int = 7) -> pd.DataFrame:
    configs = [
        ("VEH-001", 800,  2.0),
        ("VEH-002", 800,  2.0),
        ("VEH-003", 1200, 3.5),
        ("VEH-004", 1200, 3.5),
        ("VEH-005", 2000, 5.0),
        ("VEH-006", 2000, 5.0),
        ("VEH-007", 500,  1.5),
    ]
    rows = [
        {
            "vehicle_id": vid,
            "max_weight": mw,
            "max_volume": mv,
            "start_lat": DEPOT_LAT,
            "start_lng": DEPOT_LNG,
        }
        for vid, mw, mv in configs[:n]
    ]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    orders_df = generate_orders(150)
    vehicles_df = generate_vehicles(7)

    orders_path = OUTPUT_DIR / "orders.csv"
    vehicles_path = OUTPUT_DIR / "vehicles.csv"

    orders_df.to_csv(orders_path, index=False)
    vehicles_df.to_csv(vehicles_path, index=False)

    print(f"Generated {len(orders_df)} orders → {orders_path}")
    print(f"Generated {len(vehicles_df)} vehicles → {vehicles_path}")
    print(f"\nOrders summary:")
    print(f"  weight: {orders_df['weight'].min():.1f} – {orders_df['weight'].max():.1f} kg")
    print(f"  volume: {orders_df['volume'].min():.3f} – {orders_df['volume'].max():.3f} m³")
    print(f"\nVehicles:")
    print(vehicles_df.to_string(index=False))