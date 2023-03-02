import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data(nrows):
    data = pd.read_excel('get_around_delay_analysis.xlsx', nrows=nrows)
    return data

data_load_state = st.text('Loading data...')
data = load_data(21310)
data_load_state.text("")

st.title('GETAROUND 🚗')
st.markdown('_Rental car optimization : Need we to implemant **minimum delay** between two rentals ? and for witch **checkin type** ?_') 

st.text("")

st.subheader("**How many cars would be impacted with implementation of _threshold_ ?**")

with st.form("Threshold between rents (in minuts"):
    Minute = st.number_input('Insert time in minuts', min_value=30,step=30)
    submit = st.form_submit_button("submit")

    if submit:
            mask = data['time_delta_with_previous_rental_in_minutes'] <= Minute
            data_minute = data[mask]
            #mask = (avg_period_country_sales["Date"] > start_period) & (avg_period_country_sales["Date"] < end_period)
            lost_cars = data_minute['time_delta_with_previous_rental_in_minutes'].count()
            lost_cars_perc = (lost_cars/data.shape[0])*100
            st.metric("Average sales during selected period (in cars)", lost_cars)
            st.markdown(f"those {lost_cars} represent {round(lost_cars_perc,2)}% ")

st.text("")
st.markdown("***")
st.text("")

st.subheader('Focus on impacted car by delay depending of _checkin type_ ')
connected = st.selectbox("Chekin type : ", ('mobile', 'connect', 'all'))
#### Create two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("**How often the chekout delay impact the next driver ?**")

    minutes_delay = data['delay_at_checkout_in_minutes'] > 0
    df_delay = data[minutes_delay]
    df_delay['impacted_by_delay'] = (df_delay['delay_at_checkout_in_minutes'] - df_delay['time_delta_with_previous_rental_in_minutes']) > 0
    df_delay['count'] = 1

    if connected != 'all' :
        connected_choice = data['checkin_type'] == connected
        df_delay = df_delay[connected_choice]
    
        fig = px.pie(df_delay, values='count', names='impacted_by_delay')
        st.plotly_chart(fig, use_container_width=True)

    else : 
        fig = px.pie(df_delay, values='count', names='impacted_by_delay')
        st.plotly_chart(fig, use_container_width=True)


with col2:
    st.markdown("**How many problematic cases will it solve depending on the chosen threshold and scope?**")
    threshold = st.selectbox("Select a delay threshold to applicate",data['time_delta_with_previous_rental_in_minutes'].sort_values().unique())

    impacted = (df_delay['delay_at_checkout_in_minutes'] - df_delay['time_delta_with_previous_rental_in_minutes']) > 0
    impacted_df = df_delay[impacted]
    impacted_df['still_impacted'] = (impacted_df['delay_at_checkout_in_minutes'] - impacted_df['time_delta_with_previous_rental_in_minutes']) > threshold
    fig = px.pie(impacted_df, values='count', names='still_impacted')
    st.plotly_chart(fig, use_container_width=True)

# if st.button("I hope, it's help !"):
#     st.balloons()



# lancer l'app : docker build . -t stream ET docker run -it -v "$(pwd):/home/app" -e PORT=80 -p 4000:80 stream
