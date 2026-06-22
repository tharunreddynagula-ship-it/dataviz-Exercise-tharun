import streamlit as st
import pandas as pd
import plotly.express as px

# STEP 1 — Load data
df = pd.read_csv("world_happiness_2023 (1).csv")

df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Country name": "Country",
    "Regional indicator": "Region",
    "Ladder score": "Score",
    "Logged GDP per capita": "GDP",
    "Social support": "Social_Support",
    "Healthy life expectancy": "Life_Expectancy",
    "Freedom to make life choices": "Freedom",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Corruption"
})

# STEP 2 — Page setup
st.set_page_config(page_title="World Happiness Dashboard", layout="wide")

st.title("🌍 World Happiness Dashboard")
st.caption("World Happiness Report 2023")

# STEP 3 — Sidebar filters
with st.sidebar:
    st.header("Filters")
    regions = ["All"] + sorted(df["Region"].unique().tolist())
    selected_region = st.selectbox("Select Region", regions)
    top_n = st.slider("Top N Countries", 5, 25, 15)

filtered = df if selected_region == "All" else df[df["Region"] == selected_region]

# STEP 4 — KPI metrics
col1, col2, col3 = st.columns(3)

col1.metric("Countries", len(filtered))
col2.metric("Average Score", round(filtered["Score"].mean(), 2))
col3.metric("Happiest Country", filtered.loc[filtered["Score"].idxmax(), "Country"])

st.divider()

# STEP 5 — Main charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top Countries by Happiness Score")

    top = filtered.nlargest(top_n, "Score").sort_values("Score")

    fig1 = px.bar(
        top,
        x="Score",
        y="Country",
        orientation="h",
        color="Score",
        color_continuous_scale="Blues",
        title="Top Happiest Countries"
    )

    fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("GDP vs Happiness Score")

    fig2 = px.scatter(
        filtered,
        x="GDP",
        y="Score",
        hover_name="Country",
        color="Region",
        title="Relationship Between GDP and Happiness"
    )

    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# STEP 6 — Diverging colour scale chart
st.subheader("Freedom to Make Life Choices: Above and Below Global Average")

mid = df["Freedom"].mean()

fig3 = px.bar(
    filtered.sort_values("Freedom"),
    x="Freedom",
    y="Country",
    orientation="h",
    color="Freedom",
    color_continuous_scale="RdBu",
    color_continuous_midpoint=mid,
    title="Freedom Values Compared to the Global Average"
)

fig3.add_vline(
    x=mid,
    line_width=2,
    line_dash="dash",
    annotation_text="Global Average",
    annotation_position="top"
)

fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(fig3, use_container_width=True)