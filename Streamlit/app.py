import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats


@st.cache_data
def load_data(nrows):
    data = pd.read_excel("get_around_delay_analysis.xlsx", nrows=nrows)
    return data


data_load_state = st.text("Loading data...")
data = load_data(21310)
data_load_state.text("")

st.title("GETAROUND 🚗")
st.markdown(
    "_Rental car optimization : Do we need to implement a **minimum delay** between two rentals ? and for witch **checkin type** ?_"
)

st.text("")

st.subheader(
    "**How many cars would be impacted with the implementation of a _threshold_ ?**"
)

with st.form("Threshold between rentals (in minutes"):
    minute = st.number_input(
        "Insert time in minuts (with 30min step)", min_value=30, step=30
    )
    submit = st.form_submit_button("submit")

    if submit:
        mask = data["time_delta_with_previous_rental_in_minutes"] <= minute
        data_minute = data[mask]
        # mask = (avg_period_country_sales["Date"] > start_period) & (avg_period_country_sales["Date"] < end_period)
        lost_cars = data_minute["time_delta_with_previous_rental_in_minutes"].count()
        lost_cars_perc = (lost_cars / data.shape[0]) * 100
        st.metric("Average sales during selected period (in cars)", lost_cars)
        st.markdown(f"those {lost_cars} represent {round(lost_cars_perc,2)}% ")

st.text("")
st.markdown("***")
st.text("")

st.subheader(
    "Focus on the kind of car impacted by a late return depending on _checkin type_ "
)
connected = st.selectbox("Chekin type : ", ("mobile", "connect", "all"))
#### Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("**How often a late return impacts the next driver ?...**")

    minutes_delay = data["delay_at_checkout_in_minutes"] > 0
    df_delay = data[minutes_delay]
    df_delay["impacted_by_delay"] = (
        df_delay["delay_at_checkout_in_minutes"]
        - df_delay["time_delta_with_previous_rental_in_minutes"]
    ) > 0
    df_delay["number_of_cars"] = 1

    if connected != "all":
        connected_choice = data["checkin_type"] == connected
        df_delay = df_delay[connected_choice]

        fig = px.pie(df_delay, values="number_of_cars", names="impacted_by_delay", 
                     color_discrete_map={'true':'lightcyan','false':'darkblue'})
        st.plotly_chart(fig, use_container_width=True)

    else:
        fig = px.pie(df_delay, values="number_of_cars", names="impacted_by_delay", 
                     color_discrete_map={'true':'lightcyan','false':'darkblue'})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "**How many problematic cases will be solved depending on the chosen threshold?**"
    )
    threshold = st.selectbox(
        "Select a delay threshold to apply",
        data["time_delta_with_previous_rental_in_minutes"].sort_values().unique(),
    )

    impacted = (
        df_delay["delay_at_checkout_in_minutes"]
        - df_delay["time_delta_with_previous_rental_in_minutes"]
    ) > 0
    impacted_df = df_delay[impacted]
    impacted_df["still_impacted"] = (
        impacted_df["delay_at_checkout_in_minutes"]
        - impacted_df["time_delta_with_previous_rental_in_minutes"]
    ) > threshold
    fig = px.pie(impacted_df, values="number_of_cars", names="still_impacted", 
                 color_discrete_map={'true':'lightcyan','false':'darkblue'})
    st.plotly_chart(fig, use_container_width=True)


with col2:
    st.markdown("**... and how much ?**")
    df_delay_count = pd.DataFrame(
        df_delay[df_delay["impacted_by_delay"] == True]
        .groupby("delay_at_checkout_in_minutes")
        .count()
        .reset_index()
    )
    fig = px.histogram(
        df_delay_count, x="delay_at_checkout_in_minutes", nbins=100
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**how many problematic cases we want to solve ?**")

    perc = st.slider(
        "We can choose in percentage :", 0.0, 1.0, 0.0, step=0.05
    )

    delay = (
        impacted_df["delay_at_checkout_in_minutes"]
        - impacted_df["time_delta_with_previous_rental_in_minutes"]
    )
    threshold = round(delay.quantile(perc), 1)

    st.write(
        "We need to put a threshold at",
        threshold,
        "minutes to resolve",
        perc * 100,
        "% of problemaric late return",
    )
