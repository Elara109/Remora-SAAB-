
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Locate the main project folder
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulator.sensor_simulator import generate_sensor_data
from simulator.fault_detector import detect_faults
from dashboard.manta_integration import show_manta_viewer

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="DeepTwin AI",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 DeepTwin AI")
st.caption("MANTA Mini | Underwater Vehicle Monitoring Prototype")

st.divider()

# ---------------------------------------
# SIMULATION CONTROLS
# ---------------------------------------

st.subheader("⚙️ Simulation Controls")

scenario = st.selectbox(
    "Choose a simulation scenario",
    [
        "normal",
        "cooling_fault",
        "battery_overheat",
        "pressure_fault",
        "water_leak"
    ],
    format_func=lambda x: x.replace("_", " ").title()
)

if st.button("▶ Run Simulation", type="primary"):
    st.session_state["reading"] = generate_sensor_data(scenario)

# ---------------------------------------
# DETECT FAULTS
# ---------------------------------------

data = st.session_state.get("reading")

if data is not None:
    faults = detect_faults(data)

    # Prioritize cooling failure when the cooling pump has failed.
    if data.get("cooling_pump_status") == "FAILED":
        active_fault = "cooling_fault"

    elif any(
        f["problem"] == "Battery overheating"
        for f in faults
    ):
        active_fault = "battery_overheat"

    elif any(
        f["problem"] == "Abnormally high pressure reading"
        for f in faults
    ):
        active_fault = "pressure_fault"

    elif any(
        f["problem"] == "Water intrusion detected"
        for f in faults
    ):
        active_fault = "water_leak"

    else:
        active_fault = None

else:
    faults = []
    active_fault = None


# ---------------------------------------
# INTERACTIVE 3D DIGITAL TWIN
# ---------------------------------------

st.divider()
st.subheader("🌊 Interactive MANTA Mini Digital Twin")

st.write(
    "Explore the submarine, investigate detected faults, "
    "and deploy the Mini ROV for inspection."
)

show_manta_viewer(
    scenario=active_fault or "normal",
    height=690
)

st.caption(
    "Interactive 3D mission simulation. "
    "Drag to rotate, scroll to zoom, and use Run mission "
    "to deploy the Mini ROV."
)

# ---------------------------------------
# SENSOR READINGS
# ---------------------------------------




if data is not None:

    st.divider()
    st.subheader("📊 Sensor Readings")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Battery Level",
        f"{data['battery_level']:.1f}%"
    )

    c2.metric(
        "Battery Temperature",
        f"{data['battery_temperature']:.1f} °C"
    )

    c3.metric(
        "Pressure",
        f"{data['pressure']:.2f} bar"
    )

    c4.metric(
        "Water Leak",
        "DETECTED" if data["leak_detected"] else "No leak"
    )

    # ---------------------------------------
    # FAULT DETECTION
    # ---------------------------------------

    st.divider()
    st.subheader("🚨 Fault Detection")

    if not faults:
        st.success("SYSTEM HEALTHY — No faults detected")
    else:
        for fault in faults:
            if fault["severity"] == "CRITICAL":
                st.error(
                    f"CRITICAL: {fault['problem']}"
                )
            else:
                st.warning(
                    f"WARNING: {fault['problem']}"
                )

            st.write(
                f"**Affected component:** {fault['component']}"
            )

            st.write(
                f"**Recommended inspection:** "
                f"{fault['recommendation']}"
            )

    # ---------------------------------------
    # SENSOR DATA TABLE
    # ---------------------------------------

    st.divider()
    st.subheader("📋 Sensor Data")

    st.dataframe(
        pd.DataFrame([data]),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "All readings and fault thresholds are simulated "
        "for demonstration purposes."
    )

else:
    st.info(
        "Choose a simulation scenario and click Run Simulation."
    )
