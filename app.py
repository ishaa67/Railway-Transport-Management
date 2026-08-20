import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Railway Booking Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data():
    df = pd.read_excel("Transport_Management_Railway_Booking_1500x20-3.xlsx")

    df["Journey_Date"] = pd.to_datetime(df["Journey_Date"], errors="coerce")

    df["Ticket_Fare"] = pd.to_numeric(
        df["Ticket_Fare"], errors="coerce"
    )

    df["Distance_KM"] = pd.to_numeric(
        df["Distance_KM"], errors="coerce"
    )

    df["Age"] = pd.to_numeric(
        df["Age"], errors="coerce"
    )

    return df


data = load_data()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.title("Railway Booking Management")

min_date = data["Journey_Date"].min().date()
max_date = data["Journey_Date"].max().date()

date_range = st.sidebar.date_input(
    "Choose Journey Date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_range"
)

train_type = st.sidebar.multiselect(
    "Train Type",
    data["Train_Type"].dropna().unique(),
    key="train_type"
)

travel_class = st.sidebar.multiselect(
    "Travel Class",
    data["Travel_Class"].dropna().unique(),
    key="travel_class"
)

booking_status = st.sidebar.multiselect(
    "Booking Status",
    data["Booking_Status"].dropna().unique(),
    key="booking_status"
)

source = st.sidebar.multiselect(
    "Source",
    data["Source"].dropna().unique(),
    key="source"
)

destination = st.sidebar.multiselect(
    "Destination",
    data["Destination"].dropna().unique(),
    key="destination"
)


# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------

if len(date_range) == 2:

    filtered_df = data[
        (data["Journey_Date"].dt.date >= date_range[0]) &
        (data["Journey_Date"].dt.date <= date_range[1])
    ]

else:

    filtered_df = data[
        data["Journey_Date"].dt.date == date_range[0]
    ]


if train_type:
    filtered_df = filtered_df[
        filtered_df["Train_Type"].isin(train_type)
    ]

if travel_class:
    filtered_df = filtered_df[
        filtered_df["Travel_Class"].isin(travel_class)
    ]

if booking_status:
    filtered_df = filtered_df[
        filtered_df["Booking_Status"].isin(booking_status)
    ]

if source:
    filtered_df = filtered_df[
        filtered_df["Source"].isin(source)
    ]

if destination:
    filtered_df = filtered_df[
        filtered_df["Destination"].isin(destination)
    ]


st.sidebar.divider()
st.sidebar.caption(
    "Railway Transport Management\n"
    "Railway Booking Analysis Dashboard"
)


# ---------------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------------

st.title("Railway Transport Management Dashboard")
st.write("Railway Booking and Passenger Analysis")


# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------

total_bookings = filtered_df["Booking_ID"].nunique()

confirmed_bookings = (
    filtered_df["Booking_Status"]
    .eq("Confirmed")
    .sum()
)

cancelled_bookings = (
    filtered_df["Cancellation_Status"]
    .eq("Yes")
    .sum()
)

total_revenue = filtered_df["Ticket_Fare"].sum()

average_fare = filtered_df["Ticket_Fare"].mean()

total_distance = filtered_df["Distance_KM"].sum()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Total Bookings",
    value=f"{total_bookings:,}"
)

col2.metric(
    label="Confirmed Bookings",
    value=f"{confirmed_bookings:,}"
)

col3.metric(
    label="Cancelled Bookings",
    value=f"{cancelled_bookings:,}"
)

col4.metric(
    label="Total Revenue",
    value=f"₹{total_revenue:,.2f}"
)


col1, col2, col3 = st.columns(3)

col1.metric(
    label="Average Ticket Fare",
    value=f"₹{average_fare:,.2f}"
    if not np.isnan(average_fare)
    else "₹0.00"
)

col2.metric(
    label="Total Distance",
    value=f"{total_distance:,.0f} KM"
)

col3.metric(
    label="Unique Trains",
    value=f"{filtered_df['Train_ID'].nunique():,}"
)


st.divider()


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    ["Dashboard", "Insights", "Raw Data"]
)


# =========================================================
# DASHBOARD TAB
# =========================================================

