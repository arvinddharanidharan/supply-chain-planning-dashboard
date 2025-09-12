import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_supply_chain_data(n_orders=5000, n_products=100, n_suppliers=20):
    """Generate comprehensive supply chain dataset"""
    np.random.seed(42)
    
    # Product master data
    products = []
    for i in range(n_products):
        unit_cost = np.random.uniform(5, 500)
        products.append({
            'product_id': f'P{i+1:04d}',
            'product_name': f'Product_{i+1}',
            'category': np.random.choice(['Raw Material', 'Component', 'Finished Good']),
            'unit_cost': unit_cost,
            'abc_class': np.random.choice(['A', 'B', 'C'], p=[0.2, 0.3, 0.5]),
            'carrying_cost_rate': np.random.uniform(0.15, 0.35),  # Annual carrying cost %
            'scrap_cost': unit_cost * np.random.uniform(0.8, 1.2)  # Cost to scrap defective units
        })
    
    # Supplier master data
    suppliers = []
    for i in range(n_suppliers):
        suppliers.append({
            'supplier_id': f'SUP{i+1:03d}',
            'supplier_name': f'Supplier_{i+1}',
            'country': np.random.choice(['USA', 'Germany', 'China', 'India', 'Mexico']),
            'quality_rating': np.random.uniform(85, 99),
            'lead_time_target': np.random.randint(5, 30),
            'payment_terms': np.random.choice([30, 45, 60, 90]),  # Days
            'discount_rate': np.random.uniform(0, 0.05)  # Early payment discount
        })
    
    # Generate orders data
    orders_data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(n_orders):
        product = np.random.choice(products)
        supplier = np.random.choice(suppliers)
        
        order_date = start_date + timedelta(days=np.random.randint(0, 365))
        planned_delivery = order_date + timedelta(days=supplier['lead_time_target'])
        
        # Simulate actual delivery with some variance (more realistic)
        lead_time_variance = np.random.normal(0, 1.5)  # Reduced variance
        actual_delivery = planned_delivery + timedelta(days=max(0, int(lead_time_variance)))
        
        quantity = np.random.randint(50, 500)  # More realistic order quantities
        unit_price = product['unit_cost'] * np.random.uniform(0.95, 1.05)  # Tighter price variance
        total_value = quantity * unit_price
        
        # Quality metrics (more realistic defect rates)
        if supplier['quality_rating'] > 95:
            defect_rate = np.random.uniform(0, 0.5)
        elif supplier['quality_rating'] > 90:
            defect_rate = np.random.uniform(0, 2)
        else:
            defect_rate = np.random.uniform(0, 4)
        
        # Process compliance (higher compliance rates)
        mrp_compliance = np.random.choice(['Compliant', 'Non-Compliant'], p=[0.92, 0.08])
        setup_compliance = np.random.choice(['Compliant', 'Non-Compliant'], p=[0.95, 0.05])
        
        # Financial calculations
        defective_units = quantity * (defect_rate / 100)
        quality_cost = defective_units * product['scrap_cost']
        late_delivery_penalty = total_value * 0.02 if actual_delivery > planned_delivery else 0
        
        orders_data.append({
            'order_id': f'ORD{i+1:06d}',
            'product_id': product['product_id'],
            'supplier_id': supplier['supplier_id'],
            'order_date': order_date,
            'planned_delivery': planned_delivery,
            'delivery_date': actual_delivery,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_value': total_value,
            'lead_time': (actual_delivery - order_date).days,
            'lead_time_target': supplier['lead_time_target'],
            'defect_rate': defect_rate,
            'mrp_compliance': mrp_compliance,
            'setup_compliance': setup_compliance,
            'category': product['category'],
            'abc_class': product['abc_class'],
            'quality_cost': quality_cost,
            'late_penalty': late_delivery_penalty,
            'defective_units': defective_units
        })
    
    # Generate inventory data
    inventory_data = []
    for product in products:
        current_stock = np.random.randint(50, 1500)  # Avoid zero stock
        safety_stock = np.random.randint(25, 200)  # More realistic safety stock
        eoq = np.random.randint(100, 600)  # More realistic EOQ
        
        # Calculate reorder point (more realistic)
        avg_demand = np.random.uniform(20, 80)
        avg_lead_time = np.random.randint(7, 21)
        rop = avg_demand * avg_lead_time + safety_stock
        
        # Financial calculations
        inventory_value = current_stock * product['unit_cost']
        carrying_cost = inventory_value * product['carrying_cost_rate']
        
        inventory_data.append({
            'product_id': product['product_id'],
            'current_stock': current_stock,
            'safety_stock': safety_stock,
            'eoq': eoq,
            'rop': rop,
            'avg_demand': avg_demand,
            'stock_status': 'Critical' if current_stock < safety_stock else 
                          'Low' if current_stock < rop else 'Normal',
            'inventory_value': inventory_value,
            'carrying_cost': carrying_cost
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
    
    print(f"Generated datasets:")
    print(f"Orders: {len(orders)} records")
    print(f"Inventory: {len(inventory)} items")
    print(f"Products: {len(products)} items")
    print(f"Suppliers: {len(suppliers)} suppliers")