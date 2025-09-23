import streamlit as st
import pandas as pd
from database import load_data_from_db

st.set_page_config(page_title="Database Viewer", layout="wide")

st.title("📊 Database Table Viewer")

# Load data
orders, inventory, products, suppliers = load_data_from_db()

if orders is not None:
    tab1, tab2, tab3, tab4 = st.tabs(["Orders", "Inventory", "Products", "Suppliers"])
    
    with tab1:
        st.subheader("Orders Table")
        st.dataframe(orders, use_container_width=True)
        st.caption(f"Total records: {len(orders)}")
    
    with tab2:
        st.subheader("Inventory Table")
        st.dataframe(inventory, use_container_width=True)
        st.caption(f"Total records: {len(inventory)}")
    
    with tab3:
        st.subheader("Products Table")
        st.dataframe(products, use_container_width=True)
        st.caption(f"Total records: {len(products)}")
    
    with tab4:
        st.subheader("Suppliers Table")
        st.dataframe(suppliers, use_container_width=True)
        st.caption(f"Total records: {len(suppliers)}")
else:
    st.error("Failed to load data from database")