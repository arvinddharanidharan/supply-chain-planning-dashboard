#!/usr/bin/env python3
import pandas as pd
from database import load_data_from_db

def main():
    print("Loading data from database...")
    orders, inventory, products, suppliers = load_data_from_db()
    
    if orders is not None:
        print("\n=== ORDERS TABLE ===")
        print(orders.head(10))
        print(f"Total orders: {len(orders)}")
        
        print("\n=== INVENTORY TABLE ===")
        print(inventory.head(10))
        print(f"Total inventory items: {len(inventory)}")
        
        print("\n=== PRODUCTS TABLE ===")
        print(products.head(10))
        print(f"Total products: {len(products)}")
        
        print("\n=== SUPPLIERS TABLE ===")
        print(suppliers.head(10))
        print(f"Total suppliers: {len(suppliers)}")
    else:
        print("Failed to load data from database")

if __name__ == "__main__":
    main()