import base64
import sys
import tempfile
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

simulation_folder = BASE_DIR / "member_2_simulation"
sys.path.insert(0, str(simulation_folder))

from simulation import MiniROVSimulation, MissionState


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="REMORA | Digital Twin",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# FIND THE LIVE VIEWER HTML
# --------------------------------------------------

HTML_CANDIDATES = [
    BASE_DIR / "assets" / "manta_interactive.html",
    BASE_DIR / "manta_interactive.html",
    BASE_DIR / "manta_viewer" / "manta_interactive.html",
]

HTML_FILE = next(
    (
        path
        for path in HTML_CANDIDATES
        if path.is_file()
    ),
    None,
)

if HTML_FILE is None:
    st.error(
        "Cannot find manta_interactive.html. "
        "Place it inside the assets folder beside dashboard.py."
    )

    st.code(
        """your_project/
├── dashboard.py
├── assets/
│   ├── manta_interactive.html
│   └── submarine.jpg
└── member_2_simulation/
    └── simulation.py""",
        language="text",
    )

    st.stop()

html_source = HTML_FILE.read_text(encoding="utf-8")

if "streamlit:render" not in html_source:
    st.error(
        "Your HTML appears to be the original standalone demo. "
        "Use the updated live-viewer HTML that receives Python "
        "mission data, and keep its filename as "
        "manta_interactive.html."
    )

    st.stop()


# --------------------------------------------------
# PREPARE THE CUSTOM VIEWER
#
# Your source file keeps the name manta_interactive.html.
# Streamlit receives an internal index.html copy.
# --------------------------------------------------

@st.cache_resource(show_spinner=False)
def prepare_viewer_directory(source):
    viewer_directory = Path(
        tempfile.mkdtemp(prefix="remora_live_viewer_")
    )

    (viewer_directory / "index.html").write_text(
        source,
        encoding="utf-8",
    )

    return str(viewer_directory)


model_view = components.declare_component(
    "remora_live_model",
    path=prepare_viewer_directory(html_source),
)


