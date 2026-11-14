DeepTwin AI / MANTA Mini
Run: python -m pip install -r requirements.txt
Then: python -m streamlit run dashboard/app.py --server.port 8505
Open http://localhost:8505
Tests: python -m pytest tests -v

The MANTA viewer is the new procedural Three.js submarine, with scenario-driven fault markers and inspection routes. Original Python sensor readings, fault alerts and recommendations remain. Coordinates are illustrative. Internet is needed for the Three.js CDN.