with tab1:

    if filtered_df.empty:

        st.warning("No data available for the selected filters.")

    else:

        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # TOP TRAINS
        # -------------------------------------------------

        with col1:

            st.subheader(
                "Top 10 Trains by Bookings",
                text_alignment="center"
            )

            top_trains = (
                filtered_df
                .groupby("Train_Name")["Booking_ID"]
                .count()
                .sort_values(ascending=False)
                .head(10)
            )

            fig, ax = plt.subplots(figsize=(7, 4))

            ax.barh(
                top_trains.index,
                top_trains.values
            )

            ax.invert_yaxis()

            ax.set_xlabel("Number of Bookings")
            ax.set_ylabel("Train")

            plt.tight_layout()

            st.pyplot(fig)

        # -------------------------------------------------
        # ROUTE ANALYSIS
        # -------------------------------------------------

        with col2:

            st.subheader(
                "Top 10 Routes",
                text_alignment="center"
            )

            filtered_df["Route"] = (
                filtered_df["Source"]
                + " → "
                + filtered_df["Destination"]
            )

            top_routes = (
                filtered_df
                .groupby("Route")["Booking_ID"]
                .count()
                .sort_values(ascending=False)
                .head(10)
            )

            fig, ax = plt.subplots(figsize=(7, 4))

            ax.bar(
                top_routes.index,
                top_routes.values
            )

            ax.set_xlabel("Route")
            ax.set_ylabel("Bookings")

            plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            st.pyplot(fig)


        st.divider()


        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # TRAVEL CLASS
        # -------------------------------------------------

        with col1:

            st.subheader(
                "Bookings by Travel Class",
                text_alignment="center"
            )

            class_data = (
                filtered_df["Travel_Class"]
                .value_counts()
            )

            fig, ax = plt.subplots(figsize=(6, 4))

            ax.pie(
                class_data.values,
                labels=class_data.index,
                autopct="%1.1f%%",
                wedgeprops={"width": 0.7}
            )

            plt.title("Travel Class Distribution")

            st.pyplot(fig)


        # -------------------------------------------------
        # BOOKING STATUS
        # -------------------------------------------------

        with col2:

            st.subheader(
                "Booking Status",
                text_alignment="center"
            )

            status_data = (
                filtered_df["Booking_Status"]
                .value_counts()
            )

            fig, ax = plt.subplots(figsize=(6, 4))

            ax.bar(
                status_data.index,
                status_data.values
            )

            ax.set_xlabel("Booking Status")
            ax.set_ylabel("Number of Bookings")

            plt.tight_layout()

            st.pyplot(fig)


        st.divider()


        col1, col2 = st.columns(2)

        # -------------------------------------------------
        # REVENUE BY TRAIN TYPE
        # -------------------------------------------------

        with col1:

            st.subheader(
                "Revenue by Train Type",
                text_alignment="center"
            )

            revenue_train = (
                filtered_df
                .groupby("Train_Type")["Ticket_Fare"]
                .sum()
                .sort_values(ascending=False)
            )

            fig, ax = plt.subplots(figsize=(6, 4))

            ax.bar(
                revenue_train.index,
                revenue_train.values
            )

            ax.set_xlabel("Train Type")
            ax.set_ylabel("Revenue")

            plt.xticks(rotation=30)

            plt.tight_layout()

            st.pyplot(fig)


        # -------------------------------------------------
        # PAYMENT METHOD
        # -------------------------------------------------

        with col2:

            st.subheader(
                "Payment Method",
                text_alignment="center"
            )

            payment_data = (
                filtered_df["Payment_Method"]
                .value_counts()
            )

            fig, ax = plt.subplots(figsize=(6, 4))

            ax.pie(
                payment_data.values,
                labels=payment_data.index,
                autopct="%1.1f%%"
            )

            plt.title("Payment Method Distribution")

            st.pyplot(fig)


        st.divider()


        # -------------------------------------------------
        # JOURNEY TREND
        # -------------------------------------------------

        st.subheader(
            "Daily Booking Trend",
            text_alignment="center"
        )

        daily_bookings = (
            filtered_df
            .groupby("Journey_Date")["Booking_ID"]
            .count()
        )

        fig, ax = plt.subplots(figsize=(12, 4))

        ax.plot(
            daily_bookings.index,
            daily_bookings.values,
            marker="o",
            markersize=3
        )

        ax.set_xlabel("Journey Date")
        ax.set_ylabel("Number of Bookings")

        plt.xticks(rotation=45)

        plt.tight_layout()

        st.pyplot(fig)


