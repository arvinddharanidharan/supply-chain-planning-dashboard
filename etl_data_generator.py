import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from database import create_tables, load_data_to_db

def generate_incremental_data():
    """Generate new daily data that builds on existing data"""
    np.random.seed(int(datetime.now().timestamp()))
    
    # Business-relevant parameters
    current_date = datetime.now().date()
    
    # Generate new orders (10-50 per day)
    n_new_orders = np.random.randint(10, 51)
    
    # Supplier performance trends (some suppliers getting better/worse)
    supplier_trends = {
        'SUP_001': {'lead_time_factor': 0.95, 'quality_trend': 1.02},  # Improving
        'SUP_002': {'lead_time_factor': 1.08, 'quality_trend': 0.98},  # Declining
        'SUP_003': {'lead_time_factor': 1.0, 'quality_trend': 1.0},    # Stable
    }
    
    # Generate suppliers
    suppliers_data = []
    for i in range(1, 21):
        supplier_id = f'SUP_{i:03d}'
        trend = supplier_trends.get(supplier_id, {'lead_time_factor': 1.0, 'quality_trend': 1.0})
        
        base_lead_time = np.random.randint(5, 21)
        adjusted_lead_time = int(base_lead_time * trend['lead_time_factor'])
        
        base_quality = np.random.uniform(3.5, 5.0)
        adjusted_quality = min(5.0, base_quality * trend['quality_trend'])
        
        suppliers_data.append({
            'supplier_id': supplier_id,
            'supplier_name': f'Supplier {supplier_id}',
            'lead_time_target': adjusted_lead_time,
            'quality_rating': round(adjusted_quality, 1)
        })
    
    suppliers_df = pd.DataFrame(suppliers_data)
    
    # Generate products with seasonal demand patterns
    products_data = []
    categories = ['Electronics', 'Automotive', 'Industrial', 'Consumer Goods', 'Raw Materials']
    
    for i in range(1, 101):
        product_id = f'PROD_{i:03d}'
        category = np.random.choice(categories)
        
        # ABC classification based on value
        abc_weights = [0.2, 0.3, 0.5]  # 20% A, 30% B, 50% C
        abc_class = np.random.choice(['A', 'B', 'C'], p=abc_weights)
        
        # Cost varies by ABC class
        if abc_class == 'A':
            unit_cost = np.random.uniform(100, 500)
        elif abc_class == 'B':
            unit_cost = np.random.uniform(50, 150)
        else:
            unit_cost = np.random.uniform(10, 75)
        
        products_data.append({
            'product_id': product_id,
            'product_name': f'Product {product_id}',
            'category': category,
            'abc_class': abc_class,
            'unit_cost': round(unit_cost, 2)
        })
    
    products_df = pd.DataFrame(products_data)
    
    # Generate new orders with business logic
    orders_data = []
    for i in range(n_new_orders):
        supplier = suppliers_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        
        # Order date (today or yesterday)
        order_date = current_date - timedelta(days=np.random.randint(0, 2))
        
        # Planned delivery based on supplier lead time
        planned_delivery = order_date + timedelta(days=supplier['lead_time_target'])
        
        # Actual delivery (some delays based on supplier performance)
        delay_probability = 0.15 if supplier['quality_rating'] > 4.0 else 0.3
        if np.random.random() < delay_probability:
            actual_delay = np.random.randint(1, 5)
            delivery_date = planned_delivery + timedelta(days=actual_delay)
        else:
            delivery_date = planned_delivery - timedelta(days=np.random.randint(0, 2))
        
        # Quantity based on ABC class
        if product['abc_class'] == 'A':
            quantity = np.random.randint(50, 200)
        elif product['abc_class'] == 'B':
            quantity = np.random.randint(100, 500)
        else:
            quantity = np.random.randint(200, 1000)
        
        # Calculate costs
        total_value = quantity * product['unit_cost']
        lead_time = (delivery_date - order_date).days
        
        # Compliance based on supplier quality
        mrp_compliance = 'Compliant' if np.random.random() < 0.85 else 'Non-Compliant'
        setup_compliance = 'Compliant' if np.random.random() < 0.80 else 'Non-Compliant'
        
        # Defect rate inversely related to supplier quality
        base_defect_rate = max(0, 5 - supplier['quality_rating'])
        defect_rate = np.random.exponential(base_defect_rate)
        
        # Quality costs
        quality_cost = defect_rate * total_value * 0.001 if defect_rate > 1 else 0
        late_penalty = max(0, (lead_time - supplier['lead_time_target']) * total_value * 0.0005)
        
        orders_data.append({
            'order_id': f'ORD_{datetime.now().strftime("%Y%m%d")}_{i:04d}',
            'supplier_id': supplier['supplier_id'],
            'product_id': product['product_id'],
            'category': product['category'],
            'abc_class': product['abc_class'],
            'order_date': order_date,
            'planned_delivery': planned_delivery,
            'delivery_date': delivery_date,
            'quantity': quantity,
            'unit_cost': product['unit_cost'],
            'total_value': round(total_value, 2),
            'lead_time': lead_time,
            'mrp_compliance': mrp_compliance,
            'setup_compliance': setup_compliance,
            'defect_rate': round(defect_rate, 2),
            'quality_cost': round(quality_cost, 2),
            'late_penalty': round(late_penalty, 2)
        })
    
    orders_df = pd.DataFrame(orders_data)
    
    # Generate inventory with dynamic stock levels
    inventory_data = []
    for _, product in products_df.iterrows():
        # Stock levels based on recent demand
        if product['abc_class'] == 'A':
            current_stock = np.random.randint(50, 500)
            safety_stock = np.random.randint(20, 100)
        elif product['abc_class'] == 'B':
            current_stock = np.random.randint(100, 800)
            safety_stock = np.random.randint(50, 200)
        else:
            current_stock = np.random.randint(200, 1500)
            safety_stock = np.random.randint(100, 400)
        
        # EOQ calculation (simplified)
        eoq = int(np.sqrt(2 * 1000 * product['unit_cost']) * np.random.uniform(0.8, 1.2))
        
        # Reorder point
        rop = safety_stock + np.random.randint(10, 50)
        
        # Stock status
        if current_stock < safety_stock:
            stock_status = 'Critical'
        elif current_stock < rop:
            stock_status = 'Low'
        else:
            stock_status = 'Normal'
        
        inventory_value = current_stock * product['unit_cost']
        carrying_cost = inventory_value * 0.25  # 25% annual carrying cost
        
        inventory_data.append({
            'product_id': product['product_id'],
            'current_stock': current_stock,
            'safety_stock': safety_stock,
            'eoq': eoq,
            'rop': rop,
            'inventory_value': round(inventory_value, 2),
            'carrying_cost': round(carrying_cost, 2),
            'stock_status': stock_status
        })
    
    inventory_df = pd.DataFrame(inventory_data)
    
    return orders_df, inventory_df, suppliers_df, products_df

def run_etl_pipeline():
    """Main ETL pipeline function"""
    print(f"Starting ETL pipeline at {datetime.now()}")
    
    try:
        # Extract & Transform
        orders_df, inventory_df, suppliers_df, products_df = generate_incremental_data()
        
        # Create database tables
        if not create_tables():
            print("Failed to create database tables, saving to CSV")
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            return False
        
        # Load to database
        if load_data_to_db(orders_df, inventory_df, suppliers_df, products_df):
            print("ETL pipeline completed successfully")
            # Also save to CSV as backup
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            return True
        else:
            print("Database load failed, saving to CSV only")
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            return False
            
    except Exception as e:
        print(f"ETL pipeline failed: {e}")
        return False

def save_to_csv(orders_df, inventory_df, suppliers_df, products_df):
    """Save data to CSV files as backup"""
    os.makedirs('data', exist_ok=True)
    orders_df.to_csv('data/orders.csv', index=False)
    inventory_df.to_csv('data/inventory.csv', index=False)
    suppliers_df.to_csv('data/suppliers.csv', index=False)
    products_df.to_csv('data/products.csv', index=False)
    print("Data saved to CSV files")

if __name__ == "__main__":
    run_etl_pipeline()