import json
from pathlib import Path

import streamlit.components.v1 as components

HTML_FILE = Path(__file__).with_name("manta_viewer.html")


def show_manta_viewer(scenario="normal", height=690):
    template = HTML_FILE.read_text(encoding="utf-8")
    config = json.dumps({"scenario": scenario}).replace("<", "\\u003c")
    html = template.replace("__DEEPTWIN_CONFIG__", config)
    components.html(html, height=height, scrolling=False)
