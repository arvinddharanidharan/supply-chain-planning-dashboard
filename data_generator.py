import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_supply_chain_data(n_orders=5000, n_products=100, n_suppliers=20):
    """Create realistic sample data for the supply chain dashboard"""
    np.random.seed(42)
    
    # Create a list of products with their basic information
    products = []
    for i in range(n_products):
        unit_cost = np.random.uniform(5, 500)
        products.append({
            'product_id': f'P{i+1:04d}',
            'product_name': f'Product_{i+1}',
            'category': np.random.choice(['Raw Material', 'Component', 'Finished Good']),
            'unit_cost': unit_cost,
            'abc_class': np.random.choice(['A', 'B', 'C'], p=[0.2, 0.3, 0.5]),
            'carrying_cost_rate': np.random.uniform(0.15, 0.35),  # How much it costs to store this item per year
            'scrap_cost': unit_cost * np.random.uniform(0.8, 1.2)  # Cost to throw away broken items
        })
    
    # Create a list of suppliers with their performance info
    suppliers = []
    for i in range(n_suppliers):
        suppliers.append({
            'supplier_id': f'SUP{i+1:03d}',
            'supplier_name': f'Supplier_{i+1}',
            'country': np.random.choice(['USA', 'Germany', 'China', 'India', 'Mexico']),
            'quality_rating': np.random.uniform(85, 99),
            'lead_time_target': np.random.randint(5, 30),
            'payment_terms': np.random.choice([30, 45, 60, 90]),  # How many days we have to pay them
            'discount_rate': np.random.uniform(0, 0.05)  # Discount we get for paying early
        })
    
    # Create individual purchase orders with realistic details
    orders_data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(n_orders):
        product = np.random.choice(products)
        supplier = np.random.choice(suppliers)
        
        order_date = start_date + timedelta(days=np.random.randint(0, 365))
        planned_delivery = order_date + timedelta(days=supplier['lead_time_target'])
        
        # Sometimes deliveries are late, sometimes on time
        lead_time_variance = np.random.normal(0, 1.5)  # Add some randomness to delivery times
        actual_delivery = planned_delivery + timedelta(days=max(0, int(lead_time_variance)))
        
        quantity = np.random.randint(50, 500)  # How many items we ordered
        unit_price = product['unit_cost'] * np.random.uniform(0.95, 1.05)  # Price varies slightly from standard cost
        total_value = quantity * unit_price
        
        # Better suppliers have fewer defective items
        if supplier['quality_rating'] > 95:
            defect_rate = np.random.uniform(0, 0.5)
        elif supplier['quality_rating'] > 90:
            defect_rate = np.random.uniform(0, 2)
        else:
            defect_rate = np.random.uniform(0, 4)
        
        # Most of the time we follow proper processes
        mrp_compliance = np.random.choice(['Compliant', 'Non-Compliant'], p=[0.92, 0.08])  # Did we follow planning rules?
        setup_compliance = np.random.choice(['Compliant', 'Non-Compliant'], p=[0.95, 0.05])  # Did we set up production correctly?
        
        # Calculate the costs of problems
        defective_units = quantity * (defect_rate / 100)  # How many items were broken
        quality_cost = defective_units * product['scrap_cost']  # Cost of throwing away broken items
        late_delivery_penalty = total_value * 0.02 if actual_delivery > planned_delivery else 0  # Penalty for late delivery
        
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
    
    # Create current stock levels for each product
    inventory_data = []
    for product in products:
        current_stock = np.random.randint(200, 3000)  # How many we have in stock right now
        safety_stock = np.random.randint(50, 300)  # Minimum amount we want to keep in stock
        eoq = np.random.randint(200, 800)  # Optimal order quantity to minimize costs
        
        # Figure out when we should reorder
        avg_demand = np.random.uniform(20, 80)  # How many we typically use per day
        avg_lead_time = np.random.randint(7, 21)  # How long it takes to get new stock
        rop = avg_demand * avg_lead_time + safety_stock  # When to reorder
        
        # Calculate the value and cost of holding inventory
        inventory_value = current_stock * product['unit_cost']  # Total value of stock on hand
        carrying_cost = inventory_value * product['carrying_cost_rate']  # Annual cost to store this inventory
        
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
    
    # Turn our data into tables that pandas can work with
    orders_df = pd.DataFrame(orders_data)
    inventory_df = pd.DataFrame(inventory_data)
    products_df = pd.DataFrame(products)
    suppliers_df = pd.DataFrame(suppliers)
    
    return orders_df, inventory_df, products_df, suppliers_df

if __name__ == "__main__":
    orders, inventory, products, suppliers = generate_supply_chain_data()
    
    # Save all the data to CSV files
    orders.to_csv('data/orders.csv', index=False)
    inventory.to_csv('data/inventory.csv', index=False)
    products.to_csv('data/products.csv', index=False)
    suppliers.to_csv('data/suppliers.csv', index=False)
    
    print(f"Generated datasets:")
    print(f"Orders: {len(orders)} records")
    print(f"Inventory: {len(inventory)} items")
    print(f"Products: {len(products)} items")
    print(f"Suppliers: {len(suppliers)} suppliers")