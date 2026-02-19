import streamlit as st
import pandas as pd
from Home import load_data
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("👥 Customer Analytics Dashboard")

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
    tier_filter = st.multiselect(
        "Select Customer Tier",
        df["customer_tier"].unique(),
        default=df["customer_tier"].unique()
    )

filtered_df = df[
    (df["order_year"].isin(year_filter)) &
    (df["customer_tier"].isin(tier_filter))
]

st.divider()
st.subheader("Key Customer Metrics")

k1, k2, k3, k4 = st.columns(4)

total_customers = filtered_df["customer_id"].nunique()
total_revenue = filtered_df["final_amount_inr"].sum()
avg_clv = filtered_df.groupby("customer_id")["final_amount_inr"].sum().mean()

repeat_customers = filtered_df[filtered_df.duplicated("customer_id", keep=False)]["customer_id"].nunique()
retention_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0

k1.metric("Total Customers", total_customers)
k2.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
k3.metric("Avg Customer Lifetime Value", f"₹ {avg_clv:,.0f}")
k4.metric("Retention Rate", f"{retention_rate:.2f}%")

st.divider()
st.subheader("🔄 Customer Journey Analysis")

purchase_count = filtered_df.groupby("customer_id")["transaction_id"].count()
journey_df = purchase_count.reset_index()
journey_df.columns = ["customer_id", "purchase_count"]

journey_df["Customer_Type"] = journey_df["purchase_count"].apply(
    lambda x: "New" if x == 1 else "Repeat"
)

c1, c2 = st.columns(2)

with c1:
    st.bar_chart(journey_df["Customer_Type"].value_counts())

with c2:
    fig, ax = plt.subplots()
    sns.histplot(journey_df["purchase_count"], bins=30, ax=ax)
    ax.set_title("Purchase Frequency Distribution")
    st.pyplot(fig)

st.divider()

prime_summary = filtered_df.groupby("is_prime_member").agg({
    "final_amount_inr": ["mean", "sum"],
    "transaction_id": "count"
})

prime_revenue_share = filtered_df.groupby("is_prime_member")["final_amount_inr"].sum() / total_revenue * 100

p1, p2 = st.columns(2)

with p1:
    st.subheader("Prime Membership Analysis")
    st.bar_chart(prime_revenue_share, y="final_amount_inr")

with p2:
    st.subheader("Avg Spend by prime vs non prime members")
    st.bar_chart(prime_summary["final_amount_inr"]["mean"])

st.divider()
st.subheader("📈 Customer Retention Trend")

yearly_customers = filtered_df.groupby("order_year")["customer_id"].nunique()
st.line_chart(yearly_customers)

st.divider()
st.subheader("👶 Demographics & Behavior Analysis")

d1, d2 = st.columns(2)

with d1:
    age_revenue = filtered_df.groupby("customer_age_group")["final_amount_inr"].sum()
    st.bar_chart(age_revenue)

with d2:
    tier_aov = filtered_df.groupby("customer_tier")["final_amount_inr"].mean()
    st.bar_chart(tier_aov)

d3, d4 = st.columns(2)

with d3:
    st.subheader("State wise Revenue")
    state_revenue = filtered_df.groupby("customer_state")["final_amount_inr"].sum()
    st.bar_chart(state_revenue)

with d4:
    st.subheader("City wise Revenue")
    city_revenue = filtered_df.groupby("customer_city")["final_amount_inr"].mean()
    st.bar_chart(city_revenue)
