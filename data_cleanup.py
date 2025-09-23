#!/usr/bin/env python3
"""
Data cleanup and transformation script for supply chain data
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

def clean_and_transform_data():
    """Clean and standardize all CSV data files"""
    
    # Clean orders data
    orders = pd.read_csv('data/orders.csv')
    orders['order_date'] = pd.to_datetime(orders['order_date'], format='mixed').dt.date
    orders['planned_delivery'] = pd.to_datetime(orders['planned_delivery'], format='mixed').dt.date  
    orders['delivery_date'] = pd.to_datetime(orders['delivery_date'], format='mixed').dt.date
    orders['created_timestamp'] = pd.to_datetime(orders['created_timestamp'], format='mixed')
    
    # Ensure numeric columns are properly formatted
    orders['quantity'] = orders['quantity'].astype(int)
    orders['unit_cost'] = orders['unit_cost'].round(2)
    orders['total_value'] = orders['total_value'].round(2)
    orders['lead_time'] = orders['lead_time'].astype(int)
    orders['defect_rate'] = orders['defect_rate'].round(2)
    orders['quality_cost'] = orders['quality_cost'].round(2)
    orders['late_penalty'] = orders['late_penalty'].round(2)
    
    # Clean suppliers data
    suppliers = pd.read_csv('data/suppliers.csv')
    suppliers['lead_time_target'] = suppliers['lead_time_target'].astype(int)
    suppliers['quality_rating'] = suppliers['quality_rating'].round(1)
    suppliers['updated_timestamp'] = pd.to_datetime(suppliers['updated_timestamp'])
    
    # Clean products data
    products = pd.read_csv('data/products.csv')
    products['unit_cost'] = products['unit_cost'].round(2)
    if 'updated_timestamp' in products.columns:
        products['updated_timestamp'] = pd.to_datetime(products['updated_timestamp'])
    
    # Clean inventory data
    inventory = pd.read_csv('data/inventory.csv')
    inventory['current_stock'] = inventory['current_stock'].astype(int)
    inventory['safety_stock'] = inventory['safety_stock'].astype(int)
    inventory['eoq'] = inventory['eoq'].astype(int)
    inventory['rop'] = inventory['rop'].astype(int)
    inventory['inventory_value'] = inventory['inventory_value'].round(2)
    inventory['carrying_cost'] = inventory['carrying_cost'].round(2)
    if 'updated_timestamp' in inventory.columns:
        inventory['updated_timestamp'] = pd.to_datetime(inventory['updated_timestamp'])
    
    # Save cleaned data
    orders.to_csv('data/orders.csv', index=False)
    suppliers.to_csv('data/suppliers.csv', index=False)
    products.to_csv('data/products.csv', index=False)
    inventory.to_csv('data/inventory.csv', index=False)
    
    print(f"Data cleaned successfully:")
    print(f"  Orders: {len(orders)} records")
    print(f"  Suppliers: {len(suppliers)} records") 
    print(f"  Products: {len(products)} records")
    print(f"  Inventory: {len(inventory)} records")

if __name__ == "__main__":
    clean_and_transform_data()