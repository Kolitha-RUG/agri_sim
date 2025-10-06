import streamlit as st
import plotly.express as px

st.title("🍇 Plotly Cartesian Test")

# Define static points
points = [
    {"x": 0, "y": 0, "type": "Origin"},
    {"x": 5, "y": 5, "type": "Worker"},
    {"x": 10, "y": 2, "type": "Drone"},
    {"x": 8, "y": 8, "type": "Collection Point"},
]

fig = px.scatter(
    points,
    x="x",
    y="y",
    color="type",
    size_max=20,
    symbol="type",
)

fig.update_traces(marker=dict(size=15))  # bigger dots
fig.update_layout(
    xaxis_title="X position",
    yaxis_title="Y position",
    width=600,
    height=600,
)

st.plotly_chart(fig)
