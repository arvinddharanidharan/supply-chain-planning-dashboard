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
    return orders_df['quality_cost'].sum() + orders_df['late_penalty'].sum()

def calculate_working_capital(inventory_df):
    """Calculate Working Capital tied in Inventory"""
    return inventory_df['inventory_value'].sum()

def calculate_inventory_turnover(orders_df, inventory_df):
    """Calculate Inventory Turnover Ratio"""
    cogs = orders_df['total_value'].sum()
    avg_inventory = inventory_df['inventory_value'].mean()
    return cogs / avg_inventory if avg_inventory > 0 else 0

def simple_moving_average_forecast(data, window=7, forecast_days=30):
    """Simple moving average forecast"""
    if len(data) < window:
        return np.full(forecast_days, data.mean())
    
    # Calculate moving average
    ma = data.rolling(window=window).mean().iloc[-1]
    
    # Add trend component
    recent_trend = (data.iloc[-1] - data.iloc[-window]) / window
    
    # Generate forecast
    forecast = []
    for i in range(forecast_days):
        forecast_value = ma + (recent_trend * i)
        forecast.append(max(0, forecast_value))  # Ensure non-negative
    
    return np.array(forecast)

def calculate_forecast_accuracy(actual, forecast):
    """Calculate MAPE (Mean Absolute Percentage Error)"""
    if len(actual) == 0 or len(forecast) == 0:
        return 0
    
    actual = np.array(actual)
    forecast = np.array(forecast)
    
    # Avoid division by zero
    mask = actual != 0
    if not mask.any():
        return 0
    
    mape = np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100
    return max(0, 100 - mape)  # Convert to accuracy percentage

def apply_scenario(orders_df, inventory_df, lead_time_change=0, demand_change=0):
    """Apply scenario changes to data"""
    scenario_orders = orders_df.copy()
    scenario_inventory = inventory_df.copy()
    
    # Apply lead time changes
    if lead_time_change != 0:
        scenario_orders['lead_time'] = scenario_orders['lead_time'] + lead_time_change
        scenario_orders['delivery_date'] = scenario_orders['planned_delivery'] + pd.Timedelta(days=lead_time_change)
        # Recalculate late penalties
        late_orders = scenario_orders['delivery_date'] > scenario_orders['planned_delivery']
        scenario_orders.loc[late_orders, 'late_penalty'] = scenario_orders.loc[late_orders, 'total_value'] * 0.02
    
    # Apply demand changes
    if demand_change != 0:
        multiplier = 1 + (demand_change / 100)
        scenario_orders['quantity'] = scenario_orders['quantity'] * multiplier
        scenario_orders['total_value'] = scenario_orders['total_value'] * multiplier
        
        # Update inventory based on demand change
        scenario_inventory['avg_demand'] = scenario_inventory['avg_demand'] * multiplier
        scenario_inventory['rop'] = scenario_inventory['rop'] * multiplier
    
    return scenario_orders, scenario_inventory

def calculate_scenario_impact(baseline_orders, baseline_inventory, scenario_orders, scenario_inventory):
    """Calculate impact metrics for scenario"""
    baseline_otd = calculate_otd_percentage(baseline_orders)
    scenario_otd = calculate_otd_percentage(scenario_orders)
    
    baseline_copq = calculate_copq(baseline_orders)
    scenario_copq = calculate_copq(scenario_orders)
    
    baseline_critical = (baseline_inventory['stock_status'] == 'Critical').sum()
    scenario_critical = (scenario_inventory['current_stock'] < scenario_inventory['rop']).sum()
    
    return {
        'otd_change': scenario_otd - baseline_otd,
        'copq_change': scenario_copq - baseline_copq,
        'critical_items_change': scenario_critical - baseline_critical,
    }

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

