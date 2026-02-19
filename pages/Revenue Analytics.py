import streamlit as st
from Home import load_data
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

st.set_page_config(layout="wide")
df = load_data()

st.header("📊 Revenue trend analysis dashboard")

time_option = st.selectbox(
    "select time period",
    ["yearly", "quarterly", "monthly"]
)

if time_option == "yearly":
    revenue_df = df.groupby("order_year")["final_amount_inr"].sum().reset_index()
    revenue_df.columns = ["period", "revenue"]

elif time_option == "quarterly":
    revenue_df = df.groupby(["order_year", "order_quarter"])["final_amount_inr"].sum().reset_index()
    revenue_df["period"] = revenue_df["order_year"].astype(str) + "-Q" + revenue_df["order_quarter"].astype(str)
    revenue_df = revenue_df[["period", "final_amount_inr"]]
    revenue_df.columns = ["period", "revenue"]

else:  # monthly
    revenue_df = df.groupby(["order_year", "order_month"])["final_amount_inr"].sum().reset_index()
    revenue_df["period"] = revenue_df["order_year"].astype(str) + "-" + revenue_df["order_month"].astype(str)
    revenue_df = revenue_df[["period", "final_amount_inr"]]
    revenue_df.columns = ["period", "revenue"]

revenue_df["growth_percent"] = revenue_df["revenue"].pct_change() * 100

col1, col2 = st.columns(2)
with col1:
    st.subheader("Revenue trend")
    st.line_chart(
        revenue_df.set_index("period")["revenue"]
    )

with col2:
    st.subheader("Growth rate (%)")
    st.line_chart(
        revenue_df.set_index("period")["growth_percent"]
    )

st.subheader("Seasonal revenue pattern (monthly view)")
seasonal_df = df.groupby(["order_year", "order_month"])["final_amount_inr"].sum().unstack()
st.dataframe(seasonal_df)

st.subheader("Simple revenue forecast (moving average)")
revenue_df["forecast"] = revenue_df["revenue"].rolling(window=3).mean()
st.line_chart(
    revenue_df.set_index("period")[["revenue", "forecast"]]
)

st.divider()

st.header("📊 Subcategory performance dashboard")

sub_list = df["subcategory"].unique()

selected_sub = st.selectbox(
    "select subcategory for drop-down",
    ["All"] + list(sub_list)
)

sub_revenue = df.groupby("subcategory")["final_amount_inr"].sum().sort_values(ascending=False)
total_revenue = sub_revenue.sum()
market_share = (sub_revenue / total_revenue) * 100

col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue contribution by subcategory")
    st.bar_chart(sub_revenue)
with col4:
    st.subheader("Market share (%)")
    fig, ax = plt.subplots(figsize=(6,3))
    ax.pie(
        market_share,
        labels=market_share.index,
        autopct="%1.1f%%"
    )
    ax.set_title("Market share (%)")
    st.pyplot(fig)

col9, col10 = st.columns(2)

with col9:
    st.subheader("Subcategory growth trend")
    sub_yearly = df.groupby(["order_year", "subcategory"])["final_amount_inr"].sum().reset_index()
    if selected_sub != "All":
        sub_yearly = sub_yearly[sub_yearly["subcategory"] == selected_sub]

    pivot_df = sub_yearly.pivot(
        index="order_year",
        columns="subcategory",
        values="final_amount_inr"
    )
    st.line_chart(pivot_df)

with col10:
    if selected_sub != "All":
        st.subheader("Brand drop-down")
        brand_revenue = df[df["subcategory"] == selected_sub].groupby("brand")["final_amount_inr"].sum().sort_values(ascending=False)
        st.bar_chart(brand_revenue)

st.divider()
st.header("🌍 Geographic revenue analysis dashboard")

state_revenue = df.groupby("customer_state")["final_amount_inr"].sum().sort_values(ascending=False)
top_cities = df.groupby("customer_city")["final_amount_inr"].sum().sort_values(ascending=False).head(10)

col5,col6 = st.columns(2)
with col5:
    st.subheader("State-wise revenue distribution")
    st.bar_chart(state_revenue)
with col6:
    st.subheader("Top 10 cities by revenue")
    st.bar_chart(top_cities)

