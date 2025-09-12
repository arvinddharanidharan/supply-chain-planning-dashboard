import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_supply_chain_data(n_orders=5000, n_products=100, n_suppliers=20):
    """Generate comprehensive supply chain dataset"""
    np.random.seed(42)
    
    # Product master data
    products = []
    for i in range(n_products):
        products.append({
            'product_id': f'P{i+1:04d}',
            'product_name': f'Product_{i+1}',
            'category': np.random.choice(['Raw Material', 'Component', 'Finished Good']),
            'unit_cost': np.random.uniform(5, 500),
            'abc_class': np.random.choice(['A', 'B', 'C'], p=[0.2, 0.3, 0.5])
        })
    
    # Supplier master data
    suppliers = []
    for i in range(n_suppliers):
        suppliers.append({
            'supplier_id': f'SUP{i+1:03d}',
            'supplier_name': f'Supplier_{i+1}',
            'country': np.random.choice(['USA', 'Germany', 'China', 'India', 'Mexico']),
            'quality_rating': np.random.uniform(85, 99),
            'lead_time_target': np.random.randint(5, 30)
        })
    
    # Generate orders data
    orders_data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(n_orders):
        product = np.random.choice(products)
        supplier = np.random.choice(suppliers)
        
        order_date = start_date + timedelta(days=np.random.randint(0, 365))
        planned_delivery = order_date + timedelta(days=supplier['lead_time_target'])
        
        # Simulate actual delivery with some variance
        lead_time_variance = np.random.normal(0, 2)
        actual_delivery = planned_delivery + timedelta(days=int(lead_time_variance))
        
        quantity = np.random.randint(10, 1000)
        unit_price = product['unit_cost'] * np.random.uniform(0.9, 1.1)
        
        # Quality metrics
        defect_rate = np.random.uniform(0, 5) if supplier['quality_rating'] < 95 else np.random.uniform(0, 1)
        
        # Process compliance
        mrp_compliance = np.random.choice(['Compliant', 'Non-Compliant'], p=[0.85, 0.15])
        setup_compliance = np.random.choice(['Compliant', 'Non-Compliant'], p=[0.90, 0.10])
        
        orders_data.append({
            'order_id': f'ORD{i+1:06d}',
            'product_id': product['product_id'],
            'supplier_id': supplier['supplier_id'],
            'order_date': order_date,
            'planned_delivery': planned_delivery,
            'delivery_date': actual_delivery,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_value': quantity * unit_price,
            'lead_time': (actual_delivery - order_date).days,
            'lead_time_target': supplier['lead_time_target'],
            'defect_rate': defect_rate,
            'mrp_compliance': mrp_compliance,
            'setup_compliance': setup_compliance,
            'category': product['category'],
            'abc_class': product['abc_class']
        })
    
    # Generate inventory data
    inventory_data = []
    for product in products:
        current_stock = np.random.randint(0, 2000)
        safety_stock = np.random.randint(50, 300)
        eoq = np.random.randint(100, 800)
        
        # Calculate reorder point
        avg_demand = np.random.uniform(10, 100)
        avg_lead_time = np.random.randint(5, 25)
        rop = avg_demand * avg_lead_time + safety_stock
        
        inventory_data.append({
            'product_id': product['product_id'],
            'current_stock': current_stock,
            'safety_stock': safety_stock,
            'eoq': eoq,
            'rop': rop,
            'avg_demand': avg_demand,
            'stock_status': 'Critical' if current_stock < safety_stock else 
                          'Low' if current_stock < rop else 'Normal'
        })
    
    # Convert to DataFrames
    orders_df = pd.DataFrame(orders_data)
    inventory_df = pd.DataFrame(inventory_data)
    products_df = pd.DataFrame(products)
    suppliers_df = pd.DataFrame(suppliers)
    
    return orders_df, inventory_df, products_df, suppliers_df

if __name__ == "__main__":
    orders, inventory, products, suppliers = generate_supply_chain_data()
    
    # Save datasets
    orders.to_csv('data/orders.csv', index=False)
    inventory.to_csv('data/inventory.csv', index=False)
    products.to_csv('data/products.csv', index=False)
    suppliers.to_csv('data/suppliers.csv', index=False)
    
    print(f"✅ Generated datasets:")
    print(f"   📦 Orders: {len(orders)} records")
    print(f"   📊 Inventory: {len(inventory)} items")
    print(f"   🏭 Products: {len(products)} items")
    print(f"   🚚 Suppliers: {len(suppliers)} suppliers")