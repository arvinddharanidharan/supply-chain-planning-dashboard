import pandas as pd
import numpy as np

def calculate_eoq(annual_demand, ordering_cost, holding_cost):
    """Find the best order quantity to minimize total costs"""
    return np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

def calculate_rop(avg_demand, lead_time, safety_stock=0):
    """Figure out when to place a new order"""
    return (avg_demand * lead_time) + safety_stock

def calculate_safety_stock(demand_std, lead_time, service_level=0.95):
    """Calculate how much extra stock to keep as a buffer"""
    from scipy.stats import norm
    z_score = norm.ppf(service_level)
    return z_score * demand_std * np.sqrt(lead_time)

def calculate_inventory_turnover(cogs, avg_inventory):
    """See how many times per year we sell through our inventory"""
    return cogs / avg_inventory if avg_inventory > 0 else 0

def calculate_otd_percentage(df, date_col='delivery_date', planned_col='planned_delivery'):
    """Calculate what percentage of orders arrived on time"""
    on_time = df[date_col] <= df[planned_col]
    return (on_time.sum() / len(df)) * 100

def calculate_mape(actual, forecast):
    """Measure how far off our forecasts were from reality"""
    return np.mean(np.abs((actual - forecast) / actual)) * 100

def calculate_forecast_accuracy(actual, forecast):
    """Calculate how accurate our forecasts were as a percentage"""
    mape = calculate_mape(actual, forecast)
    return 100 - mape

def identify_abc_classification(df, value_col, qty_col):
    """Classify items by importance: A=most valuable, C=least valuable"""
    df = df.copy()
    df['total_value'] = df[value_col] * df[qty_col]
    df = df.sort_values('total_value', ascending=False)
    df['cumulative_value'] = df['total_value'].cumsum()
    df['cumulative_pct'] = df['cumulative_value'] / df['total_value'].sum() * 100
    
    conditions = [
        df['cumulative_pct'] <= 80,
        df['cumulative_pct'] <= 95,
        df['cumulative_pct'] > 95
    ]
    choices = ['A', 'B', 'C']
    df['abc_class'] = np.select(conditions, choices)
    return df

def calculate_process_compliance(df, process_steps):
    """Calculate what percentage of orders followed proper processes"""
    compliance_scores = []
    for step in process_steps:
        if step in df.columns:
            compliance = (df[step] == 'Compliant').sum() / len(df) * 100
            compliance_scores.append(compliance)
    return np.mean(compliance_scores) if compliance_scores else 0

def generate_kpi_summary(df):
    """Create a summary of all the key performance indicators"""
    kpis = {}
    
    # Stock-related performance metrics
    if 'stock_level' in df.columns and 'demand' in df.columns:
        kpis['avg_stock_level'] = df['stock_level'].mean()
        kpis['stockout_rate'] = (df['stock_level'] == 0).mean() * 100
        kpis['inventory_turnover'] = calculate_inventory_turnover(
            df['demand'].sum() * df.get('unit_cost', 1).mean(),
            df['stock_level'].mean()
        )
    
    # Delivery performance metrics
    if 'delivery_date' in df.columns and 'planned_delivery' in df.columns:
        kpis['otd_percentage'] = calculate_otd_percentage(df)
        
    # Time-related performance metrics
    if 'lead_time' in df.columns:
        kpis['avg_lead_time'] = df['lead_time'].mean()
        kpis['lead_time_variance'] = df['lead_time'].std()
    
    return kpis