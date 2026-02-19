import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from Home import load_data

st.set_page_config(layout="wide")
st.title("Product & Inventory Analytics")

st.header("📦 Product Performance Dashboard")

df = load_data()

product_summary = df.groupby("product_name").agg({
    "final_amount_inr": "sum",
    "quantity": "sum",
    "product_rating": "mean",
    "return_status": lambda x: (x == "Returned").mean() * 100
}).reset_index()

top_n = st.selectbox("Select Top N Products", [5,10,15,20])

top_products = product_summary.sort_values(
    "final_amount_inr", ascending=False
).head(top_n)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top products by revenue")

    plt.figure()
    plt.barh(top_products["product_name"], top_products["final_amount_inr"])
    plt.xlabel("Revenue")
    plt.gca().invert_yaxis()
    st.pyplot(plt)

with col2:
    st.subheader("Category-wise Revenue")
    category_rev = df.groupby("subcategory")["final_amount_inr"].sum()

    plt.figure()
    plt.barh(category_rev.index, category_rev.values)
    plt.xlabel("Revenue")
    st.pyplot(plt)


st.subheader("Product Lifecycle Trend")
col3, col4 = st.columns(2)
with col3:
    selected_product = st.selectbox(
        "Select Product",
        df["product_name"].unique()
    )
    product_trend = df[df["product_name"] == selected_product].groupby("order_year")["final_amount_inr"].sum()
    plt.figure()
    plt.plot(product_trend.index, product_trend.values)
    plt.xlabel("Year")
    plt.ylabel("Total Revenue")
    st.pyplot(plt)
with col4:
    selected_product1 = st.multiselect(
        "Select brand",
        sorted(df["brand"].unique().tolist()),
        default=sorted(df["brand"].unique().tolist())[:5]

    )
    units_sold = df[df["brand"].isin(selected_product1)].groupby("brand")["quantity"].sum().reset_index()
    plt.figure()
    plt.plot(units_sold["brand"], units_sold["quantity"])
    plt.xlabel("Brand")
    plt.ylabel("Total units sold")
    st.pyplot(plt)

st.divider()

st.header("💰 Brand Analytics Dashboard")

brand_rev = df.groupby("brand")["final_amount_inr"].sum().sort_values(ascending=False)
select_num = st.selectbox(
    "Select Top N", [5, 10, 15, 20]
)
col5, col6 = st.columns(2)

with col5:
    st.subheader("Brand Revenue Ranking")
    plt.figure()
    plt.barh(brand_rev.head(select_num).index, brand_rev.head(select_num).values)
    plt.gca().invert_yaxis()
    plt.xlabel("Revenue")
    st.pyplot(plt)

with col6:
    st.subheader("Brand Market Share")
    total_rev = df["final_amount_inr"].sum()
    brand_share = (brand_rev / total_rev) * 100
    plt.figure()
    plt.pie(brand_share.head(select_num), labels=brand_share.head(select_num).index, autopct='%1.1f%%')
    st.pyplot(plt)

col7, col8 = st.columns(2)

with col7:
    st.subheader("Brand Growth Over Years")
    selected_brand = st.selectbox("Select Brand", df["brand"].unique())
    brand_trend = df[df["brand"] == selected_brand].groupby("order_year")["final_amount_inr"].sum()
    plt.figure()
    plt.plot(brand_trend.index, brand_trend.values)
    plt.xlabel("Year")
    plt.ylabel("Revenue")
    st.pyplot(plt)
with col8:
    st.subheader("Customer preference")
    customer_pref = df.groupby("subcategory")["customer_id"].count()
    plt.figure()
    plt.plot(customer_pref.index, customer_pref.values)
    plt.xticks(rotation=45)
    plt.ylabel("Customers")
    st.pyplot(plt)

st.divider()
st.header("📦 Inventory Optimization Dashboard")

monthly_demand = df.groupby("order_month")["quantity"].sum()

col9, col10 = st.columns(2)

with col9:
    st.subheader("Monthly Demand Pattern")
    plt.figure()
    plt.bar(monthly_demand.index, monthly_demand.values)
    plt.xlabel("Month")
    plt.ylabel("Quantity")
    st.pyplot(plt)

