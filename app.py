import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Supply Chain Planning Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        orders = pd.read_csv('data/orders.csv', parse_dates=['order_date', 'planned_delivery', 'delivery_date'])
        inventory = pd.read_csv('data/inventory.csv')
        products = pd.read_csv('data/products.csv')
        suppliers = pd.read_csv('data/suppliers.csv')
        return orders, inventory, products, suppliers
    except FileNotFoundError:
        st.error("Data files not found. Please run data_generator.py first.")
        st.stop()

def main():
    st.title("📊 Supply Chain Planning & KPI Dashboard")
    
    orders, inventory, products, suppliers = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=[orders['order_date'].min().date(), orders['order_date'].max().date()],
        min_value=orders['order_date'].min().date(),
        max_value=orders['order_date'].max().date()
    )
    
    categories = st.sidebar.multiselect(
        "Product Categories",
        options=orders['category'].unique(),
        default=orders['category'].unique()
    )
    
    # Filter data
    filtered_orders = orders[
        (orders['order_date'].dt.date >= date_range[0]) &
        (orders['order_date'].dt.date <= date_range[1]) &
        (orders['category'].isin(categories))
    ]
    
    # Ensure we have data after filtering
    if len(filtered_orders) == 0:
        st.warning("No data matches the selected filters. Using all data.")
        filtered_orders = orders
    
    # Financial KPIs
    st.header("💰 Financial Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        try:
            copq = filtered_orders['quality_cost'].sum() + filtered_orders['late_penalty'].sum()
            st.metric("Cost of Poor Quality", f"${copq:,.0f}")
        except KeyError:
            st.metric("Cost of Poor Quality", "N/A")
    
    with col2:
        try:
            working_capital = inventory['inventory_value'].sum()
            st.metric("Working Capital", f"${working_capital:,.0f}")
        except KeyError:
            st.metric("Working Capital", "N/A")
    
    with col3:
        total_spend = filtered_orders['total_value'].sum()
        st.metric("Procurement Spend", f"${total_spend:,.0f}")
    
    with col4:
        cogs = filtered_orders['total_value'].sum()
        try:
            avg_inventory = inventory['inventory_value'].mean()
            turnover = cogs / avg_inventory if avg_inventory > 0 else 0
            st.metric("Inventory Turnover", f"{turnover:.1f}x")
        except KeyError:
            st.metric("Inventory Turnover", "N/A")
    
    with col5:
        try:
            carrying_cost = inventory['carrying_cost'].sum()
            st.metric("Carrying Cost", f"${carrying_cost:,.0f}")
        except KeyError:
            st.metric("Carrying Cost", "N/A")
    
    # Operational KPIs
    st.header("🎯 Operational Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        on_time = (filtered_orders['delivery_date'] <= filtered_orders['planned_delivery']).sum()
        otd_pct = (on_time / len(filtered_orders)) * 100 if len(filtered_orders) > 0 else 0
        st.metric("On-Time Delivery %", f"{otd_pct:.1f}%")
    
    with col2:
        avg_lead_time = filtered_orders['lead_time'].mean()
        st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")
    
    with col3:
        mrp_compliant = (filtered_orders['mrp_compliance'] == 'Compliant').sum()
        setup_compliant = (filtered_orders['setup_compliance'] == 'Compliant').sum()
        compliance = ((mrp_compliant + setup_compliant) / (len(filtered_orders) * 2)) * 100
        st.metric("Process Compliance", f"{compliance:.1f}%")
    
    with col4:
        avg_defect_rate = filtered_orders['defect_rate'].mean()
        st.metric("Avg Defect Rate", f"{avg_defect_rate:.2f}%")
    
    with col5:
        critical_stock = (inventory['stock_status'] == 'Critical').sum()
        st.metric("Critical Stock Items", critical_stock)
    
    # Charts
    st.header("📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Supplier Spend
        supplier_spend = filtered_orders.groupby('supplier_id')['total_value'].sum().reset_index()
        supplier_spend = supplier_spend.sort_values('total_value', ascending=False).head(10)
        
        fig_spend = px.bar(supplier_spend, x='supplier_id', y='total_value',
                          title="Top 10 Suppliers by Spend")
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col2:
        # Stock Status
        stock_status_counts = inventory['stock_status'].value_counts()
        fig_stock = px.pie(values=stock_status_counts.values, names=stock_status_counts.index,
                          title="Stock Status Distribution")
        st.plotly_chart(fig_stock, use_container_width=True)
    
    # Supplier Performance
    supplier_perf = filtered_orders.groupby('supplier_id').agg({
        'defect_rate': 'mean',
        'lead_time': 'mean',
        'total_value': 'sum'
    }).reset_index()
    
    fig_supplier = px.scatter(supplier_perf, x='lead_time', y='defect_rate',
                             size='total_value', hover_data=['supplier_id'],
                             title="Supplier Performance Matrix")
    st.plotly_chart(fig_supplier, use_container_width=True)

if __name__ == "__main__":
    main()