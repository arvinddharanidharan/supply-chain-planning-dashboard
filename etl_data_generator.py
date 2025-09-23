import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging
from database import create_tables, load_data_to_db

def generate_incremental_data():
    """Generate new daily data that builds on existing data"""
    np.random.seed(int(datetime.now().timestamp()))
    
    current_date = datetime.now().date()
    n_new_orders = np.random.randint(8, 15)  # Realistic daily order volume
    
    # Realistic supplier names and performance
    realistic_suppliers = [
        {'name': 'Bosch Manufacturing', 'country': 'Germany', 'lead_base': 7, 'quality_base': 4.5},
        {'name': 'Toyota Supply Co', 'country': 'Japan', 'lead_base': 5, 'quality_base': 4.8},
        {'name': 'Foxconn Electronics', 'country': 'China', 'lead_base': 12, 'quality_base': 4.2},
        {'name': 'Magna International', 'country': 'Canada', 'lead_base': 8, 'quality_base': 4.6},
        {'name': 'Siemens Industrial', 'country': 'Germany', 'lead_base': 10, 'quality_base': 4.7},
        {'name': 'Flex Manufacturing', 'country': 'Singapore', 'lead_base': 14, 'quality_base': 4.3},
        {'name': 'Jabil Circuit', 'country': 'USA', 'lead_base': 6, 'quality_base': 4.4},
        {'name': 'Celestica Inc', 'country': 'Canada', 'lead_base': 9, 'quality_base': 4.5},
        {'name': 'Sanmina Corp', 'country': 'USA', 'lead_base': 7, 'quality_base': 4.6},
        {'name': 'Benchmark Electronics', 'country': 'USA', 'lead_base': 8, 'quality_base': 4.4},
        {'name': 'Wistron Corp', 'country': 'Taiwan', 'lead_base': 11, 'quality_base': 4.3},
        {'name': 'Pegatron Corp', 'country': 'Taiwan', 'lead_base': 13, 'quality_base': 4.2},
        {'name': 'Quanta Computer', 'country': 'Taiwan', 'lead_base': 10, 'quality_base': 4.4},
        {'name': 'Compal Electronics', 'country': 'Taiwan', 'lead_base': 12, 'quality_base': 4.1},
        {'name': 'ASE Group', 'country': 'Taiwan', 'lead_base': 9, 'quality_base': 4.5},
        {'name': 'TSMC Supply', 'country': 'Taiwan', 'lead_base': 6, 'quality_base': 4.8},
        {'name': 'Samsung Electronics', 'country': 'South Korea', 'lead_base': 8, 'quality_base': 4.7},
        {'name': 'LG Electronics', 'country': 'South Korea', 'lead_base': 10, 'quality_base': 4.5},
        {'name': 'Hyundai Mobis', 'country': 'South Korea', 'lead_base': 7, 'quality_base': 4.6},
        {'name': 'Continental AG', 'country': 'Germany', 'lead_base': 9, 'quality_base': 4.7}
    ]
    
    suppliers_data = []
    for i, supplier_info in enumerate(realistic_suppliers):
        supplier_id = f'SUP_{i+1:03d}'
        # Add realistic variance to lead times and quality
        lead_time = max(3, supplier_info['lead_base'] + np.random.randint(-2, 3))
        quality = min(5.0, max(3.5, supplier_info['quality_base'] + np.random.uniform(-0.2, 0.2)))
        
        suppliers_data.append({
            'supplier_id': supplier_id,
            'supplier_name': supplier_info['name'],
            'lead_time_target': lead_time,
            'quality_rating': round(quality, 1),
            'updated_timestamp': datetime.now()
        })
    
    suppliers_df = pd.DataFrame(suppliers_data)
    
    # Generate realistic products with proper cost structure
    products_data = []
    categories = ['Electronics', 'Automotive', 'Industrial', 'Consumer Goods', 'Raw Materials']
    
    # Realistic cost ranges by category
    cost_ranges = {
        'Electronics': {'A': (200, 800), 'B': (50, 200), 'C': (10, 50)},
        'Automotive': {'A': (150, 600), 'B': (40, 150), 'C': (8, 40)},
        'Industrial': {'A': (300, 1000), 'B': (75, 300), 'C': (15, 75)},
        'Consumer Goods': {'A': (100, 400), 'B': (25, 100), 'C': (5, 25)},
        'Raw Materials': {'A': (50, 200), 'B': (15, 50), 'C': (3, 15)}
    }
    
    for i in range(1, 101):
        product_id = f'PROD_{i:03d}'
        category = np.random.choice(categories)
        abc_class = np.random.choice(['A', 'B', 'C'], p=[0.15, 0.25, 0.6])  # More realistic distribution
        
        # Realistic cost based on category and class
        cost_min, cost_max = cost_ranges[category][abc_class]
        unit_cost = np.random.uniform(cost_min, cost_max)
        
        products_data.append({
            'product_id': product_id,
            'product_name': f'Product {product_id}',
            'category': category,
            'abc_class': abc_class,
            'unit_cost': round(unit_cost, 2),
            'updated_timestamp': datetime.now()
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
        planned_delivery = order_date + timedelta(days=int(supplier['lead_time_target']))
        
        # Actual delivery (some delays based on supplier performance)
        delay_probability = 0.15 if supplier['quality_rating'] > 4.0 else 0.3
        if np.random.random() < delay_probability:
            actual_delay = np.random.randint(1, 5)
            delivery_date = planned_delivery + timedelta(days=actual_delay)
        else:
            delivery_date = planned_delivery - timedelta(days=np.random.randint(0, 2))
        
        # Realistic quantity based on ABC class and category
        if product['abc_class'] == 'A':
            quantity = np.random.randint(25, 150)  # High-value items ordered in smaller quantities
        elif product['abc_class'] == 'B':
            quantity = np.random.randint(75, 400)
        else:
            quantity = np.random.randint(150, 800)  # Low-value items in bulk
        
        # Calculate costs
        total_value = quantity * product['unit_cost']
        lead_time = (delivery_date - order_date).days
        
        # Realistic compliance rates based on supplier quality
        compliance_rate = 0.75 + (supplier['quality_rating'] - 3.5) * 0.1  # Better suppliers = higher compliance
        mrp_compliance = 'Compliant' if np.random.random() < compliance_rate else 'Non-Compliant'
        setup_compliance = 'Compliant' if np.random.random() < (compliance_rate + 0.05) else 'Non-Compliant'
        
        # Realistic defect rate (0-3% for most suppliers)
        if supplier['quality_rating'] >= 4.5:
            defect_rate = np.random.uniform(0, 0.8)  # Excellent suppliers
        elif supplier['quality_rating'] >= 4.0:
            defect_rate = np.random.uniform(0, 1.5)  # Good suppliers
        else:
            defect_rate = np.random.uniform(0.5, 3.0)  # Average suppliers
        
        # Realistic quality costs and penalties
        quality_cost = (defect_rate / 100) * total_value * 0.1 if defect_rate > 0.5 else 0
        late_penalty = max(0, (lead_time - int(supplier['lead_time_target'])) * total_value * 0.001)
        
        # Generate unique order ID with timestamp
        timestamp = int(datetime.now().timestamp())
        orders_data.append({
            'order_id': f'ORD_{timestamp}_{i:04d}',
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
            'late_penalty': round(late_penalty, 2),
            'created_timestamp': datetime.now()
        })
    
    orders_df = pd.DataFrame(orders_data)
    
    # Generate inventory with dynamic stock levels
    inventory_data = []
    for _, product in products_df.iterrows():
        # Realistic stock levels based on ABC class and category
        if product['abc_class'] == 'A':
            current_stock = np.random.randint(30, 300)  # Lower stock for expensive items
            safety_stock = np.random.randint(10, 50)
        elif product['abc_class'] == 'B':
            current_stock = np.random.randint(80, 600)
            safety_stock = np.random.randint(25, 120)
        else:
            current_stock = np.random.randint(150, 1200)
            safety_stock = np.random.randint(50, 250)
        
        # Realistic EOQ based on demand and cost
        annual_demand = np.random.randint(500, 5000)
        ordering_cost = 50  # Fixed ordering cost
        carrying_cost_rate = 0.20  # 20% carrying cost
        eoq = int(np.sqrt(2 * annual_demand * ordering_cost / (product['unit_cost'] * carrying_cost_rate)))
        eoq = max(10, min(eoq, 1000))  # Realistic bounds
        
        # Reorder point based on lead time demand
        avg_daily_demand = annual_demand / 365
        avg_lead_time = 10  # Average lead time
        rop = int(avg_daily_demand * avg_lead_time) + safety_stock
        
        # Stock status
        if current_stock < safety_stock:
            stock_status = 'Critical'
        elif current_stock < rop:
            stock_status = 'Low'
        else:
            stock_status = 'Normal'
        
        inventory_value = current_stock * product['unit_cost']
        carrying_cost = inventory_value * carrying_cost_rate
        
        inventory_data.append({
            'product_id': product['product_id'],
            'current_stock': current_stock,
            'safety_stock': safety_stock,
            'eoq': eoq,
            'rop': rop,
            'inventory_value': round(inventory_value, 2),
            'carrying_cost': round(carrying_cost, 2),
            'stock_status': stock_status,
            'updated_timestamp': datetime.now()
        })
    
    inventory_df = pd.DataFrame(inventory_data)
    
    return orders_df, inventory_df, suppliers_df, products_df

def setup_logging():
    """Setup logging with last 30 lines in current_log.txt, rest in archived_logs.txt"""
    os.makedirs('logs', exist_ok=True)
    
    current_log_path = 'logs/current_log.txt'
    archive_log_path = 'logs/archived_logs.txt'
    
    # Read existing current log
    if os.path.exists(current_log_path):
        with open(current_log_path, 'r') as f:
            lines = f.readlines()
        
        # If more than 30 lines, archive the excess
        if len(lines) > 30:
            with open(archive_log_path, 'a') as archive:
                archive.writelines(lines[:-30])
            
            # Keep only last 30 lines in current log
            with open(current_log_path, 'w') as current:
                current.writelines(lines[-30:])
    
    # Setup logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(current_log_path, mode='a'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_etl_pipeline():
    """Main ETL pipeline function with comprehensive logging"""
    logger = setup_logging()
    
    logger.info("Starting ETL pipeline")
    
    try:
        # Extract & Transform
        logger.info("Generating incremental data")
        orders_df, inventory_df, suppliers_df, products_df = generate_incremental_data()
        logger.info(f"Generated {len(orders_df)} orders, {len(inventory_df)} inventory items")
        
        # Skip database in CI environment
        if os.environ.get('GITHUB_ACTIONS'):
            logger.info("CI environment detected, saving to CSV only")
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            logger.info("ETL pipeline completed successfully (CSV mode)")
            return True
        
        # Create database tables
        logger.info("Creating database tables")
        if not create_tables():
            logger.error("Failed to create database tables, saving to CSV")
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            return False
        
        # Load to database
        logger.info("Loading data to database")
        if load_data_to_db(orders_df, inventory_df, suppliers_df, products_df):
            logger.info("ETL pipeline completed successfully")
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            logger.info("Data backup saved to CSV files")
            return True
        else:
            logger.error("Database load failed, saving to CSV only")
            save_to_csv(orders_df, inventory_df, suppliers_df, products_df)
            return False
            
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        return False

def save_to_csv(orders_df, inventory_df, suppliers_df, products_df):
    """Append new data to existing CSV files with business constraints"""
    os.makedirs('data', exist_ok=True)
    
    # Append new orders with data quality checks
    if os.path.exists('data/orders.csv'):
        existing_orders = pd.read_csv('data/orders.csv', parse_dates=['order_date', 'planned_delivery', 'delivery_date'])
        
        # Limit total orders to prevent unlimited growth (keep last 6 months)
        cutoff_date = datetime.now() - timedelta(days=180)
        existing_orders = existing_orders[existing_orders['order_date'] >= cutoff_date.strftime('%Y-%m-%d')]
        
        combined_orders = pd.concat([existing_orders, orders_df], ignore_index=True)
        combined_orders = combined_orders.drop_duplicates(subset=['order_id'], keep='last')
        
        # Ensure realistic data bounds
        combined_orders['defect_rate'] = combined_orders['defect_rate'].clip(0, 5)  # Max 5% defect rate
        combined_orders['lead_time'] = combined_orders['lead_time'].clip(1, 45)  # 1-45 days lead time
        
        combined_orders.to_csv('data/orders.csv', index=False)
        print(f"Total orders after append: {len(combined_orders)} (last 6 months)")
    else:
        orders_df.to_csv('data/orders.csv', index=False)
        print(f"Initial orders file created with {len(orders_df)} orders")
    
    # Update inventory with realistic bounds
    inventory_df['current_stock'] = inventory_df['current_stock'].clip(0, 10000)
    inventory_df['safety_stock'] = inventory_df['safety_stock'].clip(5, 1000)
    inventory_df.to_csv('data/inventory.csv', index=False)
    
    # Update suppliers with quality bounds
    suppliers_df['quality_rating'] = suppliers_df['quality_rating'].clip(3.0, 5.0)
    suppliers_df['lead_time_target'] = suppliers_df['lead_time_target'].clip(1, 30)
    suppliers_df.to_csv('data/suppliers.csv', index=False)
    
    # Update products with cost bounds
    products_df['unit_cost'] = products_df['unit_cost'].clip(1, 2000)
    products_df.to_csv('data/products.csv', index=False)
    
    print(f"Data appended: {len(orders_df)} new orders added with realistic constraints")

if __name__ == "__main__":
    run_etl_pipeline()