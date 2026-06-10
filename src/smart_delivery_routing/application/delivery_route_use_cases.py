from collections import defaultdict
from dataclasses import replace
from datetime import datetime, timezone
from uuid import UUID, uuid4

from smart_delivery_routing.domain.delivery import (
    DeliveryRouteRepository, DriverRepository, RouteStopRepository,
)
from smart_delivery_routing.domain.delivery.models import (
    DeliveryRoute, DeliveryRouteStatus, Driver,
    RouteStop, RouteStopStatus,
)
from smart_delivery_routing.domain.linehaul import ParcelRepository, ParcelStatus
from smart_delivery_routing.domain.linehaul.models import Parcel
from smart_delivery_routing.application.services import DistanceCalculator
from smart_delivery_routing.domain.linehaul.queries import ParcelQuery
from smart_delivery_routing.domain.shared.value_objects import Location
from smart_delivery_routing.domain.shipping import ShippingRequestRepository


def _build_distance_matrix(
    locations: list[Location],
    calculator: DistanceCalculator,
) -> list[list[float]]:
    return calculator.compute_matrix(locations)


def _nearest_neighbor_order(matrix: list[list[float]]) -> tuple[list[int], float]:
    n = len(matrix)
    if n <= 1:
        return list(range(n)), 0.0
    visited = [False] * n
    visited[0] = True
    order, current, total = [0], 0, 0.0
    for _ in range(n - 1):
        best, best_d = -1, float("inf")
        for j in range(n):
            if not visited[j] and matrix[current][j] < best_d:
                best_d, best = matrix[current][j], j
        visited[best] = True
        order.append(best)
        total += best_d
        current = best
    return order, total


def _optimize_stops(
    stops_data: list[tuple[Parcel, Location]],
    calculator: DistanceCalculator | None,
) -> tuple[list[tuple[Parcel, Location]], float]:
    if calculator is None or len(stops_data) <= 1:
        return stops_data, 0.0
    locations = [loc for _, loc in stops_data]
    matrix = _build_distance_matrix(locations, calculator)
    indices, total_km = _nearest_neighbor_order(matrix)
    return [stops_data[i] for i in indices], total_km


def create_delivery_routes(
    parcel_repo: ParcelRepository,
    driver_repo: DriverRepository,
    shipping_request_repo: ShippingRequestRepository,
    route_repo: DeliveryRouteRepository,
    stop_repo: RouteStopRepository,
    distance_calculator: DistanceCalculator | None = None,
) -> list[DeliveryRoute]:
    # ── Step 1: collect candidates ────────────────────────────────────────────
    all_parcels = parcel_repo.list(ParcelQuery(
        page_size=100,
        statuses=[ParcelStatus.AT_DESTINATION_HUB],
    ))
    assigned_ids = set(stop_repo.list_active_parcel_ids())
    unassigned = [p for p in all_parcels if p.id not in assigned_ids]

    if not unassigned:
        return []

    free_drivers = driver_repo.list_available()
    if not free_drivers:
        return []

    # ── Step 2: group by hub ──────────────────────────────────────────────────
    parcels_by_hub: dict[UUID, list[Parcel]] = defaultdict(list)
    for p in unassigned:
        parcels_by_hub[p.destination_hub_id].append(p)

    drivers_by_hub: dict[UUID, list[Driver]] = defaultdict(list)
    for d in free_drivers:
        drivers_by_hub[d.current_hub_id].append(d)

    active_hubs = parcels_by_hub.keys() & drivers_by_hub.keys()
    if not active_hubs:
        return []

    # ── Step 3: greedy assignment + persist ───────────────────────────────────
    created_routes: list[DeliveryRoute] = []

    for hub_id in active_hubs:
        hub_parcels = list(parcels_by_hub[hub_id])
        assigned_flags = [False] * len(hub_parcels)

        for driver in drivers_by_hub[hub_id]:
            used_weight = 0.0
            used_volume = 0.0
            driver_parcels: list[Parcel] = []

            for i, parcel in enumerate(hub_parcels):
                if assigned_flags[i]:
                    continue
                fits_weight = parcel.load.weight + used_weight <= driver.capacity.max_weight
                fits_volume = parcel.load.volume + used_volume <= driver.capacity.max_volume
                if fits_weight and fits_volume:
                    driver_parcels.append(parcel)
                    assigned_flags[i] = True
                    used_weight += parcel.load.weight
                    used_volume += parcel.load.volume

            if not driver_parcels:
                continue

            stops_data: list[tuple[Parcel, Location]] = []
            for parcel in driver_parcels:
                req = shipping_request_repo.get_by_id(parcel.shipping_request_id)
                if req is not None:
                    stops_data.append((parcel, req.delivery_address.location))

            if not stops_data:
                continue

            stops_data, total_distance_km = _optimize_stops(stops_data, distance_calculator)

            now = datetime.now(timezone.utc)
            route = DeliveryRoute(
                id=uuid4(),
                driver_id=driver.id,
                hub_id=hub_id,
                status=DeliveryRouteStatus.PLANNED,
                total_distance_km=total_distance_km,
                created_at=now,
            )
            route_repo.save(route)

            for seq, (parcel, location) in enumerate(stops_data, start=1):
                stop_repo.save(RouteStop(
                    id=uuid4(),
                    route_id=route.id,
                    parcel_id=parcel.id,
                    status=RouteStopStatus.PENDING,
                    sequence=seq,
                    location=location,
                ))

            driver_repo.update(replace(driver, status=driver.status.__class__.DELIVERING))
            created_routes.append(route)

    return created_routes
