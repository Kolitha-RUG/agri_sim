import streamlit as st
import json
from pathlib import Path

st.title("🍇 Vineyard Layout Viewer (p5.js in Streamlit)")

# Sidebar controls
num_workers = st.sidebar.slider("Number of Workers", 1, 10, 5)
num_drones = st.sidebar.slider("Number of Drones", 0, 5, 2)
num_collection_points = st.sidebar.slider("Number of Collection Points", 1, 3, 1)

if st.button("Show Layout"):
    # Generate positions (for now just static positions)
    workers = [{"id": i, "x": i * 2, "y": 2} for i in range(1, num_workers + 1)]
    drones = [{"id": j, "x": j * 2, "y": 8} for j in range(1, num_drones + 1)]
    collection_points = [{"x": 10, "y": 5 + i * 2} for i in range(num_collection_points)]

    data = {
        "workers": workers,
        "drones": drones,
        "collection_points": collection_points
    }

    # Load the HTML template
    html_template = Path("agri_anim.html").read_text()

    # Inject the JSON data
    html_filled = html_template.replace("{{DATA}}", json.dumps(data))

    # Display in Streamlit
    st.components.v1.html(html_filled, height=520)
