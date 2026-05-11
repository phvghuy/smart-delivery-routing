import io
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from smart_delivery_routing.domain.models import Location, Order, Warehouse, Vehicle


@dataclass(frozen=True)
class LoadError(Exception):
    source: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.source}] {self.reason}"


_ORDER_COLUMNS = {"order_id", "warehouse_id", "lat", "lng", "weight", "volume"}
_VEHICLE_COLUMNS = {"vehicle_id", "warehouse_id", "max_weight", "max_volume"}
_WAREHOUSE_COLUMNS = {"warehouse_id", "name", "lat", "lng"}


def load_orders(path: str | Path) -> list[Order]:
    df = _read_csv(path, _ORDER_COLUMNS)
    return orders_from_dataframe(df)


def load_vehicles(path: str | Path) -> list[Vehicle]:
    df = _read_csv(path, _VEHICLE_COLUMNS)
    return vehicles_from_dataframe(df)


def load_orders_from_bytes(content: bytes, source: str = "orders") -> list[Order]:
    df = _parse_csv(content, source, _ORDER_COLUMNS)
    return orders_from_dataframe(df)


def load_vehicles_from_bytes(content: bytes, source: str = "vehicles") -> list[Vehicle]:
    df = _parse_csv(content, source, _VEHICLE_COLUMNS)
    return vehicles_from_dataframe(df)


def load_warehouses(path: str | Path) -> list[Warehouse]:
    df = _read_csv(path, _WAREHOUSE_COLUMNS)
    return warehouses_from_dataframe(df)


def load_warehouses_from_bytes(content: bytes, source: str = "warehouses") -> list[Warehouse]:
    df = _parse_csv(content, source, _WAREHOUSE_COLUMNS)
    return warehouses_from_dataframe(df)


def warehouses_from_dataframe(df: pd.DataFrame) -> list[Warehouse]:
    return [
        Warehouse(
            warehouse_id=str(row.warehouse_id),
            location=Location(lat=float(row.lat), lng=float(row.lng)),
            name=str(row.name),
        )
        for row in df.itertuples(index=False)
    ]


def orders_from_dataframe(df: pd.DataFrame) -> list[Order]:
    return [
        Order(
            order_id=str(row.order_id),
            warehouse_id=str(row.warehouse_id),
            location=Location(lat=float(row.lat), lng=float(row.lng)),
            weight=float(row.weight),
            volume=float(row.volume),
        )
        for row in df.itertuples(index=False)
    ]


def vehicles_from_dataframe(df: pd.DataFrame) -> list[Vehicle]:
    return [
        Vehicle(
            vehicle_id=str(row.vehicle_id),
            current_warehouse_id=str(row.warehouse_id),
            max_weight=float(row.max_weight),
            max_volume=float(row.max_volume),
        )
        for row in df.itertuples(index=False)
    ]


def _read_csv(path: str | Path, required_columns: set[str]) -> pd.DataFrame:
    source = str(path)
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise LoadError(source, "file not found")
    except Exception as e:
        raise LoadError(source, f"cannot read file: {e}")
    return _validate_columns(df, source, required_columns)


def _parse_csv(content: bytes, source: str, required_columns: set[str]) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise LoadError(source, f"cannot parse CSV: {e}")
    return _validate_columns(df, source, required_columns)


def _validate_columns(df: pd.DataFrame, source: str, required_columns: set[str]) -> pd.DataFrame:
    missing = required_columns - set(df.columns)
    if missing:
        raise LoadError(source, f"missing columns: {sorted(missing)}")
    return df[list(required_columns)].dropna()