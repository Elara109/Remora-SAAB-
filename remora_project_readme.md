# REMORA | Autonomous Underwater Inspection Digital Twin

A Streamlit-based live digital twin simulation for mission planning, anomaly risk assessment, deployment control, and post-mission inspection records.

## Project Structure & File Descriptions

* **`dashboard.py`** — The main Streamlit web application. Handles the user interface, AI inspection necessity dashboard, mission playback controls, live telemetry metrics, and the 3D underwater viewer.
* **`member_2_simulation/simulation.py`** — The core Python physics and state-machine engine (`MiniROVSimulation` and `MissionState`). Calculates anomaly risk scores, battery drain, waypoint navigation, and inspection logs.
* **`requirements.txt`** — Lists the Python dependencies (`streamlit` and `plotly`) required to run the dashboard.
* **`assets/manta_interactive.html`** — The interactive 3D live model viewer embedded inside the Streamlit dashboard.
* **`assets/submarine.jpg`** — Background visual asset used in the dashboard UI.

## How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the dashboard:
   ```bash
   streamlit run dashboard.py
   ```