def create_demand_forecast_chart(orders_df):
    """Create demand forecast visualization"""
    # Aggregate daily demand
    daily_demand = orders_df.groupby('order_date')['quantity'].sum().reset_index()
    daily_demand = daily_demand.set_index('order_date').resample('D').sum().fillna(0)
    
    # Split data for training and testing
    split_point = int(len(daily_demand) * 0.8)
    train_data = daily_demand.iloc[:split_point]
    test_data = daily_demand.iloc[split_point:]
    
    # Generate forecast
    forecast_values = simple_moving_average_forecast(train_data['quantity'], window=7, forecast_days=len(test_data))
    
    # Calculate accuracy
    accuracy = calculate_forecast_accuracy(test_data['quantity'].values, forecast_values)
    
    # Create future forecast
    future_dates = pd.date_range(start=daily_demand.index[-1] + timedelta(days=1), periods=30, freq='D')
    future_forecast = simple_moving_average_forecast(daily_demand['quantity'], window=7, forecast_days=30)
    
    # Create plot
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=train_data.index,
        y=train_data['quantity'],
        mode='lines',
        name='Historical Demand',
        line=dict(color='blue')
    ))
    
    # Test data (actual)
    fig.add_trace(go.Scatter(
        x=test_data.index,
        y=test_data['quantity'],
        mode='lines',
        name='Actual Demand',
        line=dict(color='green')
    ))
    
    # Test forecast
    fig.add_trace(go.Scatter(
        x=test_data.index,
        y=forecast_values,
        mode='lines',
        name='Forecast (Test)',
        line=dict(color='red', dash='dash')
    ))
    
    # Future forecast
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_forecast,
        mode='lines',
        name='Future Forecast',
        line=dict(color='orange', dash='dot')
    ))
    
    fig.update_layout(
        title=f"Demand Forecast (Accuracy: {accuracy:.1f}%)",
        xaxis_title="Date",
        yaxis_title="Daily Demand (Units)",
        hovermode='x unified'
    )
    
    return fig, accuracy

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
    
    # Scenario Planning Section
    st.sidebar.header("🎯 Scenario Planning")
    st.sidebar.markdown("*Test 'What-if' scenarios*")
    
    lead_time_change = st.sidebar.slider(
        "Lead Time Change (days)",
        min_value=-5,
        max_value=10,
        value=0,
        help="Simulate lead time increase/decrease"
    )
    
    demand_change = st.sidebar.slider(
        "Demand Change (%)",
        min_value=-50,
        max_value=100,
        value=0,
        help="Simulate demand spike or drop"
    )
    
    scenario_active = lead_time_change != 0 or demand_change != 0
    
    # Filter data
    filtered_orders = orders[
        (orders['order_date'].dt.date >= date_range[0]) &
        (orders['order_date'].dt.date <= date_range[1]) &
        (orders['category'].isin(categories)) &
        (orders['abc_class'].isin(abc_classes))
    ]
    
    # Apply scenario if active
    if scenario_active:
        scenario_orders, scenario_inventory = apply_scenario(
            filtered_orders, inventory, lead_time_change, demand_change
        )
        impact = calculate_scenario_impact(filtered_orders, inventory, scenario_orders, scenario_inventory)
        
        # Show scenario alert
        st.warning(f"🎯 **Scenario Active**: Lead Time {lead_time_change:+d} days, Demand {demand_change:+.0f}%")
        
        # Use scenario data for calculations
        display_orders = scenario_orders
        display_inventory = scenario_inventory
    else:
        display_orders = filtered_orders
        display_inventory = inventory
        impact = None
    
    # Financial KPIs Row
    st.header("💰 Financial Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        copq = calculate_copq(display_orders)
        delta_copq = f"${impact['copq_change']:+,.0f}" if impact else None
        st.metric("Cost of Poor Quality", f"${copq:,.0f}", delta=delta_copq)
    
    with col2:
        working_capital = calculate_working_capital(display_inventory)
        st.metric("Working Capital (Inventory)", f"${working_capital:,.0f}")
    
    with col3:
        total_spend = display_orders['total_value'].sum()
        st.metric("Total Procurement Spend", f"${total_spend:,.0f}")
    
    with col4:
        inventory_turnover = calculate_inventory_turnover(display_orders, display_inventory)
        st.metric("Inventory Turnover", f"{inventory_turnover:.1f}x")
    
    with col5:
        carrying_cost = display_inventory['carrying_cost'].sum()
        st.metric("Annual Carrying Cost", f"${carrying_cost:,.0f}")
    
    # Operational KPIs Row
    st.header("🎯 Operational Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        otd_pct = calculate_otd_percentage(display_orders)
        delta_otd = f"{impact['otd_change']:+.1f}%" if impact else None
        st.metric("On-Time Delivery %", f"{otd_pct:.1f}%", delta=delta_otd)
    
    with col2:
        avg_lead_time = display_orders['lead_time'].mean()
        st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")
    
    with col3:
        process_compliance = calculate_process_compliance(display_orders, ['mrp_compliance', 'setup_compliance'])
        st.metric("Process Compliance", f"{process_compliance:.1f}%")
    
    with col4:
        avg_defect_rate = display_orders['defect_rate'].mean()
        st.metric("Avg Defect Rate", f"{avg_defect_rate:.2f}%")
    
    with col5:
        if scenario_active:
            critical_stock = (display_inventory['current_stock'] < display_inventory['rop']).sum()
            delta_critical = f"{impact['critical_items_change']:+d}" if impact else None
        else:
            critical_stock = (display_inventory['stock_status'] == 'Critical').sum()
            delta_critical = None
        st.metric("Critical Stock Items", critical_stock, delta=delta_critical)
    
    # Financial Analytics Section
    st.header("💰 Financial Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Procurement Spend by Supplier
        supplier_spend = display_orders.groupby('supplier_id')['total_value'].sum().reset_index()
        supplier_spend = supplier_spend.sort_values('total_value', ascending=False).head(10)
        
        fig_spend = px.bar(supplier_spend, x='supplier_id', y='total_value',
                          title="Top 10 Suppliers by Spend",
                          labels={'total_value': 'Spend ($)', 'supplier_id': 'Supplier'})
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col2:
        # Cost of Poor Quality Breakdown
        quality_costs = {
            'Defective Products': display_orders['quality_cost'].sum(),
            'Late Delivery Penalties': display_orders['late_penalty'].sum()
        }
        
        fig_copq = px.pie(values=list(quality_costs.values()), names=list(quality_costs.keys()),
                         title="Cost of Poor Quality Breakdown")
        st.plotly_chart(fig_copq, use_container_width=True)
    
    # Working Capital Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory Value by Category
        inventory_with_products = display_inventory.merge(products, on='product_id')
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
    
    # Scenario Impact Analysis
    if scenario_active:
        st.header("📊 Scenario Financial Impact")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💸 Cost Impact")
            if impact['copq_change'] > 10000:
                st.error(f"🔴 COPQ increases by ${impact['copq_change']:,.0f}")
            elif impact['copq_change'] > 0:
                st.warning(f"🟡 COPQ increases by ${impact['copq_change']:,.0f}")
            else:
                st.success(f"✅ COPQ stable or decreases")
        
        with col2:
            st.subheader("📦 Inventory Impact")
            if impact['critical_items_change'] > 5:
                st.error(f"🔴 {impact['critical_items_change']} more critical items")
            elif impact['critical_items_change'] > 0:
                st.warning(f"🟡 {impact['critical_items_change']} more items at risk")
            else:
                st.success("✅ No additional inventory risk")
        
        with col3:
            st.subheader("💰 Business Impact")
            total_value_change = (display_orders['total_value'].sum() - filtered_orders['total_value'].sum())
            if abs(total_value_change) > 100000:
                st.info(f"💵 Spend change: ${total_value_change:,.0f}")
            
            if impact['otd_change'] < -10:
                st.error("⚠️ Significant customer service impact")
    
    # Demand Forecasting Section
    st.header("🔮 Demand Forecasting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Demand forecast chart
        forecast_fig, forecast_accuracy = create_demand_forecast_chart(display_orders)
        st.plotly_chart(forecast_fig, use_container_width=True)
    
    with col2:
        # Forecast metrics and insights
        st.subheader("📊 Forecast Performance")
        
        # Calculate demand statistics
        daily_demand = display_orders.groupby('order_date')['quantity'].sum()
        demand_volatility = daily_demand.std() / daily_demand.mean() if daily_demand.mean() > 0 else 0
        
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric("Forecast Accuracy", f"{forecast_accuracy:.1f}%")
            st.metric("Avg Daily Demand", f"{daily_demand.mean():.0f}")
        
        with col2b:
            st.metric("Demand Volatility", f"{demand_volatility:.2f}")
            st.metric("Peak Demand", f"{daily_demand.max():.0f}")
        
        # Forecast insights
        st.subheader("💡 Forecast Insights")
        if forecast_accuracy >= 80:
            st.success("✅ High forecast accuracy - reliable for planning")
        elif forecast_accuracy >= 60:
            st.warning("⚠️ Moderate accuracy - monitor closely")
        else:
            st.error("🔴 Low accuracy - improve demand sensing")

if __name__ == "__main__":
    main()