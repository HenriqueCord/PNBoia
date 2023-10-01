import pandas as pd
import plotly.express as px
import streamlit as st
import datetime

BOIA_01 = "/media/hcordeiro/Seagate Expansion Drive/datasets/brasil-pnboia/boia-bacia-de-santos-bmo-br-01/metocean_bacia-de-santos-bm01_qualificados_publicos.csv"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

col_mapping = {
    "date_time": "dt",
    "latitude": "latitude",
    "longitude": "longitude",
    "wspd1": "wind_speed1",
    "flag_wspd1": "flag_wspd1",
    "wdir1": "wind_dir1",
    "flag_wdir1": "flag_wdir1",
}

def convert_column_to_datetime(df, column_name, date_format):
    """
    Convert a specified column in a DataFrame to datetime using the provided schema.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column_name (str): The name of the column to convert.
        distro_schema (namedtuple): The schema object containing date format information.

    Returns:
        pd.DataFrame: The DataFrame with the specified column converted to datetime.
    """
    try:
        # Convert the specified column to datetime
        df[column_name] = pd.to_datetime(
            df[column_name], format=date_format
        )
        return df
    except KeyError:
        print(f"Error: Column '{column_name}' not found in the DataFrame.")
        return None


if __name__ == "__main__":

    # read, process and slice data
    df = pd.read_csv(BOIA_01)
    df_slice = df[col_mapping.keys()].rename(columns=col_mapping)
    df_windspeed = df_slice.copy()
    df_windspeed = convert_column_to_datetime(df_windspeed, column_name="dt", date_format=DATE_FORMAT)
    df_windspeed = df_windspeed.set_index('dt')

    # get plotting slice:
    df_plot = df_windspeed[
        (df_windspeed['wind_speed1'] >= 0) &
        (df_windspeed['flag_wspd1'] == 0) &
        (df_windspeed['flag_wdir1'] == 0)
    ]


    # Streamlit app
    st.title("Wind Data Visualization")

    # get min and max dt
    default_time = datetime.time(0, 0)
    
    min_dt = df_plot.index.min().date()
    max_dt = df_plot.index.max().date()
    

    # Create a range slider to select the time range
    # Create a slider to select a range of time
    start_date, end_date = st.slider(
        "Select a Date Range", 
        min_value=min_dt, 
        max_value=max_dt, 
        value=(min_dt, max_dt)
        )

    # start_date = st.date_input(
    #     "Select Start Date", 
    #     min_value=min_dt, 
    #     max_value=max_dt,
    #     value=min_dt
    #     )
    start_date = datetime.datetime.combine(start_date, default_time)

    # end_date = st.date_input(
    #     "Select End Date", 
    #     min_value=min_dt, 
    #     max_value=max_dt,
    #     value=max_dt
    #     )
    end_date = datetime.datetime.combine(end_date, default_time)


    # Create a polar scatter plot
    fig = px.scatter_polar(df_plot, r='wind_speed1', theta='wind_dir1', title="Wind Speed and Direction")
    fig.update_traces(marker=dict(size=5, opacity=0.5))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(showticklabels=False, ticks=''),
            angularaxis=dict(showticklabels=True, tickvals=[0, 45, 90, 135, 180, 225, 270, 315]),
        ),
        width=800,
        height=800,
    )

    # Filter the DataFrame based on the selected date range
    highlighted_data = (df_plot.index >= start_date) & (df_plot.index <= end_date)

    # Update the color of the markers based on the mask
    fig.update_traces(
        marker=dict(color=[
            'red' if highlighted else 
            'blue' 
            for highlighted in highlighted_data]
            )
        )

    # Display the plot
    st.plotly_chart(fig)