# --------------------------------------------------
# UI THEME
# Kept outside periodically refreshed fragments.
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --void: #04080D;
        --deep: #070F18;
        --panel: #0A1622;
        --panel-soft: #0D1D2B;
        --line: #17324A;
        --line-bright: #23506F;
        --ice: #BFE9FF;
        --blue: #37B6FF;
        --white: #F4FAFF;
        --muted: #8FA9BC;
    }

    html,
    body,
    .stApp {
        background: #04080D;
        color: var(--white);
        font-family: "Space Grotesk", sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: transparent !important;
    }

    #MainMenu,
    footer,
    header[data-testid="stHeader"] {
        visibility: hidden;
    }

    .block-container {
        max-width: 1500px !important;
        padding-top: 1.6rem !important;
        padding-bottom: 3rem !important;
    }

    /* Typography */

    h1,
    h2,
    h3 {
        font-family: "Space Grotesk", sans-serif !important;
        color: var(--white) !important;
    }

    h1 {
        font-size: 2.65rem !important;
        letter-spacing: -.035em !important;
    }

    h2 {
        font-size: 1.18rem !important;
        letter-spacing: .12em !important;
        text-transform: uppercase !important;
        color: var(--ice) !important;
        margin-top: 1.7rem !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--white) !important;
    }

    [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
    }

    /* Metric cards */

    [data-testid="stMetric"] {
        padding: 18px 20px !important;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: linear-gradient(
            145deg,
            rgba(18,38,55,.96),
            rgba(9,21,32,.98)
        );
        box-shadow: 0 12px 30px rgba(0,0,0,.28);
        overflow: hidden;
    }

    [data-testid="stMetric"]::after {
        content: none !important;
    }

    [data-testid="stMetricLabel"] p {
        font-size: .76rem !important;
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: "IBM Plex Mono", monospace !important;
        font-size: 1.65rem !important;
        color: var(--white) !important;
    }

    /* Inputs */

    [data-baseweb="select"] > div {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
    }

    [data-baseweb="select"] span {
        color: var(--white) !important;
    }

    /* Supporting components */

    [data-testid="stAlert"],
    [data-testid="stExpander"] {
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
    }

    [data-testid="stExpander"],
    [data-testid="stCodeBlock"] {
        background: var(--panel) !important;
    }

    /* Hero */

    .remora-hero {
        position: relative;
        overflow: hidden;
        padding: 30px 34px;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: linear-gradient(
            145deg,
            rgba(13,30,45,.91),
            rgba(5,12,20,.96)
        );
        box-shadow: 0 28px 70px rgba(0,0,0,.40);
    }

    .remora-hero::before {
        content: "";
        position: absolute;
        inset: -40%;
        background: conic-gradient(
            from 180deg,
            transparent 0%,
            rgba(55,182,255,.08) 8%,
            rgba(55,182,255,.30) 18%,
            rgba(191,233,255,.14) 23%,
            rgba(55,182,255,.05) 30%,
            transparent 38%
        );
        animation: remora-orbit 14s linear infinite;
        pointer-events: none;
    }

    .remora-hero > * {
        position: relative;
        z-index: 1;
    }

    .remora-hero h1 {
        margin: 8px 0 !important;
        padding: 0 !important;
    }

    .remora-hero p {
        max-width: 780px;
        color: var(--muted);
        margin: 12px 0 0;
    }

    .remora-chip {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        padding: 7px 14px;
        border: 1px solid var(--line-bright);
        border-radius: 999px;
        background: var(--panel);
        color: var(--ice);
        font-family: "IBM Plex Mono", monospace;
        font-size: .70rem;
        letter-spacing: .12em;
        text-transform: uppercase;
    }

    .remora-chip::before {
        content: "";
        height: 7px;
        width: 7px;
        border-radius: 50%;
        background: var(--blue);
    }

    @keyframes remora-orbit {
        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }

    /* Mission Controls */

    .st-key-mission_controls {
        padding: 26px 28px !important;
        margin-top: 1.7rem;
        border: 1px solid var(--line-bright) !important;
        border-left: 4px solid var(--blue) !important;
        border-radius: 18px !important;
        background: #0D1D2B !important;
        box-shadow: 0 16px 40px rgba(0,0,0,.32);
    }

    .console-heading {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 15px;
        flex-wrap: wrap;
    }

    .console-number {
        font-family: "IBM Plex Mono", monospace;
        font-size: .70rem;
        color: var(--muted);
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .console-title {
        font-size: 1.6rem !important;
        text-transform: none !important;
        letter-spacing: -.03em !important;
        margin: 0 !important;
        padding: 0 !important;
        color: var(--white) !important;
    }

    .console-state {
        font-size: .72rem;
        font-family: "IBM Plex Mono", monospace;
        color: var(--ice);
        border: 1px solid var(--line-bright);
        border-radius: 6px;
        padding: 7px 10px;
    }

    .console-subtitle {
        font-size: .92rem;
        line-height: 1.65;
        color: var(--muted);
        margin: 10px 0 14px;
    }

    .st-key-override_panel {
        padding: 18px 20px !important;
        border: 1px solid var(--line-bright) !important;
        border-radius: 12px !important;
        background: #091622 !important;
    }

    .override-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--white);
        margin-bottom: 5px;
    }

    .override-copy {
        font-size: .85rem;
        line-height: 1.65;
        color: var(--muted);
    }

    .st-key-override_panel [data-testid="stCheckbox"] p {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--ice) !important;
    }

    .console-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: .70rem;
        color: var(--muted);
        letter-spacing: .12em;
        text-transform: uppercase;
        margin: 12px 0 3px;
    }

    /* Buttons */

    .stButton > button {
        width: 100%;
        min-height: 54px;
        border: 1px solid var(--line-bright) !important;
        border-radius: 10px !important;
        background: #10283A !important;
        color: var(--white) !important;
        transition:
            background-color .2s,
            border-color .2s !important;
    }

    .stButton > button p {
        font-family: "Space Grotesk", sans-serif !important;
        font-size: .96rem !important;
        font-weight: 600 !important;
        color: inherit !important;
    }

    .stButton > button:hover:not(:disabled) {
        background: #15364C !important;
        border-color: var(--blue) !important;
    }

    .stButton > button:disabled {
        opacity: .40 !important;
        cursor: not-allowed;
    }

    .stButton > button:focus-visible {
        outline: 2px solid var(--ice) !important;
        outline-offset: 3px;
    }

    .st-key-deploy_control button {
        background: #155379 !important;
        border-color: var(--blue) !important;
    }

    .st-key-reset_control button {
        background: transparent !important;
        color: var(--muted) !important;
    }

    .console-note {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--line);
        font-size: .76rem;
        line-height: 1.6;
        color: var(--muted);
    }

    /* Live viewer */

    .st-key-live_model_panel {
        border: 1px solid var(--line-bright) !important;
        border-radius: 18px !important;
        overflow: hidden;
        background: #04141F !important;
        padding: 3px !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: var(--line) !important;
        margin: 1.3rem 0 !important;
    }

    @media (max-width: 700px) {
        .st-key-mission_controls {
            padding: 22px 16px !important;
        }

        .st-key-override_panel {
            padding: 15px !important;
        }

        .remora-hero {
            padding: 26px 24px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .remora-hero::before {
            animation: none !important;
        }

        .stButton > button {
            transition: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# BACKGROUND IMAGE
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("ascii")


background_file = BASE_DIR / "assets" / "submarine.jpg"

if background_file.is_file():
    encoded_background = encode_image(
        background_file.read_bytes()
    )

    background_css = """
    <style>
    .stApp {
        background-color: #04080D !important;
        background-image:
            linear-gradient(
                90deg,
                rgba(4,8,13,.78),
                rgba(4,8,13,.52) 55%,
                rgba(4,8,13,.28)
            ),
            linear-gradient(
                180deg,
                rgba(4,8,13,.10),
                rgba(4,8,13,.20) 65%,
                rgba(4,8,13,.65)
            ),
            url("data:image/jpeg;base64,__IMAGE__") !important;
        background-size: cover !important;
        background-position: right center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }
    </style>
    """

    st.markdown(
        background_css.replace(
            "__IMAGE__",
            encoded_background,
        ),
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SIMULATION TIMING AND SESSION STATE
# --------------------------------------------------

SIMULATION_STEP_SECONDS = 0.2
MAX_CATCHUP_STEPS = 5

if "rov" not in st.session_state:
    st.session_state.rov = MiniROVSimulation()

if "running" not in st.session_state:
    st.session_state.running = False

if "last_simulation_tick" not in st.session_state:
    st.session_state.last_simulation_tick = time.monotonic()


# --------------------------------------------------
# MISSION HELPERS
# --------------------------------------------------

def is_idle(rov):
    return rov.state in (
        MissionState.DOCKED,
        MissionState.MISSION_COMPLETE,
    )


def reset_mission():
    st.session_state.rov = MiniROVSimulation()
    st.session_state.running = False
    st.session_state.last_simulation_tick = time.monotonic()

    st.session_state.scenario_selector = (
        st.session_state.rov.selected_scenario
    )

    st.session_state.operator_override = False

    st.session_state.pop("mission_notice", None)


def deploy_mission():
    rov = st.session_state.rov
    scenario = st.session_state.scenario_selector

    operator_override = bool(
        st.session_state.get("operator_override", False)
    )

    if is_idle(rov):
        success = rov.start_deployment(
            scenario,
            operator_override=operator_override,
        )
    else:
        success = False

    if success:
        st.session_state.running = True
        st.session_state.last_simulation_tick = (
            time.monotonic()
        )

        st.session_state.pop("mission_notice", None)

    else:
        st.session_state.mission_notice = (
            "Deployment could not be started."
        )


def pause_mission():
    st.session_state.running = False
    st.session_state.last_simulation_tick = time.monotonic()


def resume_mission():
    if not is_idle(st.session_state.rov):
        st.session_state.running = True
        st.session_state.last_simulation_tick = (
            time.monotonic()
        )


def advance_due_steps():
    now = time.monotonic()

    if not st.session_state.running:
        st.session_state.last_simulation_tick = now
        return

    elapsed = max(
        0.0,
        now - st.session_state.last_simulation_tick,
    )

    due_steps = int(
        elapsed / SIMULATION_STEP_SECONDS
    )

    steps = min(
        due_steps,
        MAX_CATCHUP_STEPS,
    )

    if steps == 0:
        return

    rov = st.session_state.rov

    for _ in range(steps):
        rov.advance()

        if rov.state == MissionState.MISSION_COMPLETE:
            st.session_state.running = False
            st.session_state.last_simulation_tick = now

            # Refresh static button states once at completion.
            st.rerun()

    if due_steps > MAX_CATCHUP_STEPS:
        # Avoid a long catch-up freeze after browser sleep
        # or an extended delay.
        st.session_state.last_simulation_tick = now
    else:
        st.session_state.last_simulation_tick += (
            steps * SIMULATION_STEP_SECONDS
        )


def serialize_points(values):
    return [
        [
            float(point[0]),
            float(point[1]),
            float(point[2]),
        ]
        for point in values
    ]


def display_history(history, limit=1000):
    count = len(history)

    if count <= limit:
        return serialize_points(history)

    indexes = [
        round(
            index * (count - 1) / (limit - 1)
        )
        for index in range(limit)
    ]

    return serialize_points(
        [history[index] for index in indexes]
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="remora-hero">
        <div class="remora-chip">
            Digital Twin · Simulation
        </div>
        <h1>REMORA</h1>
        <p>
            Autonomous underwater inspection system —
            a live digital twin for mission planning,
            risk assessment, deployment control,
            and post-mission inspection records.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# --------------------------------------------------
# STATIC SCENARIO AND DECISION SECTIONS
#
# These no longer redraw on the 200 ms viewer timer.
# --------------------------------------------------

rov = st.session_state.rov
mission_idle = is_idle(rov)

st.header("1 · Underwater Inspection Scenario")

scenario_options = list(rov.SCENARIOS.keys())

selected_scenario = st.selectbox(
    "Select a simulated underwater condition",
    scenario_options,
    index=scenario_options.index(
        rov.selected_scenario
    ),
    disabled=not mission_idle,
    key="scenario_selector",
)

if selected_scenario != rov.selected_scenario:
    rov.select_inspection_scenario(
        selected_scenario
    )


st.header("2 · AI Inspection Necessity Engine")

decision_data = rov.evaluate_inspection_need(
    selected_scenario
)

decision = decision_data["decision"]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Anomaly Severity",
    f'{decision_data["severity"]}/10',
)

col2.metric(
    "Sensor Confidence",
    f'{decision_data["confidence"]}%',
)

col3.metric(
    "Delay Risk",
    f'{decision_data["delay_risk"]}/10',
)

if decision == "DEPLOY":
    st.success(
        "DEPLOY — Inspection is justified "
        "based on the simulated risk."
    )

elif decision == "MONITOR":
    st.info(
        "MONITOR — No immediate deployment is recommended."
    )

else:
    st.warning(
        "ESCALATE — Human assessment is recommended."
    )

score1, score2 = st.columns(2)

score1.metric(
    "Anomaly Risk Score",
    decision_data["anomaly_risk_score"],
)

score2.metric(
    "Deployment Cost Score",
    decision_data["deployment_cost"],
)

st.caption(
    "Decision engine: rule-based prototype. "
    "Not a trained machine-learning model."
)


# --------------------------------------------------
# STATIC MISSION CONTROLS
#
# Buttons use callbacks instead of being rebuilt
# by the fast viewer timer.
# --------------------------------------------------

with st.container(
    key="mission_controls",
    border=False,
):
    if rov.state == MissionState.MISSION_COMPLETE:
        badge = "MISSION COMPLETE"

    elif st.session_state.running:
        badge = "SIMULATION RUNNING"

    elif not mission_idle:
        badge = "SIMULATION PAUSED"

    else:
        badge = "MISSION STANDBY"

    st.markdown(
        f"""
        <div class="console-heading">
            <div>
                <div class="console-number">
                    03 / Mission operations
                </div>
                <h2 class="console-title">
                    Mission Controls
                </h2>
            </div>
            <span class="console-state">
                {badge}
            </span>
        </div>
        <div class="console-subtitle">
            Manage deployment and playback.
            The models below use the same Python mission.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(
        key="override_panel",
        border=False,
    ):
        description_col, toggle_col = st.columns(
            [3, 1]
        )

        with description_col:
            st.markdown(
                """
                <div class="override-title">
                    Operator override
                </div>
                <div class="override-copy">
                    Permit demonstration deployment when
                    the engine recommends MONITOR or ESCALATE.
                    Not real operational authorization.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with toggle_col:
            operator_override = st.toggle(
                "Enable override",
                key="operator_override",
                disabled=not mission_idle,
            )

    st.markdown(
        """
        <div class="console-label">
            Deployment & playback
        </div>
        """,
        unsafe_allow_html=True,
    )

    control1, control2, control3, control4 = (
        st.columns(4)
    )

    with control1:
        with st.container(key="deploy_control"):
            st.button(
                "Deploy REMORA",
                on_click=deploy_mission,
                disabled=(
                    not mission_idle
                    or (
                        decision != "DEPLOY"
                        and not operator_override
                    )
                ),
                use_container_width=True,
            )

    with control2:
        st.button(
            "Pause Simulation",
            on_click=pause_mission,
            disabled=not st.session_state.running,
            use_container_width=True,
        )

    with control3:
        st.button(
            "Resume Simulation",
            on_click=resume_mission,
            disabled=(
                st.session_state.running
                or mission_idle
            ),
            use_container_width=True,
        )

    with control4:
        with st.container(key="reset_control"):
            st.button(
                "Reset Mission",
                on_click=reset_mission,
                use_container_width=True,
            )

    st.markdown(
        """
        <div class="console-note">
            Pause holds the mission state.
            Camera orbit is independent.
            Reset creates a new mission.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("mission_notice"):
        st.warning(
            st.session_state.mission_notice
        )


# --------------------------------------------------
# LIVE METRICS
# Only this small section refreshes every 500 ms.
# --------------------------------------------------

st.header("4 · Live Mission Dashboard")


@st.fragment(run_every="500ms")
def live_metrics():
    status = st.session_state.rov.get_status()

    status1, status2, status3, status4 = (
        st.columns(4)
    )

    status1.metric(
        "Mission State",
        status["state"],
    )

    status2.metric(
        "Mini ROV Battery",
        f'{status["battery"]}%',
    )

    status3.metric(
        "Inspection Progress",
        f'{status["inspection_progress"]}/'
        f'{status["total_waypoints"]}',
    )

    status4.metric(
        "Connection Status",
        (
            "CONNECTED"
            if status["connected"]
            else "DETACHED"
        ),
    )


live_metrics()


# --------------------------------------------------
# LIVE 3D VIEWER
# Static heading and slider stay outside its timer.
# --------------------------------------------------

st.header("5 · 3D Underwater Digital Twin")

st.caption(
    "Live Python mission · "
    "Automatic 360° camera orbit · "
    "Drag to rotate · Scroll to zoom"
)

st.slider(
    "Model display scale",
    min_value=0.10,
    max_value=1.00,
    value=0.35,
    step=0.05,
    key="model_scale",
    help=(
        "Changes visual dimensions only. "
        "Vehicle centers and inspection targets "
        "use Python simulation coordinates."
    ),
)


@st.fragment(run_every="200ms")
def live_viewer():
    # Only this function advances the simulation.
    advance_due_steps()

    current_rov = st.session_state.rov
    status = current_rov.get_status()

    payload = {
        "main_position": serialize_points(
            [status["main_auv_position"]]
        )[0],
        "position": serialize_points(
            [status["position"]]
        )[0],
        "waypoints": serialize_points(
            current_rov.waypoints
        ),
        "history": display_history(
            status["position_history"]
        ),
        "state": str(status["state"]),
        "battery": float(status["battery"]),
        "progress": int(
            status["inspection_progress"]
        ),
        "total": int(
            status["total_waypoints"]
        ),
        "connected": bool(status["connected"]),
        "running": bool(
            st.session_state.running
        ),
        "model_scale": float(
            st.session_state.model_scale
        ),
    }

    with st.container(
        key="live_model_panel",
        border=False,
    ):
        model_view(
            mission=payload,
            key="remora_live_3d",
            default=None,
        )


live_viewer()

st.caption(
    "Models are illustrative. Python supplies the route, "
    "vehicle centers, battery, and inspection progress. "
    "Camera movement does not change the mission."
)


# --------------------------------------------------
# INSPECTION RECORDS
# Refreshed less frequently than the 3D viewer.
# --------------------------------------------------

st.header("6 · Inspection Records")


@st.fragment(run_every="2s")
def inspection_records():
    status = st.session_state.rov.get_status()
    records = status["inspection_records"]

    if not records:
        st.info(
            "No inspection records have been generated yet."
        )
        return

    for index, record in enumerate(
        records,
        start=1,
    ):
        with st.expander(
            f'Inspection {index:02d} — {record["target"]}',
            expanded=True,
        ):
            record1, record2 = st.columns(2)

            with record1:
                st.write("**Scenario**")

                st.code(
                    record["scenario"],
                    language="text",
                )

                st.write("**Finding**")
                st.write(record["finding"])

            with record2:
                st.metric(
                    "Severity",
                    f'{record["severity"]}/10',
                )

                st.metric(
                    "Sensor Confidence",
                    f'{record["confidence"]}%',
                )


inspection_records()


# --------------------------------------------------
# ROBOT POSITIONS
# Refreshed once per second.
# --------------------------------------------------

st.header("7 · Robot Position Information")


@st.fragment(run_every="1s")
def robot_positions():
    status = st.session_state.rov.get_status()

    position1, position2 = st.columns(2)

    with position1:
        st.write("**Main submarine position**")

        st.code(
            str(status["main_auv_position"]),
            language="text",
        )

    with position2:
        st.write("**REMORA position**")

        st.code(
            str(status["position"]),
            language="text",
        )


robot_positions()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "REMORA Hackathon Prototype · "
    "Simulated underwater environment · "
    "Not validated for real submarine operations"
)