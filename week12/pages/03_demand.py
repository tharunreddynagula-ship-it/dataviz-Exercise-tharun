# pages/03_demand.py
import streamlit as st
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_data, sidebar_filters

# -----------------------------------------------------------------------------
# Load data + shared sidebar filters
# -----------------------------------------------------------------------------
df, p95 = load_data()
filtered = sidebar_filters(df, p95)

st.title("Where is guest demand strongest?")
st.caption(
    "Demand is approximated using reviews per month. "
    "Higher reviews/month generally indicates stronger guest demand."
)

# -----------------------------------------------------------------------------
# Persisted room type selector
# -----------------------------------------------------------------------------
if "sel_room" not in st.session_state:
    st.session_state.sel_room = filtered["room_type"].iloc[0]

# Keep-alive pattern
st.session_state.sel_room = st.session_state.sel_room

room_options = sorted(filtered["room_type"].unique())

# Guard against filtered-out value
if st.session_state.sel_room not in room_options:
    st.session_state.sel_room = room_options[0]

st.selectbox(
    "Focus Room Type",
    room_options,
    key="sel_room"
)

# -----------------------------------------------------------------------------
# Focus dataset
# -----------------------------------------------------------------------------
focus = filtered[
    filtered["room_type"] == st.session_state.sel_room
]

# -----------------------------------------------------------------------------
# KPI Row (5-second test)
# -----------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)

c1.metric(
    "Listings",
    f"{len(focus):,}"
)

c2.metric(
    "Median Reviews / Month",
    round(focus["reviews_per_month"].median(), 2)
)

c3.metric(
    "Median Price (£)",
    round(focus["price"].median(), 0)
)

st.divider()

# -----------------------------------------------------------------------------
# Create highlight column
# Colour type = Highlight (Blue) vs Other (Grey)
# -----------------------------------------------------------------------------
plot_df = filtered.copy()

plot_df["highlight"] = plot_df["room_type"].apply(
    lambda x: "Selected"
    if x == st.session_state.sel_room
    else "Other"
)

# -----------------------------------------------------------------------------
# Scatter Plot
# -----------------------------------------------------------------------------
fig = px.scatter(
    plot_df,
    x="price",
    y="reviews_per_month",
    color="highlight",
    hover_data=["neighbourhood"],
    color_discrete_map={
        "Selected": "#2E75B6",  # Blue
        "Other": "#D3D3D3"      # Grey
    },
    title=f"Insight: {st.session_state.sel_room} listings show the strongest demand pattern"
)

fig.update_traces(
    marker=dict(size=9)
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_family="Arial",
    font_color="black",
    title_font=dict(
        size=18,
        color="black"
    ),
    xaxis_title="Price (£ per Night)",
    yaxis_title="Reviews per Month (Demand Proxy)",
    legend_title="Room Type Focus"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------------------------------------------------
# Data freshness footer
# -----------------------------------------------------------------------------
import datetime

st.caption(
    f"Data source: Airbnb London | Last updated: {datetime.date.today()}"
)