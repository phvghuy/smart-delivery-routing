from pathlib import Path

import folium

from smart_delivery_routing.domain.models import Order, RoutingResult, Vehicle

_COLORS = [
    "blue", "red", "green", "purple", "orange",
    "darkred", "darkblue", "darkgreen", "cadetblue", "pink",
]


def build_map(
    result: RoutingResult,
    orders: list[Order],
    vehicles: list[Vehicle],
) -> folium.Map:
    order_by_id = {o.order_id: o for o in orders}
    vehicle_by_id = {v.vehicle_id: v for v in vehicles}
    depot = vehicles[0].depot

    fmap = folium.Map(location=[depot.lat, depot.lng], zoom_start=12)
    _add_depot_marker(fmap, depot)

    for idx, route in enumerate(result.routes):
        color = _COLORS[idx % len(_COLORS)]
        group = folium.FeatureGroup(name=f"{route.vehicle_id} ({len(route.stops)} stops)", show=True)

        coords = [[depot.lat, depot.lng]]
        for stop in route.stops:
            order = order_by_id[stop.order_id]
            coords.append([stop.location.lat, stop.location.lng])
            _add_stop_marker(group, order, color)
        coords.append([depot.lat, depot.lng])  # return to depot

        folium.PolyLine(
            locations=coords,
            color=color,
            weight=2.5,
            opacity=0.8,
            tooltip=f"{route.vehicle_id} — {route.total_distance:.1f} km",
        ).add_to(group)

        group.add_to(fmap)

    _add_unassigned_markers(fmap, result.unassigned_orders, order_by_id)
    folium.LayerControl(collapsed=False).add_to(fmap)

    return fmap


def save_map(fmap: folium.Map, path: str | Path) -> None:
    fmap.save(str(path))


def _add_depot_marker(fmap: folium.Map, depot) -> None:
    folium.Marker(
        location=[depot.lat, depot.lng],
        popup="Depot",
        tooltip="Depot",
        icon=folium.Icon(color="black", icon="home", prefix="fa"),
    ).add_to(fmap)


def _add_stop_marker(group: folium.FeatureGroup, order: Order, color: str) -> None:
    popup_html = (
        f"<b>{order.order_id}</b><br>"
        f"Weight: {order.weight} kg<br>"
        f"Volume: {order.volume} m³"
    )
    folium.CircleMarker(
        location=[order.location.lat, order.location.lng],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=folium.Popup(popup_html, max_width=200),
        tooltip=order.order_id,
    ).add_to(group)


def _add_unassigned_markers(
    fmap: folium.Map,
    unassigned_ids: list[str],
    order_by_id: dict[str, Order],
) -> None:
    if not unassigned_ids:
        return
    group = folium.FeatureGroup(name=f"Unassigned ({len(unassigned_ids)})", show=True)
    for order_id in unassigned_ids:
        order = order_by_id[order_id]
        folium.CircleMarker(
            location=[order.location.lat, order.location.lng],
            radius=5,
            color="gray",
            fill=True,
            fill_opacity=0.5,
            popup=folium.Popup(f"<b>{order_id}</b><br>Weight: {order.weight} kg<br>Volume: {order.volume} m³", max_width=200),
            tooltip=f"{order_id} (unassigned)",
        ).add_to(group)
    group.add_to(fmap)