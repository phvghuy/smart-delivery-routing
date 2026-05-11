"""Generate sample warehouses, orders, and vehicles CSV for TP.HCM area."""

import random
import pandas as pd
from pathlib import Path

SEED = 42
random.seed(SEED)

# TP.HCM bounding box
LAT_MIN, LAT_MAX = 10.65, 10.90
LNG_MIN, LNG_MAX = 106.60, 106.90

OUTPUT_DIR = Path(__file__).parent

WAREHOUSES = [
    ("WH-001", "Kho Bình Dương",  10.9800, 106.6500),
    ("WH-002", "Kho Thủ Đức",     10.8500, 106.7700),
    ("WH-003", "Kho Bình Chánh",  10.6800, 106.6100),
]

VEHICLE_CONFIGS = [
    ("VEH-001", "WH-001",  800, 2.0),
    ("VEH-002", "WH-001",  800, 2.0),
    ("VEH-003", "WH-001", 1200, 3.5),
    ("VEH-004", "WH-002", 1200, 3.5),
    ("VEH-005", "WH-002", 2000, 5.0),
    ("VEH-006", "WH-003", 2000, 5.0),
    ("VEH-007", "WH-003",  500, 1.5),
]


def generate_warehouses() -> pd.DataFrame:
    return pd.DataFrame([
        {"warehouse_id": wid, "name": name, "lat": lat, "lng": lng}
        for wid, name, lat, lng in WAREHOUSES
    ])


def generate_orders(n: int = 150) -> pd.DataFrame:
    warehouse_ids = [wid for wid, *_ in WAREHOUSES]
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "order_id":     f"ORD-{i:04d}",
            "warehouse_id": random.choice(warehouse_ids),
            "lat":          round(random.uniform(LAT_MIN, LAT_MAX), 6),
            "lng":          round(random.uniform(LNG_MIN, LNG_MAX), 6),
            "weight":       round(random.uniform(5.0, 150.0), 2),
            "volume":       round(random.uniform(0.01, 0.80), 3),
        })
    return pd.DataFrame(rows)


def generate_vehicles() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "vehicle_id":   vid,
            "warehouse_id": wid,
            "max_weight":   mw,
            "max_volume":   mv,
        }
        for vid, wid, mw, mv in VEHICLE_CONFIGS
    ])


if __name__ == "__main__":
    warehouses_df = generate_warehouses()
    orders_df     = generate_orders(150)
    vehicles_df   = generate_vehicles()

    warehouses_path = OUTPUT_DIR / "warehouses.csv"
    orders_path     = OUTPUT_DIR / "orders.csv"
    vehicles_path   = OUTPUT_DIR / "vehicles.csv"

    warehouses_df.to_csv(warehouses_path, index=False)
    orders_df.to_csv(orders_path, index=False)
    vehicles_df.to_csv(vehicles_path, index=False)

    print(f"Generated {len(warehouses_df)} warehouses → {warehouses_path}")
    print(f"Generated {len(orders_df)} orders      → {orders_path}")
    print(f"Generated {len(vehicles_df)} vehicles    → {vehicles_path}")

    print("\nWarehouses:")
    print(warehouses_df.to_string(index=False))

    print("\nOrders per warehouse:")
    print(orders_df.groupby("warehouse_id").size().to_string())

    print("\nVehicles per warehouse:")
    print(vehicles_df.groupby("warehouse_id").size().to_string())

    print(f"\nOrders weight: {orders_df['weight'].min():.1f} – {orders_df['weight'].max():.1f} kg")
    print(f"Orders volume: {orders_df['volume'].min():.3f} – {orders_df['volume'].max():.3f} m³")