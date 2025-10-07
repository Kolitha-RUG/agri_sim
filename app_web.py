import streamlit as st
import json
from agrisim import run_sim_stepwise
from streamlit_autorefresh import st_autorefresh
st.set_page_config(page_title="Vineyard Live Simulation", layout="centered")
st.title("🍇 Vineyard Live Simulation (SimPy + p5.js)")

# Sidebar controls
num_workers = st.sidebar.slider("Number of Workers", 1, 10, 5)
num_drones = st.sidebar.slider("Number of Drones", 0, 5, 2)
fatigue_threshold = st.sidebar.slider("Fatigue Threshold", 1, 10, 3)
sim_time = st.sidebar.slider("Simulation Time (minutes)", 10, 200, 60)

# When button clicked, run one step of simulation and store frame in session_state
if "sim_gen" not in st.session_state:
    st.session_state.sim_gen = None
    st.session_state.last_frame = None

if st.button("Start / Continue Simulation"):
    st.session_state.sim_gen = run_sim_stepwise(
        num_workers=num_workers,
        num_drones=num_drones,
        sim_time=sim_time,
        fatigue_threshold=fatigue_threshold,
    )

if st.session_state.sim_gen is not None:
    try:
        frame = next(st.session_state.sim_gen)
        st.session_state.last_frame = frame
    except StopIteration:
        st.session_state.sim_gen = None

frame = st.session_state.last_frame
if frame:
    t, workers, drones, collection_point = frame
    data = {
        "time": t,
        "workers": [{"x": w.location.x, "y": w.location.y} for w in workers],
        "drones": [{"x": d.location.x, "y": d.location.y} for d in drones],
        "collection_points": [{"x": collection_point.location.x, "y": collection_point.location.y}],
    }

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
    </head>
    <body style="margin:0; overflow:hidden;">
    <script>
      const data = {json.dumps(data)};
      function setup() {{
        createCanvas(800, 500);
        background(230,255,230);
      }}
      function draw() {{
        background(230,255,230);
        fill('green');
        data.collection_points.forEach(cp=>rect(cp.x*40, height-cp.y*40, 15,15));
        fill('red');
        data.workers.forEach(w=>ellipse(w.x*40, height-w.y*40, 15,15));
        fill('blue');
        data.drones.forEach(d=>ellipse(d.x*40, height-d.y*40, 20,20));
        fill(0); textSize(16);
        text("Time: "+data.time.toFixed(2),10,20);
      }}
    </script>
    </body>
    </html>
    """
    st.components.v1.html(html, height=520)

    # auto refresh every 300 ms while simulation running
    if st.session_state.sim_gen is not None:
        # count keeps track of refresh cycles
        count = st_autorefresh(interval=100, limit=None, key="sim_refresh")
