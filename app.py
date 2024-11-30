import streamlit as st
import pymysql
import pandas as pd

# Streamlit Page Configuration
st.set_page_config(page_title="RedBus-app", layout="wide")

# Title
st.title("RedBus Bus Filtering Application")

# Connect to MySQL Database
def sql_connection():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="123456789",  # Update with your password
            database="RED_BUS"    # Update with your database name
        )
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

# Format time columns
def format_time(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%H:%M:%S')
    return df

# Fetch Data from MySQL
def fetch_data():
    conn = sql_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = "SELECT * FROM BUS_DETAIL"  # Your table name
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)

        # Ensure time columns are formatted correctly
        for time_col in ['Departure', 'Reach']:  # Adjust column names as needed
            if time_col in df.columns and pd.api.types.is_timedelta64_dtype(df[time_col]):
                df[time_col] = df[time_col].apply(
                    lambda td: f"{td.seconds//3600:02}:{(td.seconds%3600)//60:02}:{td.seconds%60:02}"
                )

        # Clean and process data
        if "Reach" in df.columns:
            df.rename(columns={"Reach": "Arrival"}, inplace=True)
        if "Route_Name" in df.columns:
            df[["Start_Place", "Reach_Place"]] = df["Route_Name"].str.split(" to ", expand=True)
        if "Bus_Type" in df.columns:
            df["AC_Type"] = df["Bus_Type"].apply(lambda x: "AC" if "A.C" in x.upper() else "Non-AC")

        # Close the connection only if it was successfully created
        if conn:
            conn.close()
            
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        if conn:  # Ensure connection is closed on error
            conn.close()
        return pd.DataFrame()

# Load data
df = fetch_data()

# If data is available, apply filters
if not df.empty:
    col1, col2 = st.columns(2)

    with col1:
        # Route filter
        routes = df["Route_Name"].unique()
        selected_route = st.selectbox("Select Route", options=["All"] + list(routes))
        if selected_route != "All":
            df = df[df["Route_Name"] == selected_route]

    with col2:
        # Bus type filter
        bus_types = df["Bus_Type"].unique()
        selected_bus_types = st.multiselect("Select Bus Type", options=bus_types)
        if selected_bus_types:
            df = df[df["Bus_Type"].isin(selected_bus_types)]

    col3, col4 = st.columns(2)

    with col3:
        # Departure time filter
        departure_times = df["Departure"].unique()
        selected_time = st.selectbox("Select Departure Time", options=["All"] + list(departure_times))
        if selected_time != "All":
            df = df[df["Departure"] == selected_time]

    with col4:
        # Star ratings filter (Modified for simplicity)
        ratings_options = ["Above 2*", "Above 3*", "Above 4*"]
        selected_ratings = st.multiselect("Select Star Ratings", options=ratings_options)
        
        if selected_ratings:
            # We will create a condition for each rating filter selected
            if "Above 2*" in selected_ratings:
                df = df[df["Star_Ratings"] >= 2]
            if "Above 3*" in selected_ratings:
                df = df[df["Star_Ratings"] >= 3]
            if "Above 4*" in selected_ratings:
                df = df[df["Star_Ratings"] >= 4]

    col5, col6 = st.columns(2)

    with col5:
        # AC type filter
        ac_types = df["AC_Type"].unique()
        selected_ac_types = st.multiselect("Select A/C Type", options=ac_types)
        if selected_ac_types:
            df = df[df["AC_Type"].isin(selected_ac_types)]

    with col6:
        # Price range filter
        price_ranges = {
            "Below ₹500": (0, 500),
            "₹500 - ₹1000": (500, 1000),
            "₹1000 - ₹1500": (1000, 1500),
            "Above ₹1500": (1500, float("inf")),
        }
        selected_price_ranges = st.multiselect("Select Price Range", options=price_ranges.keys())
        if selected_price_ranges:
            conditions = None
            for range_key in selected_price_ranges:
                min_val, max_val = price_ranges[range_key]
                condition = (df["Price"] >= min_val) & (df["Price"] <= max_val)
                if conditions is None:
                    conditions = condition
                else:
                    conditions = conditions | condition
            if conditions is not None:
                df = df[conditions]

    # Show results
    if st.button("Show Buses"):
        if not df.empty:
            st.subheader("Filtered Results")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No buses match the selected criteria.")
else:
    st.warning("No data available. Please check your database.")
