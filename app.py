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
    
    # Filter data
    filtered_orders = orders[
        (orders['order_date'].dt.date >= date_range[0]) &
        (orders['order_date'].dt.date <= date_range[1]) &
        (orders['category'].isin(categories))
    ]
    
    # Financial KPIs Row
    st.header("💰 Financial Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        copq = filtered_orders['quality_cost'].sum() + filtered_orders['late_penalty'].sum()
        st.metric("Cost of Poor Quality", f"${copq:,.0f}")
    
    with col2:
        working_capital = inventory['inventory_value'].sum()
        st.metric("Working Capital", f"${working_capital:,.0f}")
    
    with col3:
        total_spend = filtered_orders['total_value'].sum()
        st.metric("Procurement Spend", f"${total_spend:,.0f}")
    
    with col4:
        cogs = filtered_orders['total_value'].sum()
        avg_inventory = inventory['inventory_value'].mean()
        turnover = cogs / avg_inventory if avg_inventory > 0 else 0
        st.metric("Inventory Turnover", f"{turnover:.1f}x")
    
    with col5:
        carrying_cost = inventory['carrying_cost'].sum()
        st.metric("Carrying Cost", f"${carrying_cost:,.0f}")
    
    # Operational KPIs Row
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
        quality_cost_total = filtered_orders['quality_cost'].sum()
        penalty_cost_total = filtered_orders['late_penalty'].sum()
        
        if quality_cost_total > 0 or penalty_cost_total > 0:
            quality_costs = {
                'Defective Products': quality_cost_total,
                'Late Delivery Penalties': penalty_cost_total
            }
            
            fig_copq = px.pie(values=list(quality_costs.values()), names=list(quality_costs.keys()),
                             title="Cost of Poor Quality Breakdown")
            st.plotly_chart(fig_copq, use_container_width=True)
        else:
            st.info("No quality costs in selected period")
    
    # Working Capital Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory Value by Category
        inventory_with_products = inventory.merge(products, on='product_id')
        category_value = inventory_with_products.groupby('category')['inventory_value'].sum().reset_index()
        
        fig_inv_value = px.bar(category_value, x='category', y='inventory_value',
                              title="Working Capital by Category",
                              labels={'inventory_value': 'Inventory Value ($)', 'category': 'Category'})
        st.plotly_chart(fig_inv_value, use_container_width=True)
    
    with col2:
        # Carrying Cost vs Inventory Value
        fig_carrying = px.scatter(inventory_with_products, x='inventory_value', y='carrying_cost',
                                 color='category', size='current_stock',
                                 title="Carrying Cost vs Inventory Value",
                                 labels={'inventory_value': 'Inventory Value ($)',
                                        'carrying_cost': 'Annual Carrying Cost ($)'})
        st.plotly_chart(fig_carrying, use_container_width=True)
    
    # Performance Analytics
    st.header("📈 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # OTD Trend
        monthly_data = filtered_orders.groupby(filtered_orders['order_date'].dt.to_period('M')).agg({
            'delivery_date': 'count',
            'planned_delivery': lambda x: ((filtered_orders.loc[x.index, 'delivery_date'] <= 
                                          filtered_orders.loc[x.index, 'planned_delivery']).sum())
        }).reset_index()
        monthly_data['otd_pct'] = (monthly_data['planned_delivery'] / monthly_data['delivery_date']) * 100
        monthly_data['order_date'] = monthly_data['order_date'].astype(str)
        
        fig_otd = px.line(monthly_data, x='order_date', y='otd_pct', 
                         title="On-Time Delivery Trend",
                         labels={'otd_pct': 'OTD %', 'order_date': 'Month'})
        fig_otd.add_hline(y=95, line_dash="dash", line_color="green", 
                         annotation_text="Target: 95%")
        st.plotly_chart(fig_otd, use_container_width=True)
    
    with col2:
        # Supplier Performance
        supplier_perf = filtered_orders.groupby('supplier_id').agg({
            'delivery_date': 'count',
            'defect_rate': 'mean',
            'lead_time': 'mean',
            'total_value': 'sum'
        }).reset_index()
        supplier_perf.columns = ['supplier_id', 'order_count', 'avg_defect_rate', 'avg_lead_time', 'total_spend']
        
        fig_supplier = px.scatter(supplier_perf, x='avg_lead_time', y='avg_defect_rate',
                                 size='total_spend', hover_data=['supplier_id', 'order_count'],
                                 title="Supplier Performance Matrix",
                                 labels={'avg_lead_time': 'Avg Lead Time (days)',
                                        'avg_defect_rate': 'Avg Defect Rate (%)'})
        st.plotly_chart(fig_supplier, use_container_width=True)
    
    # Inventory Management Section
    st.header("📦 Inventory Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Stock Status Distribution
        stock_status_counts = inventory['stock_status'].value_counts()
        fig_stock = px.pie(values=stock_status_counts.values, names=stock_status_counts.index,
                          title="Stock Status Distribution")
        st.plotly_chart(fig_stock, use_container_width=True)
    
    with col2:
        # EOQ vs Current Stock
        fig_eoq = px.scatter(inventory, x='current_stock', y='eoq',
                            color='stock_status',
                            title="Current Stock vs EOQ",
                            labels={'current_stock': 'Current Stock',
                                   'eoq': 'Economic Order Quantity'})
        st.plotly_chart(fig_eoq, use_container_width=True)
    
    with col3:
        # Reorder Recommendations
        reorder_needed = inventory[inventory['current_stock'] < inventory['rop']]
        st.subheader(f"🚨 Reorder Alerts ({len(reorder_needed)})")
        
        if len(reorder_needed) > 0:
            reorder_display = reorder_needed[['product_id', 'current_stock', 'rop', 'eoq']].head(10)
            reorder_display['shortage'] = reorder_display['rop'] - reorder_display['current_stock']
            st.dataframe(reorder_display, use_container_width=True)
        else:
            st.success("✅ No immediate reorders needed")

if __name__ == "__main__":
    main()