col7, col8 = st.columns(2)
with col7:
    st.subheader("State growth trend (select state)")

    state_list = df["customer_state"].unique()
    selected_state = st.selectbox("select state", state_list)
    state_yearly = (
        df[df["customer_state"] == selected_state]
        .groupby("order_year")["final_amount_inr"]
        .sum()
        .reset_index()
    )
    st.line_chart(state_yearly.set_index("order_year"))

with col8:
    st.subheader("Tier-wise revenue growth trend")

    tier_yearly = df.groupby(["order_year", "customer_tier"])["final_amount_inr"].sum().reset_index()
    pivot_tier = tier_yearly.pivot(
        index="order_year",
        columns="customer_tier",
        values="final_amount_inr"
    )
    st.line_chart(pivot_tier)

st.divider()
st.header("🎉 Festival sales analytics dashboard")

festival_df = df[df["is_festival_sale"] == 1]
festival_revenue = festival_df["final_amount_inr"].sum()
festival_orders = festival_df["transaction_id"].count()
festival_customers = festival_df["customer_id"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("festival revenue", f"₹{festival_revenue:,.0f}")
col2.metric("festival orders", f"{festival_orders:,}")
col3.metric("festival customers", f"{festival_customers:,}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by festival")
    festival_revenue_by_name = (
        festival_df.groupby("festival_name")["final_amount_inr"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(festival_revenue_by_name)

with col2:
    st.subheader("Festival revenue trend (yearly)")

    festival_yearly = (
        festival_df.groupby("order_year")["final_amount_inr"]
        .sum()
        .reset_index()
    )
    st.line_chart(festival_yearly.set_index("order_year"))

st.subheader("Seasonal revenue pattern (festival months)")

seasonal_pattern = (
    festival_df.groupby("order_month")["final_amount_inr"]
    .sum()
)

st.line_chart(seasonal_pattern)

st.divider()
st.subheader("🔎 Price Optimization Dashboard")

f1, f2 = st.columns(2)

with f1:
    category_filter = st.multiselect(
        "Select Category",
        options=df["subcategory"].unique(),
        default=df["subcategory"].unique()
    )

with f2:
    year_filter = st.multiselect(
        "Select Year",
        options=sorted(df["order_year"].unique()),
        default=sorted(df["order_year"].unique())
    )

filtered_df = df[(df["subcategory"].isin(category_filter)) &(df["order_year"].isin(year_filter))]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue",f"₹ {round(filtered_df['final_amount_inr'].sum(),2)}")
k2.metric("Avg Selling Price",f"₹ {round(filtered_df['discounted_price_inr'].mean(),2)}")
k3.metric("Avg Discount %",f"{round(filtered_df['discount_percent'].mean(),2)} %")
k4.metric("Total Quantity Sold", round(filtered_df['quantity'].sum(),2))

st.subheader("Pricing & Discount Analysis")
col1, col2 = st.columns(2)
with col1:
    fig1, ax1 = plt.subplots()
    sns.scatterplot(
        data=filtered_df,
        x="discounted_price_inr",
        y="quantity",
        ax=ax1
    )
    ax1.set_title("Price vs Quantity Sold")
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots()
    sns.scatterplot(
        data=filtered_df,
        x="discount_percent",
        y="quantity",
        ax=ax2
    )
    ax2.set_title("Discount % vs Quantity")
    st.pyplot(fig2)


col3, col4 = st.columns(2)
with col3:
    st.subheader("Revenue & Competitive Pricing")
    revenue_cat = filtered_df.groupby("subcategory")["final_amount_inr"].sum()
    fig3, ax3 = plt.subplots()
    revenue_cat.sort_values().plot(kind="barh", ax=ax3)
    ax3.set_title("Revenue by Category")
    ax3.set_xlabel("Revenue")
    st.pyplot(fig3)

with col4:
    st.subheader("Correlation Matrix")
    fig5, ax5 = plt.subplots()
    corr = filtered_df[[
        "original_price_inr",
        "discount_percent",
        "discounted_price_inr",
        "quantity",
        "final_amount_inr"
    ]].corr()

    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax5)
    ax5.set_title("Pricing Correlation Analysis")
    st.pyplot(fig5)