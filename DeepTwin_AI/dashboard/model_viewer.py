
import base64
from pathlib import Path

import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent.parent


def show_3d_model(model_name="main_auv.glb", height=500, fault=None):
    model_path = ROOT / "models" / model_name

    if not model_path.is_file():
        raise FileNotFoundError(f"3D model not found: {model_path}")

    model_data = base64.b64encode(
        model_path.read_bytes()
    ).decode("ascii")

    # Approximate fault locations for our demonstration.
    # These are not verified physical component coordinates.
    fault_settings = {
       "cooling_fault": {
          "label": "COOLING SYSTEM FAILURE",
          "position": "0m 0.4m 0m"
       },
       "battery_overheat": {
          "label": "BATTERY OVERHEAT",
          "position": "0m 0.4m 0m"
        },
       "pressure_fault": {
         "label": "PRESSURE WARNING",
         "position": "1m 0.4m 0m"
        },
        "water_leak": {
          "label": "WATER LEAK",
          "position": "-1m 0.4m 0m"
       }
}

    selected_fault = fault_settings.get(fault)

    warning_html = ""
    marker_html = ""

    if selected_fault and model_name == "main_auv.glb":
        warning_html = (
            '<div class="warning">⚠ '
            + selected_fault["label"]
            + '</div>'
        )

        marker_html = f"""
        <button
            slot="hotspot-fault"
            class="marker"
            data-position="{selected_fault['position']}"
            data-normal="0m 1m 0m"
            aria-label="{selected_fault['label']}">
        </button>
        """

    html = """
    <html>
    <head>
        <style>
            body {
                margin: 0;
                background: #071b30;
                overflow: hidden;
                font-family: Arial, sans-serif;
            }

            model-viewer {
                width: 100%;
                height: 100vh;
                background: #071b30;
            }

            .warning {
                position: absolute;
                top: 20px;
                left: 20px;
                background: #dc2626;
                color: white;
                padding: 12px 18px;
                border-radius: 8px;
                font-weight: bold;
                z-index: 10;
            }

            .marker {
                display: block;
                width: 24px;
                height: 24px;
                background: #ff3030;
                border: 3px solid white;
                border-radius: 50%;
                box-shadow: 0 0 20px #ff3030;
                transform: translate(-50%, -50%);
                cursor: pointer;
            }

            .marker[hidden] {
                display: none;
            }
        </style>

        <script
          type="module"
          src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js">
        </script>
    </head>

    <body>
        WARNING_HTML

        <model-viewer
            src="data:model/gltf-binary;base64,MODEL_DATA"
            camera-controls
            auto-rotate
            shadow-intensity="1"
            exposure="1"
            alt="DeepTwin AI underwater vehicle">

            MARKER_HTML

        </model-viewer>
    </body>
    </html>
    """

    html = html.replace("MODEL_DATA", model_data)
    html = html.replace("WARNING_HTML", warning_html)
    html = html.replace("MARKER_HTML", marker_html)

    components.html(
        html,
        height=height,
        scrolling=False
    )