with col10:
    st.subheader("Seasonal Revenue Trend")
    seasonal = df.groupby("order_quarter")["final_amount_inr"].sum()
    plt.figure()
    plt.bar(seasonal.index, seasonal.values)
    plt.xlabel("Quater")
    plt.ylabel("Revenue")
    st.pyplot(plt)

st.subheader("Demand Forecast (Simple Rolling Average)")

yearly = df.groupby("order_year")["quantity"].sum()
forecast = yearly.rolling(3).mean()

plt.figure()
plt.plot(yearly.index, yearly.values, label="Actual Quantity")
plt.plot(forecast.index, forecast.values, label="3-Year Moving Avg (Trend)")
plt.xlabel("Year")
plt.ylabel("Quantity")
plt.legend()
st.pyplot(plt)


st.divider()
st.header("⭐ Product Rating & Review Dashboard")
st.subheader("Filter Options")

selected_category = st.selectbox(
    "Select Category",
    ["All"] + list(df["subcategory"].unique())
)

if selected_category != "All":
    filtered_df = df[df["subcategory"] == selected_category]

col1, col2, col3 = st.columns(3)

col1.metric("Average Rating", round(filtered_df["product_rating"].mean(), 2))
col2.metric("Total Reviews", filtered_df["product_rating"].count())
col3.metric("Total Revenue", f"₹ {int(filtered_df['final_amount_inr'].sum())}")

col11, col12 = st.columns(2)
with col11:
    st.subheader("📊 Rating Distribution")

    plt.figure()
    plt.hist(filtered_df["product_rating"].dropna(), bins=5)
    plt.xlabel("Rating")
    plt.ylabel("Count")
    st.pyplot(plt)

with col12:
    st.subheader("📈 Rating vs Revenue")

    rating_sales = filtered_df.groupby("product_rating")["final_amount_inr"].sum()

    plt.figure()
    plt.scatter(rating_sales.index, rating_sales.values)
    plt.xlabel("Rating")
    plt.ylabel("Revenue")
    st.pyplot(plt)

st.subheader("Return Rate vs Rating")

return_analysis = filtered_df.groupby("product_rating")["return_status"].apply(lambda x: (x == "Returned").mean()*100)

plt.figure()
plt.plot(return_analysis.index, return_analysis.values)
plt.xlabel("Rating")
plt.ylabel("Return Rate (%)")
st.pyplot(plt)


st.divider()

st.header("🚀 New Product Launch Dashboard")
first_sale = df.groupby("product_id")["order_year"].min().reset_index()
first_sale.columns = ["product_id", "launch_year"]

df = df.merge(first_sale, on="product_id", how="left")
launch_df = df[df["order_year"] == df["launch_year"]]

st.subheader("Filter Options")

selected_year = st.selectbox(
    "Select Launch Year",
    sorted(launch_df["launch_year"].unique())
)
launch_df = launch_df[launch_df["launch_year"] == selected_year]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Launch Revenue", f"₹ {int(launch_df['final_amount_inr'].sum())}")
col2.metric("Products Launched", launch_df["product_id"].nunique())
col3.metric("Avg Launch Rating", round(launch_df["product_rating"].mean(), 2))
col4.metric("Launch Return Rate (%)", round((launch_df["return_status"] == "Returned").mean()*100, 2))

col7, col8 = st.columns(2)

with col7:
    st.subheader("Top Launch Products by Revenue")
    top_launch = launch_df.groupby("product_name")["final_amount_inr"].sum().sort_values(ascending=False).head(10)

    plt.figure()
    plt.barh(top_launch.index, top_launch.values)
    plt.xlabel("Revenue")
    plt.gca().invert_yaxis()
    st.pyplot(plt)

with col8:
    st.subheader("📊 Launch Revenue by Category")
    category_launch = launch_df.groupby("subcategory")["final_amount_inr"].sum()

    plt.figure()
    plt.bar(category_launch.index, category_launch.values)
    plt.xticks(rotation=45)
    st.pyplot(plt)