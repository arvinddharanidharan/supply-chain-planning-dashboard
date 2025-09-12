import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils import *

st.set_page_config(
    page_title="Supply Chain Planning Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    orders = pd.read_csv('data/orders.csv', parse_dates=['order_date', 'planned_delivery', 'delivery_date'])
    inventory = pd.read_csv('data/inventory.csv')
    products = pd.read_csv('data/products.csv')
    suppliers = pd.read_csv('data/suppliers.csv')
    return orders, inventory, products, suppliers

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
    
    # KPI Metrics Row
    st.header("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        otd_pct = calculate_otd_percentage(filtered_orders)
        st.metric("On-Time Delivery %", f"{otd_pct:.1f}%", 
                 delta=f"{otd_pct-85:.1f}%" if otd_pct >= 85 else f"{otd_pct-85:.1f}%")
    
    with col2:
        avg_lead_time = filtered_orders['lead_time'].mean()
        target_lead_time = filtered_orders['lead_time_target'].mean()
        st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days",
                 delta=f"{avg_lead_time-target_lead_time:.1f} days")
    
    with col3:
        process_compliance = calculate_process_compliance(filtered_orders, ['mrp_compliance', 'setup_compliance'])
        st.metric("Process Compliance", f"{process_compliance:.1f}%",
                 delta=f"{process_compliance-90:.1f}%")
    
    with col4:
        avg_defect_rate = filtered_orders['defect_rate'].mean()
        st.metric("Avg Defect Rate", f"{avg_defect_rate:.2f}%",
                 delta=f"{2.0-avg_defect_rate:.2f}%" if avg_defect_rate <= 2.0 else f"{2.0-avg_defect_rate:.2f}%")
    
    with col5:
        critical_stock = (inventory['stock_status'] == 'Critical').sum()
        st.metric("Critical Stock Items", critical_stock,
                 delta=f"-{critical_stock}" if critical_stock > 0 else "0")
    
    # Charts Row 1
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
        # Lead Time Distribution
        fig_lead = px.histogram(filtered_orders, x='lead_time', nbins=20,
                               title="Lead Time Distribution",
                               labels={'lead_time': 'Lead Time (days)', 'count': 'Frequency'})
        fig_lead.add_vline(x=filtered_orders['lead_time_target'].mean(), 
                          line_dash="dash", line_color="red",
                          annotation_text="Target")
        st.plotly_chart(fig_lead, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
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
    
    with col2:
        # ABC Analysis
        abc_summary = filtered_orders.groupby('abc_class').agg({
            'total_value': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        fig_abc = px.pie(abc_summary, values='total_value', names='abc_class',
                        title="Value Distribution by ABC Class")
        st.plotly_chart(fig_abc, use_container_width=True)
    
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
    
    # Process Compliance Section
    st.header("⚙️ Process Compliance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Compliance by Category
        compliance_by_cat = filtered_orders.groupby('category').agg({
            'mrp_compliance': lambda x: (x == 'Compliant').mean() * 100,
            'setup_compliance': lambda x: (x == 'Compliant').mean() * 100
        }).reset_index()
        
        fig_compliance = px.bar(compliance_by_cat, x='category', 
                               y=['mrp_compliance', 'setup_compliance'],
                               title="Process Compliance by Category",
                               labels={'value': 'Compliance %', 'variable': 'Process Type'})
        st.plotly_chart(fig_compliance, use_container_width=True)
    
    with col2:
        # Non-Compliance Root Causes
        non_compliant = filtered_orders[
            (filtered_orders['mrp_compliance'] == 'Non-Compliant') |
            (filtered_orders['setup_compliance'] == 'Non-Compliant')
        ]
        
        if len(non_compliant) > 0:
            root_causes = non_compliant.groupby(['category', 'abc_class']).size().reset_index(name='count')
            fig_root = px.treemap(root_causes, path=['category', 'abc_class'], values='count',
                                 title="Non-Compliance Distribution")
            st.plotly_chart(fig_root, use_container_width=True)
        else:
            st.success("✅ No compliance issues detected")
    
    # Recommendations Section
    st.header("💡 Optimization Recommendations")
    
    # Generate recommendations
    recommendations = []
    
    # Lead time recommendations
    high_lead_time_suppliers = supplier_perf[supplier_perf['avg_lead_time'] > supplier_perf['avg_lead_time'].quantile(0.8)]
    for _, supplier in high_lead_time_suppliers.iterrows():
        recommendations.append({
            'Type': 'Lead Time',
            'Priority': 'High',
            'Recommendation': f"Supplier {supplier['supplier_id']}: Reduce lead time by {supplier['avg_lead_time'] - supplier_perf['avg_lead_time'].median():.1f} days",
            'Impact': 'Improved OTD, reduced inventory'
        })
    
    # Quality recommendations
    high_defect_suppliers = supplier_perf[supplier_perf['avg_defect_rate'] > 3.0]
    for _, supplier in high_defect_suppliers.iterrows():
        recommendations.append({
            'Type': 'Quality',
            'Priority': 'Critical',
            'Recommendation': f"Supplier {supplier['supplier_id']}: Implement quality improvement plan (current defect rate: {supplier['avg_defect_rate']:.2f}%)",
            'Impact': 'Reduced waste, improved customer satisfaction'
        })
    
    # Inventory recommendations
    excess_stock = inventory[inventory['current_stock'] > inventory['eoq'] * 2]
    for _, item in excess_stock.head(5).iterrows():
        recommendations.append({
            'Type': 'Inventory',
            'Priority': 'Medium',
            'Recommendation': f"Product {item['product_id']}: Reduce EOQ by {((item['current_stock'] / item['eoq']) - 1) * 100:.0f}% to optimize carrying costs",
            'Impact': 'Reduced working capital, lower storage costs'
        })
    
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        
        # Color code by priority
        def color_priority(val):
            if val == 'Critical':
                return 'background-color: #ffebee'
            elif val == 'High':
                return 'background-color: #fff3e0'
            return 'background-color: #e8f5e8'
        
        st.dataframe(
            rec_df.style.applymap(color_priority, subset=['Priority']),
            use_container_width=True
        )
    else:
        st.success("✅ All processes are optimized - no immediate recommendations")

if __name__ == "__main__":
    main()