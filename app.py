import streamlit as st
import plotly.express as px
import pandas as pd
import time
from agrisim import run_sim_stepwise

st.title("🍇 Vineyard Simulation — Live Queue Length")

# Sidebar controls
num_workers = st.sidebar.slider("Number of Workers", 1, 10, 5)
num_drones = st.sidebar.slider("Number of Drones", 0, 5, 2)
fatigue_threshold = st.sidebar.slider("Fatigue Threshold", 1, 10, 3)
sim_time = st.sidebar.slider("Simulation Time (minutes)", 10, 200, 60)

speed = st.sidebar.slider(
    "Animation Speed (1 = Fast, 10 = Slow)",
    min_value=1,
    max_value=10,
    value=3,
    help="Controls how quickly Streamlit updates during animation."
)


if st.button("Run Simulation"):
    st.subheader("📊 Live Queue Length Over Time")

    queue_chart = st.empty()
    queue_metric = st.empty()

    # Data storage
    times = []
    queue_sizes = []

    for t, workers, drones, collection_point in run_sim_stepwise(
        num_workers=num_workers,
        num_drones=num_drones,
        sim_time=sim_time,
        fatigue_threshold=fatigue_threshold
    ):
        queue_length = len(drones[0].box_queue.items) if drones else 0
        times.append(t)
        queue_sizes.append(queue_length)

        queue_metric.metric("Current Queue Length", queue_length)

        df = pd.DataFrame({"Time": times, "QueueLength": queue_sizes})
        fig = px.line(df, x="Time", y="QueueLength", title="Queue Length Over Time")
        fig.update_layout(
            width=700, 
            height=400, 
            yaxis_title="Boxes waiting",
            xaxis=dict(range=[0, sim_time])
        )
        queue_chart.plotly_chart(fig, use_container_width=True)

        time.sleep(speed * 0.05)  # <-- speed control here
