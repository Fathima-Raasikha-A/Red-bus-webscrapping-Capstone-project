import streamlit as st
import pymysql
import pandas as pd

# Streamlit Page Configuration
st.set_page_config(page_title="RedBus-app", layout="wide")

# Title
st.title("RedBus Bus Filtering Application")

# Function to Connect to MySQL
def sql_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="RED_BUS"
        )
        return connection
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Fetch Data from MySQL
def fetch_data():
    conn = sql_connection()
    if not conn:
        st.error("Database connection failed!")
        return pd.DataFrame()
    try:
        query = "SELECT * FROM BUS_DETAIL"
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)
         # chnaging time columns correctly
        for col in ['Departure', 'Reach']: 
            if col in df.columns and pd.api.types.is_timedelta64_dtype(df[col]):
                df[col] = df[col].apply(lambda td: f"{td.seconds//3600:02}:{(td.seconds%3600)//60:02}:{td.seconds%60:02}")
 
        if "Reach" in df.columns:
            df.rename(columns={"Reach": "Arrival"}, inplace=True)
        if "Route_Name" in df.columns:
            df[["Start_Place", "Reach_Place"]] = df["Route_Name"].str.split(" to ", expand=True)
        if "Bus_Type" in df.columns:
            df["AC_Type"] = df["Bus_Type"].apply(lambda x: "AC" if "A/C" in x.upper() else "Non-AC")

        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Sidebar Menu
st.sidebar.title("Home")
menu_option = st.sidebar.radio("Main-menu", ["Home Page", "Filtering Page"])

# Home Page
if menu_option == "Home Page":
    st.title("Hey there..!")
    st.subheader("Happy Journey!")
    st.subheader("Click on the 'Filtering Page' to filter your data!")

# Filtering Page
elif menu_option == "Filtering Page":
    df = fetch_data()

    if not df.empty:
        # Filtering logic
        col1, col2 = st.columns(2)

        with col1:
            routes = df["Route_Name"].dropna().unique()
            select_route = st.selectbox("Select Route", options=["All"] + list(routes))
            if select_route != "All":
                df = df[df["Route_Name"] == select_route]

        with col2:
            bus_types = df["Bus_Type"].dropna().unique()
            select_bus_types = st.multiselect("Select Bus Type", options=bus_types)
            if select_bus_types:
                df = df[df["Bus_Type"].isin(select_bus_types)]

        col3, col4 = st.columns(2)

        with col3:
            departure_time = df["Departure"].dropna().unique()
            selected_time = st.selectbox("Select Departure Time", options=["All"] + list(departure_time))
            if selected_time != "All":
                df = df[df["Departure"] == selected_time]

        with col4:
            ratings_options = ["Above 2*", "Above 3*", "Above 4*"]
            selected_ratings = st.multiselect("Select Star Ratings", options=ratings_options)
            if selected_ratings:
                for rating in selected_ratings:
                    if rating == "Above 2*":
                        df = df[df["Star_Ratings"] >= 2]
                    elif rating == "Above 3*":
                        df = df[df["Star_Ratings"] >= 3]
                    elif rating == "Above 4*":
                        df = df[df["Star_Ratings"] >= 4]

        col5, col6 = st.columns(2)

        with col5:
            ac_types = df["AC_Type"].dropna().unique()
            selected_ac_types = st.multiselect("Select A/C Type", options=ac_types)
            if selected_ac_types:
                df = df[df["AC_Type"].isin(selected_ac_types)]

        with col6:
            price_ranges = {
                "Below ₹500": (0, 500),
                "₹500 - ₹1000": (500, 1000),
                "₹1000 - ₹1500": (1000, 1500),
                "Above ₹1500": (1500, float("inf")),
            }
            selected_price_ranges = st.multiselect("Select Price Range", options=price_ranges.keys())
            if selected_price_ranges:
                # Simplified price range filtering
                price_conditions = []
                for range_key in selected_price_ranges:
                    min_val, max_val = price_ranges[range_key]
                    price_conditions.append((df["Price"] >= min_val) & (df["Price"] <= max_val))
                if price_conditions:
                    df = df[pd.concat(price_conditions, axis=1).any(axis=1)]

        # Show filtered results
        if st.button("Show Buses"):
            if not df.empty:
                st.subheader("Your Bus Details")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No buses match the selected options.")
    else:
        st.warning("No data available. Please check your database connection or content.")
