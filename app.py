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
        query = "SELECT * FROM BUS_DETAILS"
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)

        # Formatting time columns
        for col in ['Departure', 'Reach']:
            if col in df.columns and pd.api.types.is_timedelta64_dtype(df[col]):
                df[col] = df[col].apply(lambda td: f"{td.seconds // 3600:02}:{(td.seconds % 3600) // 60:02}:{td.seconds % 60:02}")
        
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
        col1, col2, col3 = st.columns(3)

        # Column 1: Select State
        with col1:
            states = df['state'].unique()
            select_state = st.selectbox("Select State", options=["All"] + list(states))
            if select_state != "All":
                df = df[df['state'] == select_state]

        # Column 2: Select Route
        with col2:
            routes = df["Route_Name"].unique()
            select_route = st.selectbox("Select Route", options=["All"] + list(routes))
            if select_route != "All":
                df = df[df["Route_Name"] == select_route]

        # Column 3: Select Bus Type Category
        with col3:
            # Define categories for bus types
                        # Updated bus type categories
            bus_type_categories = {
                "Seater": [
                    "Electric A/C Seater (2+2)", "A/C Seater / Sleeper (2+1)",
                    "Non AC Seater", "Luxury Seater", "2+2 Push Back","seater"
                ],
                "Sleeper": [
                    "AC Sleeper (2+1)", "Sleeper", "Luxury Sleeper", "Non AC Sleeper","A/C Sleeper",
                ],
                "Semi Sleeper": [
                    "Night Rider (Seater cum Sleeper)", "Deluxe Semi Sleeper","A/C Semi Sleeper",
                    "Super Luxury (Non-AC, 2 + 2 Push Back)", "Seater cum Sleeper","semi sleeper","Non A/c Semi Sleeper"
                ]
            }


           # Function to categorize bus types
            def categorize_bus_type(bus_type):
                for category, types in bus_type_categories.items():
                    if any(t.lower() in bus_type.lower() for t in types):  # Partial match
                        return category
                return "Other"  # Default category for unmatched types

            # Categorize bus types in DataFrame
            df["Bus_Type_Category"] = df["Bus_Type"].apply(categorize_bus_type)

            # Dropdown for bus type selection
            select_bus_category = st.selectbox(
                "Select Bus Type Category",
                options=["All"] + list(bus_type_categories.keys())  # Include all categories
            )

            # Filter DataFrame based on selected bus type category
            if select_bus_category != "All":
                df = df[df["Bus_Type_Category"] == select_bus_category]

            # Drop temporary category column
            df = df.drop(columns=["Bus_Type_Category"], errors="ignore")


        col4, col5, col6 = st.columns(3)

        # Column 4: Departure Time Range
        with col4:
            time_ranges = {
                "12:00am - 6:00am": (0, 6),
                "6:00am - 12:00pm": (6, 12),
                "12:00pm - 6:00pm": (12, 18),
                "6:00pm - 12:00am": (18, 24),
            }
            selected_range = st.selectbox("Select Departure Time Range", options=["All"] + list(time_ranges.keys()))
            if selected_range != "All":
                start_hour, end_hour = time_ranges[selected_range]
                df['Hour'] = df['Departure'].str.split(":").str[0].astype(int)
                if start_hour < end_hour:
                    df = df[(df['Hour'] >= start_hour) & (df['Hour'] < end_hour)]
                else:
                    df = df[(df['Hour'] >= start_hour) | (df['Hour'] < end_hour)]
                df = df.drop(columns=["Hour"])

        # Column 5: Star Ratings
        with col5:
            min_rating, max_rating = st.slider("Select Star Ratings Range", min_value=1, max_value=5, value=(2, 5), step=0.5)
            df = df[(df["Star_Ratings"] >= min_rating) & (df["Star_Ratings"] <= max_rating)]

        # Column 6: AC Type
        with col6:
            # Ensure A/C Type column exists
            if "AC_Type" not in df.columns:
                df["AC_Type"] = df["Bus_Type"].apply(lambda x: "AC" if "A/C" in x.upper() or "AC" in x.upper() else "Non-AC")

            # Add A/C type filter
            select_ac_type = st.selectbox("Select A/C Type", options=["All", "AC", "Non-AC"])

            # Filter the DataFrame based on A/C type
            if select_ac_type != "All":
                df = df[df["AC_Type"] == select_ac_type]

        col7,col8=st.columns(2)
        # Column 7: Price Range
        with col7:
            price_ranges = {
                "Below ₹500": (0, 500),
                "₹500 - ₹1000": (500, 1000),
                "₹1000 - ₹1500": (1000, 1500),
                "Above ₹1500": (1500, float("inf")),
            }
            selected_price_ranges = st.multiselect("Select Price Range", options=price_ranges.keys())
            if selected_price_ranges:
                price_conditions = []
                for range_key in selected_price_ranges:
                    min_val, max_val = price_ranges[range_key]
                    price_conditions.append((df["Price"] >= min_val) & (df["Price"] <= max_val))
                if price_conditions:
                    df = df[pd.concat(price_conditions, axis=1).any(axis=1)]

        # Column 8: Seat Availability
        with col8:
            seat_ranges = {
                "Below 10": (0, 10),
                "above 10": (10, 20),
                "above 20": (20, 30),
                "above 30": (30, 40),
                "above 50": (40, 50)
            }
            selected_seat_range = st.selectbox("Select Seat Availability Range", options=["All"] + list(seat_ranges.keys()))
            if selected_seat_range != "All":
                min_seats, max_seats = seat_ranges[selected_seat_range]
                df = df[(df["Seat_Availability"] >= min_seats) & (df["Seat_Availability"] < max_seats)]

        # Show filtered results
        if st.button("Show Buses"):
            if not df.empty:
                st.subheader("Your Bus Details")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No buses match the selected options.")
    else:
        st.warning("No data available. Please check your database connection or content.")
