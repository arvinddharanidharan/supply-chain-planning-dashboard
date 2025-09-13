import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import io
from utils import *

# Page configuration
st.set_page_config(
    page_title="Supply Chain Planning Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .kpi-container {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    h1 { color: #1e293b; font-weight: 700; }
    h2 { color: #334155; font-weight: 600; margin-top: 2rem; }
    h3 { color: #475569; font-weight: 500; }
    .sidebar .sidebar-content { background-color: #f1f5f9; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f1f5f9;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        orders = pd.read_csv('data/orders.csv', parse_dates=['order_date', 'planned_delivery', 'delivery_date'])
        inventory = pd.read_csv('data/inventory.csv')
        products = pd.read_csv('data/products.csv')
        suppliers = pd.read_csv('data/suppliers.csv')
        
        # Generate open orders data
        open_po = generate_open_purchase_orders(orders, suppliers)
        open_co = generate_open_customer_orders(products)
        
        return orders, inventory, products, suppliers, open_po, open_co
    except FileNotFoundError:
        st.error("📁 Data files not found. Please run data_generator.py first.")
        st.stop()

def generate_open_purchase_orders(orders, suppliers):
    """Generate realistic open purchase orders"""
    np.random.seed(42)
    n_open = 150
    
    open_orders = []
    for i in range(n_open):
        supplier = suppliers.sample(1).iloc[0]
        order_date = datetime.now() - timedelta(days=int(np.random.randint(1, 30)))
        expected_delivery = order_date + timedelta(days=int(supplier['lead_time_target']))
        
        open_orders.append({
            'po_number': f'PO-{2025000 + i}',
            'supplier_id': supplier['supplier_id'],
            'order_date': order_date,
            'expected_delivery': expected_delivery,
            'quantity': np.random.randint(100, 1000),
            'unit_price': np.random.uniform(50, 500),
            'total_value': 0,
            'status': np.random.choice(['Pending', 'In Transit', 'Delayed'], p=[0.4, 0.5, 0.1]),
            'days_outstanding': (datetime.now() - order_date).days
        })
    
    df = pd.DataFrame(open_orders)
    df['total_value'] = df['quantity'] * df['unit_price']
    return df

def generate_open_customer_orders(products):
    """Generate realistic open customer orders"""
    np.random.seed(43)
    n_open = 200
    
    open_orders = []
    for i in range(n_open):
        product = products.sample(1).iloc[0]
        order_date = datetime.now() - timedelta(days=np.random.randint(1, 14))
        promised_delivery = order_date + timedelta(days=int(np.random.randint(3, 21)))
        
        open_orders.append({
            'co_number': f'CO-{3025000 + i}',
            'product_id': product['product_id'],
            'customer': f'Customer_{np.random.randint(1, 50)}',
            'order_date': order_date,
            'promised_delivery': promised_delivery,
            'quantity': np.random.randint(50, 500),
            'unit_price': product['unit_cost'] * np.random.uniform(1.2, 2.0),
            'total_value': 0,
            'status': np.random.choice(['Confirmed', 'In Production', 'Ready to Ship'], p=[0.3, 0.5, 0.2]),
            'priority': np.random.choice(['High', 'Medium', 'Low'], p=[0.2, 0.6, 0.2])
        })
    
    df = pd.DataFrame(open_orders)
    df['total_value'] = df['quantity'] * df['unit_price']
    return df

def create_sidebar_filters(orders, suppliers, products):
    """Create comprehensive sidebar filters"""
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Controls")
        st.markdown("---")
        
        # Time window selection
        time_window = st.selectbox(
            "📅 Time Window",
            ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"],
            index=0
        )
        
        # Date range based on time window
        end_date = orders['order_date'].max().date()
        if time_window == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif time_window == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        elif time_window == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif time_window == "Last Year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = orders['order_date'].min().date()
        
        date_range = st.date_input(
            "📆 Custom Date Range",
            value=[start_date, end_date],
            min_value=orders['order_date'].min().date(),
            max_value=orders['order_date'].max().date()
        )
        
        st.markdown("---")
        
        # Supplier selection
        supplier_options = ['All Suppliers'] + sorted(orders['supplier_id'].unique().tolist())
        selected_suppliers = st.multiselect(
            "🏭 Suppliers",
            options=supplier_options,
            default=['All Suppliers']
        )
        
        # Product category (ABC) filter
        abc_options = ['All Classes'] + sorted(products['abc_class'].unique().tolist())
        selected_abc = st.multiselect(
            "📊 ABC Classification",
            options=abc_options,
            default=['All Classes']
        )
        
        # Product categories
        category_options = ['All Categories'] + sorted(orders['category'].unique().tolist())
        selected_categories = st.multiselect(
            "🏷️ Product Categories",
            options=category_options,
            default=['All Categories']
        )
        
        # Compliance filters
        st.markdown("---")
        compliance_filter = st.selectbox(
            "✅ Process Compliance",
            ["All Orders", "Compliant Only", "Non-Compliant Only", "Happy Path Only"]
        )
        
        return {
            'date_range': date_range,
            'suppliers': selected_suppliers,
            'abc_classes': selected_abc,
            'categories': selected_categories,
            'compliance': compliance_filter
        }

def filter_data(orders, products, filters):
    """Apply filters to data"""
    filtered_orders = orders.copy()
    
    # Date filter
    if len(filters['date_range']) == 2:
        filtered_orders = filtered_orders[
            (filtered_orders['order_date'].dt.date >= filters['date_range'][0]) &
            (filtered_orders['order_date'].dt.date <= filters['date_range'][1])
        ]
    
    # Supplier filter
    if 'All Suppliers' not in filters['suppliers'] and filters['suppliers']:
        filtered_orders = filtered_orders[filtered_orders['supplier_id'].isin(filters['suppliers'])]
    
    # Category filter
    if 'All Categories' not in filters['categories'] and filters['categories']:
        filtered_orders = filtered_orders[filtered_orders['category'].isin(filters['categories'])]
    
    # ABC filter
    if 'All Classes' not in filters['abc_classes'] and filters['abc_classes']:
        filtered_orders = filtered_orders[filtered_orders['abc_class'].isin(filters['abc_classes'])]
    
    # Compliance filter
    if filters['compliance'] == "Compliant Only":
        filtered_orders = filtered_orders[
            (filtered_orders['mrp_compliance'] == 'Compliant') & 
            (filtered_orders['setup_compliance'] == 'Compliant')
        ]
    elif filters['compliance'] == "Non-Compliant Only":
        filtered_orders = filtered_orders[
            (filtered_orders['mrp_compliance'] == 'Non-Compliant') | 
            (filtered_orders['setup_compliance'] == 'Non-Compliant')
        ]
    elif filters['compliance'] == "Happy Path Only":
        filtered_orders = filtered_orders[
            (filtered_orders['mrp_compliance'] == 'Compliant') & 
            (filtered_orders['setup_compliance'] == 'Compliant') &
            (filtered_orders['delivery_date'] <= filtered_orders['planned_delivery']) &
            (filtered_orders['defect_rate'] < 1.0)
        ]
    
    return filtered_orders

def overview_tab(filtered_orders, inventory, products, suppliers):
    """Overview dashboard tab"""
    st.markdown("### 📊 Executive Summary")
    st.caption("Key performance indicators and financial metrics overview")
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        try:
            copq = filtered_orders['quality_cost'].sum() + filtered_orders['late_penalty'].sum()
            st.metric("Cost of Poor Quality", f"${copq:,.0f}", 
                     help="Total cost of quality issues and late delivery penalties")
        except:
            st.metric("Cost of Poor Quality", "N/A")
    
    with col2:
        working_capital = inventory['inventory_value'].sum()
        st.metric("Working Capital", f"${working_capital:,.0f}",
                 help="Total value of inventory on hand")
    
    with col3:
        total_spend = filtered_orders['total_value'].sum()
        st.metric("Procurement Spend", f"${total_spend:,.0f}",
                 help="Total spending on procurement for selected period")
    
    with col4:
        try:
            days_in_period = (filtered_orders['order_date'].max() - filtered_orders['order_date'].min()).days
            annualized_cogs = total_spend * (365 / max(days_in_period, 1))
            turnover = annualized_cogs / working_capital if working_capital > 0 else 0
            st.metric("Inventory Turnover", f"{turnover:.1f}x",
                     help="How many times inventory is sold per year")
        except:
            st.metric("Inventory Turnover", "N/A")
    
    with col5:
        try:
            carrying_cost = inventory['carrying_cost'].sum()
            st.metric("Annual Carrying Cost", f"${carrying_cost:,.0f}",
                     help="Annual cost to hold inventory")
        except:
            st.metric("Annual Carrying Cost", "N/A")
    
    st.markdown("---")
    
    # Operational metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        otd_pct = calculate_otd_percentage(filtered_orders)
        delta = otd_pct - 85  # Target is 85%
        st.metric("On-Time Delivery %", f"{otd_pct:.1f}%", f"{delta:+.1f}%",
                 help="Percentage of orders delivered on time")
    
    with col2:
        avg_lead_time = filtered_orders['lead_time'].mean()
        st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days",
                 help="Average time from order to delivery")
    
    with col3:
        compliance = calculate_process_compliance(filtered_orders, ['mrp_compliance', 'setup_compliance'])
        st.metric("Process Compliance", f"{compliance:.1f}%",
                 help="Percentage following proper processes")
    
    with col4:
        avg_defect_rate = filtered_orders['defect_rate'].mean()
        st.metric("Avg Defect Rate", f"{avg_defect_rate:.2f}%",
                 help="Average percentage of defective units")
    
    with col5:
        critical_stock = (inventory['stock_status'] == 'Critical').sum()
        st.metric("Critical Stock Items", critical_stock,
                 help="Items below safety stock requiring attention")
    
    # Charts section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top suppliers by spend
        supplier_spend = filtered_orders.groupby('supplier_id')['total_value'].sum().reset_index()
        supplier_spend = supplier_spend.sort_values('total_value', ascending=False).head(10)
        
        fig_spend = px.bar(supplier_spend, x='supplier_id', y='total_value',
                          title="Top 10 Suppliers by Spend",
                          color='total_value', color_continuous_scale='Blues')
        fig_spend.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col2:
        # Stock status distribution
        stock_counts = inventory['stock_status'].value_counts()
        colors = {'Critical': '#ef4444', 'Low': '#f59e0b', 'Normal': '#10b981'}
        
        fig_stock = px.pie(values=stock_counts.values, names=stock_counts.index,
                          title="Stock Status Distribution", hole=0.4,
                          color=stock_counts.index, color_discrete_map=colors)
        fig_stock.update_layout(height=400)
        st.plotly_chart(fig_stock, use_container_width=True)

def inventory_tab(inventory, products, open_po):
    """Inventory management tab"""
    st.markdown("### 📦 Inventory Management")
    st.caption("Stock levels, reorder recommendations, and inventory optimization")
    
    # Inventory alerts
    critical_items = inventory[inventory['stock_status'] == 'Critical']
    low_items = inventory[inventory['stock_status'] == 'Low']
    
    if len(critical_items) > 0:
        st.error(f"🚨 {len(critical_items)} items are at critical stock levels!")
        
        with st.expander("View Critical Items"):
            critical_display = critical_items[['product_id', 'current_stock', 'safety_stock', 'rop']].copy()
            critical_display['shortage'] = critical_display['safety_stock'] - critical_display['current_stock']
            st.dataframe(critical_display, use_container_width=True)
    
    if len(low_items) > 0:
        st.warning(f"⚠️ {len(low_items)} items are at low stock levels")
    
    # Reorder recommendations
    st.markdown("#### 🔄 Reorder Recommendations")
    st.caption("Items requiring immediate attention based on current stock levels and reorder points")
    
    reorder_items = inventory[inventory['current_stock'] <= inventory['rop']].copy()
    if len(reorder_items) > 0:
        reorder_items['recommended_qty'] = reorder_items['eoq']
        reorder_items['estimated_cost'] = reorder_items['recommended_qty'] * products.set_index('product_id')['unit_cost']
        
        reorder_display = reorder_items[['product_id', 'current_stock', 'rop', 'recommended_qty', 'estimated_cost']].copy()
        reorder_display['priority'] = reorder_display.apply(
            lambda x: 'High' if x['current_stock'] < x['rop'] * 0.5 else 'Medium', axis=1
        )
        
        st.dataframe(reorder_display.sort_values('estimated_cost', ascending=False), use_container_width=True)
        
        # Export reorder list
        csv = reorder_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Reorder List",
            data=csv,
            file_name=f"reorder_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ All items are adequately stocked")
    
    # Inventory analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # ABC analysis
        abc_counts = inventory.merge(products[['product_id', 'abc_class']], on='product_id')['abc_class'].value_counts()
        fig_abc = px.bar(x=abc_counts.index, y=abc_counts.values,
                        title="Inventory by ABC Classification",
                        color=abc_counts.index, color_discrete_sequence=['#ef4444', '#f59e0b', '#10b981'])
        st.plotly_chart(fig_abc, use_container_width=True)
    
    with col2:
        # Inventory value by category
        inv_category = inventory.merge(products[['product_id', 'category']], on='product_id')
        category_value = inv_category.groupby('category')['inventory_value'].sum().reset_index()
        
        fig_cat = px.pie(category_value, values='inventory_value', names='category',
                        title="Inventory Value by Category")
        st.plotly_chart(fig_cat, use_container_width=True)
    
    # Open Purchase Orders
    st.markdown("#### 📋 Open Purchase Orders")
    st.caption("Current purchase orders pending delivery and their status")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Open POs", len(open_po), help="Number of purchase orders currently open and pending delivery")
    with col2:
        st.metric("Total PO Value", f"${open_po['total_value'].sum():,.0f}", help="Total monetary value of all open purchase orders")
    with col3:
        delayed_pos = len(open_po[open_po['status'] == 'Delayed'])
        st.metric("Delayed POs", delayed_pos, help="Number of purchase orders that are delayed beyond expected delivery date")
    
    # PO status breakdown
    po_status = open_po['status'].value_counts()
    fig_po = px.bar(x=po_status.index, y=po_status.values,
                   title="Purchase Order Status",
                   color=po_status.index)
    st.plotly_chart(fig_po, use_container_width=True)

def suppliers_tab(filtered_orders, suppliers, open_po):
    """Suppliers performance tab"""
    st.markdown("### 🏭 Supplier Performance")
    st.caption("Supplier scorecards, performance matrix, and relationship management")
    
    # Supplier performance matrix
    supplier_perf = filtered_orders.groupby('supplier_id').agg({
        'defect_rate': 'mean',
        'lead_time': 'mean',
        'total_value': 'sum',
        'delivery_date': lambda x: ((filtered_orders.loc[x.index, 'delivery_date'] <= 
                                   filtered_orders.loc[x.index, 'planned_delivery']).mean() * 100)
    }).reset_index()
    supplier_perf.columns = ['supplier_id', 'avg_defect_rate', 'avg_lead_time', 'total_spend', 'otd_rate']
    
    # Performance matrix chart
    fig_matrix = px.scatter(supplier_perf, x='avg_lead_time', y='avg_defect_rate',
                           size='total_spend', color='otd_rate',
                           hover_data=['supplier_id'],
                           title="Supplier Performance Matrix",
                           labels={'avg_lead_time': 'Average Lead Time (days)',
                                  'avg_defect_rate': 'Average Defect Rate (%)',
                                  'otd_rate': 'On-Time Delivery %'})
    
    fig_matrix.add_annotation(text="🎯 Best suppliers: bottom-left quadrant",
                             xref="paper", yref="paper", x=0.02, y=0.98,
                             showarrow=False, font=dict(size=12))
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Supplier scorecards
    st.markdown("#### 📊 Supplier Scorecards")
    st.caption("Performance rankings based on delivery, quality, and lead time metrics")
    
    # Add supplier details
    supplier_details = supplier_perf.merge(suppliers, on='supplier_id')
    supplier_details['performance_score'] = (
        (100 - supplier_details['avg_defect_rate']) * 0.3 +
        supplier_details['otd_rate'] * 0.4 +
        (100 - (supplier_details['avg_lead_time'] / supplier_details['avg_lead_time'].max() * 100)) * 0.3
    )
    
    # Top and bottom performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🏆 Top Performers")
        top_suppliers = supplier_details.nlargest(5, 'performance_score')[
            ['supplier_id', 'supplier_name', 'performance_score', 'otd_rate', 'avg_defect_rate']
        ]
        st.dataframe(top_suppliers, use_container_width=True)
    
    with col2:
        st.markdown("##### ⚠️ Needs Improvement")
        bottom_suppliers = supplier_details.nsmallest(5, 'performance_score')[
            ['supplier_id', 'supplier_name', 'performance_score', 'otd_rate', 'avg_defect_rate']
        ]
        st.dataframe(bottom_suppliers, use_container_width=True)

def compliance_tab(filtered_orders):
    """Process compliance tab"""
    st.markdown("### ✅ Process Compliance Analysis")
    st.caption("Happy path tracking, compliance rates, and process optimization")
    
    # Happy path analysis
    happy_path_orders = filtered_orders[
        (filtered_orders['mrp_compliance'] == 'Compliant') & 
        (filtered_orders['setup_compliance'] == 'Compliant') &
        (filtered_orders['delivery_date'] <= filtered_orders['planned_delivery']) &
        (filtered_orders['defect_rate'] < 1.0)
    ]
    
    happy_path_rate = len(happy_path_orders) / len(filtered_orders) * 100 if len(filtered_orders) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Happy Path Rate", f"{happy_path_rate:.1f}%",
                 help="Percentage of orders following optimal process flow: compliant MRP & setup, on-time delivery, and low defect rate")
    
    with col2:
        mrp_compliance = (filtered_orders['mrp_compliance'] == 'Compliant').mean() * 100
        st.metric("MRP Compliance", f"{mrp_compliance:.1f}%", help="Percentage of orders following proper Material Requirements Planning processes")
    
    with col3:
        setup_compliance = (filtered_orders['setup_compliance'] == 'Compliant').mean() * 100
        st.metric("Setup Compliance", f"{setup_compliance:.1f}%", help="Percentage of orders following proper production setup procedures")
    
    with col4:
        quality_orders = len(filtered_orders[filtered_orders['defect_rate'] < 1.0])
        quality_rate = quality_orders / len(filtered_orders) * 100 if len(filtered_orders) > 0 else 0
        st.metric("Quality Orders", f"{quality_rate:.1f}%", help="Percentage of orders with defect rate below 1% threshold")
    
    # Failed orders drill-down
    st.markdown("#### 🔍 Non-Compliant Orders Analysis")
    st.caption("Detailed breakdown of orders that failed to follow optimal processes")
    
    failed_orders = filtered_orders[
        (filtered_orders['mrp_compliance'] == 'Non-Compliant') | 
        (filtered_orders['setup_compliance'] == 'Non-Compliant') |
        (filtered_orders['delivery_date'] > filtered_orders['planned_delivery']) |
        (filtered_orders['defect_rate'] >= 1.0)
    ].copy()
    
    if len(failed_orders) > 0:
        # Add failure reasons
        failed_orders['failure_reasons'] = failed_orders.apply(lambda row: 
            ', '.join([
                'MRP Non-Compliant' if row['mrp_compliance'] == 'Non-Compliant' else '',
                'Setup Non-Compliant' if row['setup_compliance'] == 'Non-Compliant' else '',
                'Late Delivery' if row['delivery_date'] > row['planned_delivery'] else '',
                'Quality Issues' if row['defect_rate'] >= 1.0 else ''
            ]).strip(', '), axis=1
        )
        
        failure_display = failed_orders[['order_id', 'supplier_id', 'category', 'total_value', 'failure_reasons']].copy()
        st.dataframe(failure_display, use_container_width=True)
        
        # Export failed orders
        csv = failure_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Non-Compliant Orders",
            data=csv,
            file_name=f"non_compliant_orders_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ All orders are compliant!")
    
    # Compliance trends
    compliance_by_category = filtered_orders.groupby('category').agg({
        'mrp_compliance': lambda x: (x == 'Compliant').mean() * 100,
        'setup_compliance': lambda x: (x == 'Compliant').mean() * 100
    }).reset_index()
    
    fig_compliance = px.bar(compliance_by_category, x='category', 
                           y=['mrp_compliance', 'setup_compliance'],
                           title="Compliance Rates by Category",
                           barmode='group')
    st.plotly_chart(fig_compliance, use_container_width=True)

