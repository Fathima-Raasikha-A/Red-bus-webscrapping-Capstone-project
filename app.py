import streamlit as st  # Importing Streamlit for creating web applications
import pymysql  # Importing pymysql to connect with MySQL databases
import pandas as pd  # Importing pandas for data manipulation

# Streamlit Page
st.set_page_config(page_title="RedBus-app", layout="wide")  # Setting the page title and layout to wide

# Title
st.title("RedBus Bus Filtering Application")  # Displaying the app title

# Function to Connect to MySQL 
def sql_connection():
    
    # connection to the MySQL database
    sql_connection= pymysql.connect(
        host="localhost",  
        user="root",
        password="123456789",  
        database="RED_BUS"  
    )
    return sql_connection

# Fetch Data from MySQL
def fetch_data():
    conn = sql_connection()  #calling database connection
    if not conn:
        # Returning an empty df if the connection fails
        return pd.DataFrame()
    else:
        try:
            # SQL query for the BUS_DETAIL table
            query = "SELECT * FROM BUS_DETAIL"
            cursor = conn.cursor()  # Creating a cursor 
            cursor.execute(query)  # Executing the  query
            columns = [desc[0] for desc in cursor.description]  # Extracting column names
            rows = cursor.fetchall()  # Fetching all rows 
            df = pd.DataFrame(rows, columns=columns)  # Creating a df using extracted details

            # chnaging time columns correctly
            for col in ['Departure', 'Reach']:  # Adjust column names as needed
                if col in df.columns and pd.api.types.is_timedelta64_dtype(df[col]):
                    df[col] = df[col].apply(lambda td: f"{td.seconds//3600:02}:{(td.seconds%3600)//60:02}:{td.seconds%60:02}")

            # Cleaning  the col in df
            if "Reach" in df.columns:
                # Renaming the column Reach to Arrival
                df.rename(columns={"Reach": "Arrival"}, inplace=True)
            if "Route_Name" in df.columns:
                # Splitting Route_Name into Start_Place and Reach_Place
                df[["Start_Place", "Reach_Place"]] = df["Route_Name"].str.split(" to ", expand=True)
            if "Bus_Type" in df.columns:
                # Creating a new column AC_Type 
                df["AC_Type"] = df["Bus_Type"].apply(lambda x: "AC" if "A/C" in x.upper() else "Non-AC")

            # Closing the database connection 
            if conn:
                conn.close()

            return df  # Returning the df
        except Exception as e:
            # Displaying an error message 
            st.error(f"Error fetching data: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()  # Returning the empty df

# Load data
df = fetch_data()  

# If data if present,
if not df.empty:
    # Creating two columnns
    col1, col2 = st.columns(2)

    with col1:
        # Route filter
        routes = df["Route_Name"].unique()  # Getting unique route names
        # Dropdown to select a route
        select_route = st.selectbox("Select Route", options=["All"] + list(routes))
        if select_route != "All":
            # Filtering the df by the selected route
            df = df[df["Route_Name"] == select_route]

    with col2:
        # Bus type filter
        bus_types = df["Bus_Type"].unique()  # Getting unique bus types
        select_bus_types = st.multiselect("Select Bus Type", options=bus_types)# Multiselect to choose one or more bus types
        if select_bus_types:
            df = df[df["Bus_Type"].isin(select_bus_types)]# Filtering the df by selected bus types

    # Creating two more columns 
    col3, col4 = st.columns(2)

    with col3:
        # Departure time filter
        departure_time = df["Departure"].unique()  # Getting unique departure times
        # Dropdown to select a departure time
        selected_time = st.selectbox("Select Departure Time", options=["All"] + list(departure_time))
        if selected_time != "All":
            df = df[df["Departure"] == selected_time]# Filtering the df by the selected departure time

    with col4:
        # Star ratings filter
        ratings_options = ["Above 2*", "Above 3*", "Above 4*"]  #creating rating options
        # Multiselect to choose one or more star ratings
        selected_ratings = st.multiselect("Select Star Ratings", options=ratings_options)

        if selected_ratings:
            # Applying rating filters one by one
            if "Above 2*" in selected_ratings:
                df = df[df["Star_Ratings"] >= 2]
            if "Above 3*" in selected_ratings:
                df = df[df["Star_Ratings"] >= 3]
            if "Above 4*" in selected_ratings:
                df = df[df["Star_Ratings"] >= 4]

    # Creating two more columns for filters
    col5, col6 = st.columns(2)

    with col5:
        # AC type filter
        ac_types = df["AC_Type"].unique()  # Getting unique AC types
        selected_ac_types = st.multiselect("Select A/C Type", options=ac_types)
        if selected_ac_types:
            df = df[df["AC_Type"].isin(selected_ac_types)]# Filtering the df by selected AC types

    with col6:
        # Price range filter
        price_ranges = {
            "Below ₹500": (0, 500),
            "₹500 - ₹1000": (500, 1000),
            "₹1000 - ₹1500": (1000, 1500),
            "Above ₹1500": (1500, float("inf")),
        }
        # Multiselect to choose one or more price ranges
        selected_price_ranges = st.multiselect("Select Price Range", options=price_ranges.keys())
        if selected_price_ranges:
            # Applying price range filters one by one
            conditions = None
            for range in selected_price_ranges:
                min_val, max_val = price_ranges[range]
                condition = (df["Price"] >= min_val) & (df["Price"] <= max_val)
                if conditions is None:
                    conditions = condition
                else:
                    conditions = conditions | condition
            if conditions is not None:
                df = df[conditions]

    # Show results
    if st.button(label ="Show Buses"):
        if not df.empty:
            # Displaying the filtered results in a table
            st.subheader("Your Bus Details")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No buses match the selected options")
else:
    # Warning if no data is available
    st.warning("No data available")