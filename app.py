import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Supply Chain Planning Dashboard",
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
    st.title("Supply Chain Planning & KPI Dashboard")
    
    orders, inventory, products, suppliers = load_data()
    
    st.sidebar.header("Filters")
    
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
    
    st.header("Financial Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        try:
            copq = filtered_orders['quality_cost'].sum() + filtered_orders['late_penalty'].sum()
            st.metric("Cost of Poor Quality ℹ️", f"${copq:,.0f}", help="Total cost of quality issues and late delivery penalties. Calculated as: Quality Costs + Late Penalties")
        except KeyError:
            st.metric("Cost of Poor Quality ℹ️", "N/A", help="Data not available")
    
    with col2:
        try:
            working_capital = inventory['inventory_value'].sum()
            st.metric("Working Capital ℹ️", f"${working_capital:,.0f}", help="Total value of inventory on hand. Calculated as: Sum of (Current Stock × Unit Cost) for all products")
        except KeyError:
            st.metric("Working Capital ℹ️", "N/A", help="Data not available")
    
    with col3:
        total_spend = filtered_orders['total_value'].sum()
        st.metric("Procurement Spend ℹ️", f"${total_spend:,.0f}", help="Total spending on procurement for the selected period. Calculated as: Sum of all order values")
    
    with col4:
        try:
            total_inventory_value = inventory['inventory_value'].sum()
            days_in_period = (filtered_orders['order_date'].max() - filtered_orders['order_date'].min()).days
            annualized_cogs = total_spend * (365 / max(days_in_period, 1))
            turnover = annualized_cogs / total_inventory_value if total_inventory_value > 0 else 0
            st.metric("Inventory Turnover ℹ️", f"{turnover:.1f}x", help="How many times inventory is sold per year. Calculated as: Annualized COGS ÷ Average Inventory Value")
        except KeyError:
            st.metric("Inventory Turnover ℹ️", "N/A", help="Data not available")
    
    with col5:
        try:
            carrying_cost = inventory['carrying_cost'].sum()
            st.metric("Annual Carrying Cost ℹ️", f"${carrying_cost:,.0f}", help="Annual cost to hold inventory. Calculated as: Inventory Value × Carrying Cost Rate (15-35% annually)")
        except KeyError:
            st.metric("Annual Carrying Cost ℹ️", "N/A", help="Data not available")
    
    st.header("Operational Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        on_time = (filtered_orders['delivery_date'] <= filtered_orders['planned_delivery']).sum()
        otd_pct = (on_time / len(filtered_orders)) * 100 if len(filtered_orders) > 0 else 0
        st.metric("On-Time Delivery % ℹ️", f"{otd_pct:.1f}%", help="Percentage of orders delivered on or before planned delivery date. Calculated as: (On-time deliveries ÷ Total orders) × 100")
    
    with col2:
        avg_lead_time = filtered_orders['lead_time'].mean()
        st.metric("Avg Lead Time ℹ️", f"{avg_lead_time:.1f} days", help="Average time from order placement to delivery. Calculated as: Sum of (Delivery Date - Order Date) ÷ Number of orders")
    
    with col3:
        mrp_compliant = (filtered_orders['mrp_compliance'] == 'Compliant').sum()
        setup_compliant = (filtered_orders['setup_compliance'] == 'Compliant').sum()
        compliance = ((mrp_compliant + setup_compliant) / (len(filtered_orders) * 2)) * 100
        st.metric("Process Compliance ℹ️", f"{compliance:.1f}%", help="Percentage of orders following proper MRP and setup processes. Calculated as: (Compliant processes ÷ Total process steps) × 100")
    
    with col4:
        avg_defect_rate = filtered_orders['defect_rate'].mean()
        st.metric("Avg Defect Rate ℹ️", f"{avg_defect_rate:.2f}%", help="Average percentage of defective units received. Calculated as: Sum of (Defective units ÷ Total units) × 100 ÷ Number of orders")
    
    with col5:
        critical_stock = (inventory['stock_status'] == 'Critical').sum()
        st.metric("Critical Stock Items ℹ️", critical_stock, help="Number of products with stock levels below safety stock. Items requiring immediate attention to avoid stockouts")
    
    st.header("Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:

        supplier_spend = filtered_orders.groupby('supplier_id')['total_value'].sum().reset_index()
        supplier_spend = supplier_spend.sort_values('total_value', ascending=False).head(10)
        
        fig_spend = px.bar(supplier_spend, x='supplier_id', y='total_value',
                          title="Top 10 Suppliers by Spend")
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col2:

        stock_status_counts = inventory['stock_status'].value_counts()
        colors = {'Critical': '#ff4444', 'Low': '#ffaa00', 'Normal': '#44aa44'}
        fig_stock = px.pie(values=stock_status_counts.values, names=stock_status_counts.index,
                          title="Stock Status Distribution",
                          color=stock_status_counts.index,
                          color_discrete_map=colors)
        st.plotly_chart(fig_stock, use_container_width=True)
    

    supplier_perf = filtered_orders.groupby('supplier_id').agg({
        'defect_rate': 'mean',
        'lead_time': 'mean',
        'total_value': 'sum'
    }).reset_index()
    
    fig_supplier = px.scatter(supplier_perf, x='lead_time', y='defect_rate',
                             size='total_value', hover_data=['supplier_id'],
                             title="Supplier Performance Matrix",
                             labels={'lead_time': 'Average Lead Time (days)', 
                                   'defect_rate': 'Average Defect Rate (%)',
                                   'total_value': 'Total Spend ($)'})
    fig_supplier.add_annotation(text="Better suppliers appear in bottom-left (low lead time, low defects)",
                               xref="paper", yref="paper", x=0.02, y=0.98, showarrow=False,
                               font=dict(size=10, color="gray"))
    st.plotly_chart(fig_supplier, use_container_width=True)

if __name__ == "__main__":
    main()