import streamlit as st
import pandas as pd
from Home import load_data

st.set_page_config(layout="wide")
st.title("📊 Executive Dashboard")

df = load_data()

st.header("1️⃣ Executive Summary")

total_revenue = df["final_amount_inr"].sum()
active_customers = df["customer_id"].nunique()
total_orders = df["transaction_id"].count()
avg_order_value = df["final_amount_inr"].mean()

yearly = df.groupby("order_year")["final_amount_inr"].sum().reset_index()
yearly["yoy_growth"] = yearly["final_amount_inr"].pct_change() * 100

latest_year = yearly.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{latest_year['final_amount_inr']:,.0f}")
col2.metric("Active Customers", f"{active_customers:,}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Avg Order Value", f"₹{avg_order_value:,.0f}")

col5, col6, col7 = st.columns(3)

with col5:
    st.subheader("Revenue Trend")
    st.line_chart(yearly.set_index("order_year")["final_amount_inr"])

with col6:
    top_subcategories = (
        df.groupby("subcategory")["final_amount_inr"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.subheader("Top 5 Subcategories")
    st.bar_chart(top_subcategories)
with col7:
    st.subheader("YoY Growth (%)") 
    st.line_chart(yearly.set_index("order_year")["yoy_growth"])

st.divider()

st.header("📈 Real-time business performance")

monthly_revenue = df.groupby(["order_year", "order_month"])["final_amount_inr"].sum().reset_index()

latest = monthly_revenue.iloc[-1]
previous = monthly_revenue.iloc[-2]

current_revenue = latest["final_amount_inr"]
previous_revenue = previous["final_amount_inr"]

mom_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100

col1, col2, col3 = st.columns(3)

col1.metric("Current Month Revenue", f"₹{current_revenue:,.0f}")
col2.metric("Previous Month Revenue", f"₹{previous_revenue:,.0f}")
col3.metric("MoM Growth (%)", f"{mom_growth:.2f}%")

if mom_growth < 0:
    st.error("⚠ Revenue decreased compared to last month")
else:
    st.success("✅ Revenue is growing")

monthly_revenue["year_month"] = monthly_revenue["order_year"].astype(str) + "-" + monthly_revenue["order_month"].astype(str)

st.subheader("Monthly Revenue Trend")
st.line_chart(monthly_revenue.set_index("year_month")["final_amount_inr"])

st.divider()

st.header("3️⃣ Strategic Overview")

brand_revenue = df.groupby("brand")["final_amount_inr"].sum()
brand_share = (brand_revenue / brand_revenue.sum()) * 100
top_brands = brand_share.sort_values(ascending=False).head(10)

state_revenue = df.groupby("customer_state")["final_amount_inr"].sum()
city_revenue = df.groupby("customer_city")["final_amount_inr"].sum().head(10)

return_rate = (df["return_status"] == "Returned").mean() * 100
avg_rating = df["customer_rating"].mean()

col11, col12 = st.columns(2)
col11.metric("Return Rate", f"{return_rate:.2f}%")
col12.metric("Avg Customer Rating", f"{avg_rating:.2f}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Brand Market Share (%)")
    st.bar_chart(top_brands)

with col2:
    st.subheader("Revenue by State")
    st.bar_chart(state_revenue)

st.subheader("Top 10 Revenue by City")
st.bar_chart(city_revenue)

st.divider()

st.header("4️⃣ Financial Performance Dashboard")

df["estimated_cost"] = df["original_price_inr"] * 0.7
df["profit"] = df["final_amount_inr"] - df["estimated_cost"]
df["profit_margin"] = (df["profit"] / df["final_amount_inr"]) * 100
total_profit = df["profit"].sum()
avg_margin = df["profit_margin"].mean()
total_discount = (df["original_price_inr"] - df["discounted_price_inr"]).sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Profit (Est.)", f"₹{total_profit:,.0f}")
col2.metric("Average Profit Margin", f"{avg_margin:.2f}%")
col3.metric("Total Discount Given", f"₹{total_discount:,.0f}")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Revenue by Subcategory")
    st.bar_chart(
        df.groupby("subcategory")["final_amount_inr"].sum()
    )

with col5:
    st.subheader("Profit Margin by Subcategory")
    st.bar_chart(
        df.groupby("subcategory")["profit_margin"].mean()
    )

st.divider()

st.header("5️⃣ Growth Analytics Dashboard")

customer_growth = df.groupby("order_year")["customer_id"].nunique()
product_growth = df.groupby("order_year")["product_id"].nunique()
prime_growth = df.groupby("order_year")["is_prime_member"].mean() * 100

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customer Growth")
    st.line_chart(customer_growth)

with col2:
    st.subheader("Product Growth")
    st.line_chart(product_growth)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Prime Member Adoption (%)")
    st.line_chart(prime_growth)

with col2:
    festival_revenue = (
        df[df["is_festival_sale"] == 1]
        .groupby("festival_name")["final_amount_inr"]
        .sum()
    )

    st.subheader("Festival Sales Performance")
    st.bar_chart(festival_revenue)