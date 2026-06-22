import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

@st.cache_data
def load_data():
    path = Path(__file__).parent / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")
with st.sidebar:
    st.header("Filters")

    regions = ['All'] + sorted(df['Region'].dropna().unique())
    selected_region = st.selectbox("Region", regions)

    if selected_region == 'All':
        country_options = sorted(df['Country'].unique())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].unique())

    selected_countries = st.multiselect(
        "Countries",
        country_options,
        default=country_options[:3]
    )

    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2000, 1, 1), datetime.date(2022, 1, 1)),
        min_value=datetime.date(int(df['Year'].min()), 1, 1),
        max_value=datetime.date(int(df['Year'].max()), 1, 1),
        format="YYYY-MM-DD"
    )

    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    highlight_top = st.checkbox("Show only top emitter highlighted")

if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()

if len(date_range) != 2:
    st.warning("Select a start AND end date.")
    st.stop()

start_ts = pd.Timestamp(date_range[0])
end_ts = pd.Timestamp(date_range[1])

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) &
    (df['Date'] <= end_ts)
]

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

st.caption(
    f"{len(selected_countries)} countries | "
    f"{selected_region} | "
    f"{date_range[0].strftime('%d %b %Y')} – {date_range[1].strftime('%d %b %Y')} | "
    f"{metric} | "
    f"{len(filtered)} matching records"
)

# KPI row
first_year = filtered['Year'].min()
last_year = filtered['Year'].max()

first_total = filtered[filtered['Year'] == first_year][y_col].sum()
last_total = filtered[filtered['Year'] == last_year][y_col].sum()

pct_change = ((last_total - first_total) / first_total * 100) if first_total != 0 else 0

last_year_data = filtered[filtered['Year'] == last_year]
top_country = last_year_data.loc[last_year_data[y_col].idxmax(), 'Country']

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("Total in Last Year", f"{last_total:,.1f}")
kpi2.metric("Change First → Last Year", f"{pct_change:.1f}%")
kpi3.metric("Highest Emitter", top_country)

col_left, col_right = st.columns([2, 1])

with col_left:
    if highlight_top:
        top_country_range = (
            filtered.groupby('Country')[y_col]
            .sum()
            .idxmax()
        )

        filtered['Highlight'] = filtered['Country'].apply(
            lambda x: top_country_range if x == top_country_range else "Other countries"
        )

        # BBD colour type: grey-and-highlight
        fig_line = px.line(
            filtered,
            x='Year',
            y=y_col,
            color='Highlight',
            line_group='Country',
            title=f"{top_country_range} is the highest emitter in the selected range",
            labels={y_col: y_label}
        )

        end_point = filtered[
            (filtered['Country'] == top_country_range) &
            (filtered['Year'] == filtered[filtered['Country'] == top_country_range]['Year'].max())
        ]

        fig_line.add_annotation(
            x=end_point['Year'].iloc[0],
            y=end_point[y_col].iloc[0],
            text=top_country_range,
            showarrow=True,
            arrowhead=1
        )

    else:
        # BBD colour type: categorical country colours
        fig_line = px.line(
            filtered,
            x='Year',
            y=y_col,
            color='Country',
            title=f"{metric} over time",
            labels={y_col: y_label}
        )

    fig_line.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial')
    )

    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    latest = (
        filtered[filtered['Year'] == last_year]
        .sort_values(y_col, ascending=True)
    )

    # BBD colour type: single highlight colour
    fig_bar = px.bar(
        latest,
        x=y_col,
        y='Country',
        orientation='h',
        title=f"Ranking in {last_year}",
        labels={y_col: y_label}
    )

    fig_bar.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial'),
        xaxis=dict(range=[0, latest[y_col].max() * 1.15])
    )

    fig_bar.update_traces(marker_line_width=0)

    st.plotly_chart(fig_bar, use_container_width=True)