import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from smart_delivery_routing.application.data_loader import LoadError, load_orders_from_bytes, load_vehicles_from_bytes
from smart_delivery_routing.application.kpi import KPIReport
from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.application.solvers.ortools_solver import ORToolsSolver
from smart_delivery_routing.application.use_cases import OptimizeRoutesInput, OptimizeRoutesOutput, ValidationFailed, optimize_routes
from smart_delivery_routing.infrastructure.distance import HaversineDistanceCalculator
from smart_delivery_routing.interface.visualizer import build_map

_nn_solver = NearestNeighborSolver()
_or_solver = ORToolsSolver(time_limit_seconds=30)
_distance_calculator = HaversineDistanceCalculator()

st.set_page_config(page_title="Smart Delivery Routing", page_icon="🚚", layout="wide")


def main() -> None:
    st.title("Smart Delivery Routing")

    with st.sidebar:
        _render_sidebar()

    nn_output = st.session_state.get("nn_output")
    or_output = st.session_state.get("or_output")

    if nn_output and or_output:
        tab_nn, tab_or = st.tabs(["Nearest Neighbor", "OR-Tools"])
        with tab_nn:
            _render_result(nn_output)
        with tab_or:
            _render_result(or_output)


def _render_sidebar() -> None:
    st.header("Upload Data")
    orders_file = st.file_uploader("Orders CSV", type="csv", key="orders_upload")
    vehicles_file = st.file_uploader("Vehicles CSV", type="csv", key="vehicles_upload")

    # st.divider()
    # time_limit = st.slider("OR-Tools time limit (s)", min_value=5, max_value=120, value=30, step=5)

    disabled = not (orders_file and vehicles_file)
    if st.button("Optimize", type="primary", disabled=disabled):
        _run(orders_file, vehicles_file)


def _run(orders_file, vehicles_file) -> None:
    try:
        orders = load_orders_from_bytes(orders_file.read(), source=orders_file.name)
        vehicles = load_vehicles_from_bytes(vehicles_file.read(), source=vehicles_file.name)
    except LoadError as e:
        st.error(str(e))
        return

    input_data = OptimizeRoutesInput(orders=orders, vehicles=vehicles)

    with st.spinner("Running Nearest Neighbor..."):
        try:
            nn_output = optimize_routes(input_data, _nn_solver, _distance_calculator)
        except ValidationFailed as e:
            for err in e.errors:
                st.error(f"[{err.entity_id}] {err.field}: {err.reason}")
            return

    or_solver = ORToolsSolver(time_limit_seconds=0)
    with st.spinner(f"Running OR-Tools (max 10s)..."):
        or_output = optimize_routes(input_data, or_solver, _distance_calculator)

    st.session_state.update({
        "nn_output": nn_output,
        "or_output": or_output,
        "orders": orders,
        "vehicles": vehicles,
    })
    st.success("Done!")


# --- Result rendering ---

def _render_result(output: OptimizeRoutesOutput) -> None:
    _render_kpi_metrics(output.kpi)
    st.divider()
    _render_map_section(output)
    st.divider()
    _render_vehicle_table(output.kpi)
    if output.result.unassigned_orders:
        _render_unassigned(output.result.unassigned_orders)


def _render_kpi_metrics(kpi: KPIReport) -> None:
    st.subheader("KPI Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Distance", f"{kpi.total_distance_km:.1f} km")
    c2.metric("Vehicles Used", kpi.vehicles_used)
    c3.metric("Avg Fill (Weight)", f"{kpi.average_fill_rate_weight:.1%}")
    c4.metric("Avg Fill (Volume)", f"{kpi.average_fill_rate_volume:.1%}")
    if kpi.unassigned_count:
        st.warning(f"{kpi.unassigned_count} orders could not be assigned.")


def _render_map_section(output: OptimizeRoutesOutput) -> None:
    st.subheader("Route Map")
    vehicles = st.session_state.get("vehicles", [])
    orders = st.session_state.get("orders", [])
    fmap = build_map(output.result, orders, vehicles)
    st_folium(fmap, use_container_width=True, height=800, returned_objects=[])


def _render_vehicle_table(kpi: KPIReport) -> None:
    st.subheader("Per Vehicle Breakdown")
    rows = [
        {
            "Vehicle": v.vehicle_id,
            "Stops": v.stops_count,
            "Distance (km)": round(v.distance_km, 2),
            "Fill Weight": f"{v.fill_rate_weight:.1%}",
            "Fill Volume": f"{v.fill_rate_volume:.1%}",
        }
        for v in kpi.per_vehicle
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_unassigned(unassigned: list[str]) -> None:
    with st.expander(f"Unassigned Orders ({len(unassigned)})"):
        st.dataframe(pd.DataFrame({"order_id": unassigned}), hide_index=True)


if __name__ == "__main__":
    main()
