import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from Home import load_data


st.set_page_config(layout="wide")
st.title("Operations & Logistics")
st.header("Delivery Performance Dashboard")

df = load_data()

st.subheader("Filters")

f1, f2 = st.columns(2)

with f1:
    year_filter = st.multiselect(
        "Select Year",
        sorted(df["order_year"].unique()),
        default=sorted(df["order_year"].unique())
    )

with f2:
    state_filter = st.multiselect(
        "Select State",
        df["customer_state"].unique(),
        default=df["customer_state"].unique()
    )

filtered_df = df[
    (df["order_year"].isin(year_filter)) &
    (df["customer_state"].isin(state_filter))
].copy()


filtered_df["On_Time"] = filtered_df["delivery_days"].apply(
    lambda x: 1 if x <= 5 else 0
)

st.subheader("Delivery Performance KPIs")

k1, k2, k3, k4 = st.columns(4)

avg_delivery = filtered_df["delivery_days"].mean()
on_time_rate = (filtered_df["On_Time"].sum() / len(filtered_df)) * 100
fastest_delivery = filtered_df["delivery_days"].min()
slowest_delivery = filtered_df["delivery_days"].max()

k1.metric("Average Delivery Days", round(avg_delivery, 2))
k2.metric("On-Time Delivery Rate", f"{on_time_rate:.2f}%")
k3.metric("Fastest Delivery", fastest_delivery)
k4.metric("Slowest Delivery", slowest_delivery)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Delivery Days Distribution")
    fig1, ax1 = plt.subplots()
    sns.histplot(filtered_df["delivery_days"], bins=30, ax=ax1)
    ax1.set_xlabel("Delivery Days")
    st.pyplot(fig1)

with col2:
    st.subheader("On-Time vs Delayed Orders")
    on_time_counts = filtered_df["On_Time"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(
        on_time_counts,
        labels=["On-Time", "Delayed"],
        autopct="%1.1f%%"
    )
    st.pyplot(fig2)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Average Delivery Days by State")
    state_avg = filtered_df.groupby("customer_state")["delivery_days"].mean().sort_values()
    st.bar_chart(state_avg)

with col4:
    st.subheader("On-Time Rate by State")
    state_ontime = filtered_df.groupby("customer_state")["On_Time"].mean() * 100
    st.bar_chart(state_ontime)

st.subheader("Delivery Performance Trend Over Years")

yearly_delivery = filtered_df.groupby("order_year")["delivery_days"].mean()
st.line_chart(yearly_delivery)


st.divider()
st.header("Payment Analytics Dashboard")
st.subheader("Payment KPIs")

k1, k2, k3 = st.columns(3)

total_transactions = len(filtered_df)
total_revenue = filtered_df["final_amount_inr"].sum()
most_used_method = filtered_df["payment_method"].value_counts().idxmax()

k1.metric("Total Transactions", total_transactions)
k2.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
k3.metric("Most Used Method", most_used_method)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Payment Method Preference (Transaction Count)")
    payment_counts = filtered_df["payment_method"].value_counts()
    st.bar_chart(payment_counts)

with col2:
    st.subheader("Revenue by Payment Method")
    payment_revenue = filtered_df.groupby("payment_method")["final_amount_inr"].sum()
    st.bar_chart(payment_revenue)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Payment Market Share (%)")
    market_share = (payment_revenue / total_revenue) * 100
    fig, ax = plt.subplots()
    ax.pie(
        market_share,
        labels=market_share.index,
        autopct="%1.1f%%"
    )
    st.pyplot(fig)

with col4:
    st.subheader("Payment Trend Evolution (Yearly Revenue)")

    payment_trend = (
        filtered_df.groupby(["order_year", "payment_method"])
        ["final_amount_inr"]
        .sum()
        .reset_index()
    )

    pivot_payment = payment_trend.pivot(
        index="order_year",
        columns="payment_method",
        values="final_amount_inr"
    )

    st.line_chart(pivot_payment)

st.divider()
st.header("Return & Cancellation Dashboard")

st.subheader("Filters")

f1, f2 = st.columns(2)

with f1:
    year_filter = st.multiselect(
        "Select Year",
        sorted(df["order_year"].unique()),
        default=sorted(df["order_year"].unique()),
        key="delivery_year_filter"
    )

with f2:
    category_filter = st.multiselect(
        "Select Category",
        df["subcategory"].unique(),
        default=df["subcategory"].unique()
    )

filtered_df = df[
    (df["order_year"].isin(year_filter)) &
    (df["subcategory"].isin(category_filter))
].copy()

return_df = filtered_df[filtered_df["return_status"] == "Returned"]

total_orders = len(filtered_df)
total_returns = len(return_df)
return_rate = (total_returns / total_orders) * 100 if total_orders > 0 else 0

revenue_loss = return_df["final_amount_inr"].sum()
st.subheader("📌 Return KPIs")

k1, k2, k3 = st.columns(3)

k1.metric("Total Orders", total_orders)
k2.metric("Return Rate (%)", f"{return_rate:.2f}%")
k3.metric("Revenue Lost (₹)", f"{revenue_loss:,.0f}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Returns by Category")
    return_by_cat = return_df.groupby("subcategory")["transaction_id"].count()
    st.bar_chart(return_by_cat)

with col2:
    st.subheader("Return Trend Over Years")
    yearly_returns = return_df.groupby("order_year")["transaction_id"].count()
    st.line_chart(yearly_returns)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Return Rate by Category (%)")

    category_orders = filtered_df.groupby("subcategory")["transaction_id"].count()
    category_returns = return_df.groupby("subcategory")["transaction_id"].count()

    category_return_rate = (category_returns / category_orders) * 100
    st.bar_chart(category_return_rate)

with col4:
    st.subheader("Return Rate by Rating Group (%)")

    filtered_df["rating_group"] = pd.cut(
        filtered_df["product_rating"],
        bins=[0,2,3,4,5],
        labels=["Low (0-2)", "Medium (2-3)", "High (3-4)", "Very High (4-5)"]
    )

    return_rate = (
        filtered_df.groupby("rating_group")["return_status"]
        .apply(lambda x: (x == "Returned").mean() * 100)
    )

    st.bar_chart(return_rate)