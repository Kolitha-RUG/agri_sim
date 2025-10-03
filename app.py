import streamlit as st
from agrisim import run_sim


st.title("🍇 Vineyard Simulation")

# Sidebar controls
num_workers = st.sidebar.slider("Number of Workers", 1, 10, 5)
num_drones = st.sidebar.slider("Number of Drones", 0, 5, 2)
fatigue_threshold = st.sidebar.slider("Fatigue Threshold", 1, 10, 3)
sim_time = st.sidebar.slider("Simulation Time (minutes)", 10, 200, 60)

if st.button("Run Simulation"):
    workers, drones, queue = run_sim(
        num_workers=num_workers,
        num_drones=num_drones,
        sim_time=sim_time,
        fatigue_threshold=fatigue_threshold
    )

    st.success("Simulation finished!")
    st.write(f"Final queue size: {len(queue.items)}")
    st.write(f"Total workers: {num_workers}, Total drones: {num_drones}")
    st.write("You could now add charts or logs here 🚀")