def forecast_tab(filtered_orders, products):
    """Forecasting and scenario analysis tab"""
    st.markdown("### 📈 Demand Forecasting & Scenarios")
    st.caption("Forecast accuracy analysis and scenario planning simulation")
    
    # Generate forecast data
    forecast_data = generate_forecast_data(filtered_orders)
    
    # Forecast accuracy
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mape = calculate_mape(forecast_data['actual'], forecast_data['forecast'])
        st.metric("Forecast Accuracy (MAPE)", f"{mape:.1f}%",
                 help="Mean Absolute Percentage Error - measures forecast accuracy, lower values indicate better forecasting")
    
    with col2:
        accuracy = 100 - mape
        st.metric("Forecast Accuracy", f"{accuracy:.1f}%", help="Overall forecast accuracy percentage (100% - MAPE). Higher values indicate better forecasting performance")
    
    with col3:
        bias = (forecast_data['forecast'] - forecast_data['actual']).mean()
        st.metric("Forecast Bias", f"{bias:+.0f} units", help="Average difference between forecast and actual demand. Positive = over-forecasting, Negative = under-forecasting")
    
    # Demand vs Forecast chart
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=forecast_data['date'], y=forecast_data['actual'],
                                     mode='lines', name='Actual Demand', line=dict(color='blue')))
    fig_forecast.add_trace(go.Scatter(x=forecast_data['date'], y=forecast_data['forecast'],
                                     mode='lines', name='Forecast', line=dict(color='red', dash='dash')))
    fig_forecast.update_layout(title="Demand vs Forecast", height=400)
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Scenario simulation
    st.markdown("#### 🎯 Scenario Simulation")
    st.caption("Test the impact of changes in lead times and demand on key performance metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lead_time_change = st.slider("Lead Time Change (%)", -50, 50, 0, 5)
        demand_change = st.slider("Demand Change (%)", -30, 50, 0, 5)
    
    with col2:
        if st.button("🚀 Run Scenario"):
            scenario_results = run_scenario_simulation(filtered_orders, lead_time_change, demand_change)
            
            st.markdown("##### Scenario Impact:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("OTD Impact", f"{scenario_results['otd_change']:+.1f}%", help="Expected change in On-Time Delivery percentage based on scenario parameters")
            with col2:
                st.metric("Inventory Impact", f"${scenario_results['inventory_change']:+,.0f}", help="Expected change in inventory value due to demand fluctuations")
            with col3:
                st.metric("Cost Impact", f"${scenario_results['cost_change']:+,.0f}", help="Expected change in total costs including quality and penalty costs")

def generate_forecast_data(orders):
    """Generate realistic forecast vs actual data"""
    np.random.seed(42)
    
    # Group orders by date and sum quantities
    daily_demand = orders.groupby(orders['order_date'].dt.date)['quantity'].sum().reset_index()
    daily_demand.columns = ['date', 'actual']
    
    # Generate forecast with some error
    daily_demand['forecast'] = daily_demand['actual'] * np.random.uniform(0.85, 1.15, len(daily_demand))
    
    return daily_demand

def run_scenario_simulation(orders, lead_time_change, demand_change):
    """Run scenario simulation"""
    # Simulate impacts
    base_otd = calculate_otd_percentage(orders)
    base_inventory = orders['total_value'].sum() * 0.3  # Assume 30% inventory ratio
    base_cost = orders['quality_cost'].sum() + orders['late_penalty'].sum()
    
    # Calculate scenario impacts
    otd_impact = -lead_time_change * 0.5  # Lead time increase reduces OTD
    inventory_impact = demand_change * base_inventory / 100
    cost_impact = abs(lead_time_change) * base_cost / 100
    
    return {
        'otd_change': otd_impact,
        'inventory_change': inventory_impact,
        'cost_change': cost_impact
    }

def main():
    # Header
    st.title("🏭 Supply Chain Planning Dashboard")
    st.markdown("**Enterprise-level supply chain analytics and optimization platform**")
    
    # Load data
    orders, inventory, products, suppliers, open_po, open_co = load_data()
    
    # Sidebar filters
    filters = create_sidebar_filters(orders, suppliers, products)
    filtered_orders = filter_data(orders, products, filters)
    
    # Data summary
    if len(filtered_orders) == 0:
        st.warning("⚠️ No data matches the selected filters. Showing all data.")
        filtered_orders = orders
    else:
        st.success(f"✅ Analyzing {len(filtered_orders):,} orders from {len(filtered_orders['supplier_id'].unique())} suppliers")
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📦 Inventory", 
        "🏭 Suppliers", 
        "✅ Compliance", 
        "📈 Forecast"
    ])
    
    with tab1:
        overview_tab(filtered_orders, inventory, products, suppliers)
    
    with tab2:
        inventory_tab(inventory, products, open_po)
    
    with tab3:
        suppliers_tab(filtered_orders, suppliers, open_po)
    
    with tab4:
        compliance_tab(filtered_orders)
    
    with tab5:
        forecast_tab(filtered_orders, products)
    
    # Footer
    st.markdown("---")
    st.markdown("*Supply Chain Planning Dashboard - Professional Analytics Platform*")

if __name__ == "__main__":
    main()