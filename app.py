import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Streamlit page config
st.set_page_config(
    page_title="Supply Chain Planning Dashboard",
    page_icon="📊",
    layout="wide"
)

# Utility functions
def calculate_otd_percentage(df):
    """Calculate On-Time Delivery percentage"""
    if len(df) == 0:
        return 0
    on_time = df['delivery_date'] <= df['planned_delivery']
    return (on_time.sum() / len(df)) * 100

def calculate_process_compliance(df, process_steps):
    """Calculate process compliance percentage"""
    if len(df) == 0:
        return 0
    compliance_scores = []
    for step in process_steps:
        if step in df.columns:
            compliance = (df[step] == 'Compliant').sum() / len(df) * 100
            compliance_scores.append(compliance)
    return np.mean(compliance_scores) if compliance_scores else 0

def calculate_copq(orders_df):
    """Calculate Cost of Poor Quality"""
    if 'quality_cost' in orders_df.columns and 'late_penalty' in orders_df.columns:
        return orders_df['quality_cost'].sum() + orders_df['late_penalty'].sum()
    return 0

def calculate_working_capital(inventory_df):
    """Calculate Working Capital tied in Inventory"""
    if 'inventory_value' in inventory_df.columns:
        return inventory_df['inventory_value'].sum()
    return 0

def calculate_inventory_turnover(orders_df, inventory_df):
    """Calculate Inventory Turnover Ratio"""
    cogs = orders_df['total_value'].sum()
    if 'inventory_value' in inventory_df.columns:
        avg_inventory = inventory_df['inventory_value'].mean()
        return cogs / avg_inventory if avg_inventory > 0 else 0
    return 0

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
    st.markdown("*Real-time monitoring of planning processes, compliance, and optimization opportunities*")
    
    # Load data
    orders, inventory, products, suppliers = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Date Range",
        value=[orders['order_date'].min().date(), orders['order_date'].max().date()],
        min_value=orders['order_date'].min().date(),
        max_value=orders['order_date'].max().date()
    )
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Product Categories",
        options=orders['category'].unique(),
        default=orders['category'].unique()
    )
    
    # ABC Class filter
    abc_classes = st.sidebar.multiselect(
        "ABC Classification",
        options=['A', 'B', 'C'],
        default=['A', 'B', 'C']
    )
    
    # Filter data
    filtered_orders = orders[
        (orders['order_date'].dt.date >= date_range[0]) &
        (orders['order_date'].dt.date <= date_range[1]) &
        (orders['category'].isin(categories)) &
        (orders['abc_class'].isin(abc_classes))
    ]
    
    # Financial KPIs Row
    st.header("💰 Financial Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        copq = calculate_copq(filtered_orders)
        st.metric("Cost of Poor Quality", f"${copq:,.0f}")
    
    with col2:
        working_capital = calculate_working_capital(inventory)
        st.metric("Working Capital (Inventory)", f"${working_capital:,.0f}")
    
    with col3:
        total_spend = filtered_orders['total_value'].sum()
        st.metric("Total Procurement Spend", f"${total_spend:,.0f}")
    
    with col4:
        inventory_turnover = calculate_inventory_turnover(filtered_orders, inventory)
        st.metric("Inventory Turnover", f"{inventory_turnover:.1f}x")
    
    with col5:
        if 'carrying_cost' in inventory.columns:
            carrying_cost = inventory['carrying_cost'].sum()
        else:
            carrying_cost = 0
        st.metric("Annual Carrying Cost", f"${carrying_cost:,.0f}")
    
    # Operational KPIs Row
    st.header("🎯 Operational Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        otd_pct = calculate_otd_percentage(filtered_orders)
        st.metric("On-Time Delivery %", f"{otd_pct:.1f}%")
    
    with col2:
        avg_lead_time = filtered_orders['lead_time'].mean()
        st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")
    
    with col3:
        process_compliance = calculate_process_compliance(filtered_orders, ['mrp_compliance', 'setup_compliance'])
        st.metric("Process Compliance", f"{process_compliance:.1f}%")
    
    with col4:
        avg_defect_rate = filtered_orders['defect_rate'].mean()
        st.metric("Avg Defect Rate", f"{avg_defect_rate:.2f}%")
    
    with col5:
        critical_stock = (inventory['stock_status'] == 'Critical').sum()
        st.metric("Critical Stock Items", critical_stock)
    
    # Financial Analytics Section
    st.header("💰 Financial Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Procurement Spend by Supplier
        supplier_spend = filtered_orders.groupby('supplier_id')['total_value'].sum().reset_index()
        supplier_spend = supplier_spend.sort_values('total_value', ascending=False).head(10)
        
        fig_spend = px.bar(supplier_spend, x='supplier_id', y='total_value',
                          title="Top 10 Suppliers by Spend",
                          labels={'total_value': 'Spend ($)', 'supplier_id': 'Supplier'})
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col2:
        # Cost of Poor Quality Breakdown
        if 'quality_cost' in filtered_orders.columns and 'late_penalty' in filtered_orders.columns:
            quality_costs = {
                'Defective Products': filtered_orders['quality_cost'].sum(),
                'Late Delivery Penalties': filtered_orders['late_penalty'].sum()
            }
            
            fig_copq = px.pie(values=list(quality_costs.values()), names=list(quality_costs.keys()),
                             title="Cost of Poor Quality Breakdown")
            st.plotly_chart(fig_copq, use_container_width=True)
        else:
            st.info("Quality cost data not available")
    
    # Performance Analytics
    st.header("📈 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # OTD Trend
        monthly_otd = filtered_orders.groupby(filtered_orders['order_date'].dt.to_period('M')).apply(
            lambda x: calculate_otd_percentage(x)
        ).reset_index()
        monthly_otd['order_date'] = monthly_otd['order_date'].astype(str)
        
        fig_otd = px.line(monthly_otd, x='order_date', y=0, 
                         title="On-Time Delivery Trend",
                         labels={'0': 'OTD %', 'order_date': 'Month'})
        fig_otd.add_hline(y=95, line_dash="dash", line_color="green", 
                         annotation_text="Target: 95%")
        st.plotly_chart(fig_otd, use_container_width=True)
    
    with col2:
        # Supplier Performance
        supplier_perf = filtered_orders.groupby('supplier_id').agg({
            'delivery_date': 'count',
            'defect_rate': 'mean',
            'lead_time': 'mean'
        }).reset_index()
        supplier_perf.columns = ['supplier_id', 'order_count', 'avg_defect_rate', 'avg_lead_time']
        
        fig_supplier = px.scatter(supplier_perf, x='avg_lead_time', y='avg_defect_rate',
                                 size='order_count', hover_data=['supplier_id'],
                                 title="Supplier Performance Matrix",
                                 labels={'avg_lead_time': 'Avg Lead Time (days)',
                                        'avg_defect_rate': 'Avg Defect Rate (%)'})
        st.plotly_chart(fig_supplier, use_container_width=True)

if __name__ == "__main__":
    main()