import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Amazon India Dashboard", layout="wide")

st.title("📊 Amazon India Sales Analytics")


@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+pymysql://root:Keerthick2300$@localhost/amazon_india_analytics"
    )

@st.cache_data
def load_data():
    engine = get_engine()

    transactions = pd.read_sql("select * from transactions", engine)
    products = pd.read_sql("select * from products", engine)
    customers = pd.read_sql("select * from customers", engine)
    time_dimension = pd.read_sql("select * from time_dimension", engine)

    df = transactions.merge(products, on="product_id", how="left")
    df = df.merge(customers, on="customer_id", how="left")
    df = df.merge(time_dimension, on="order_date", how="left")

    return df

