import psycopg2
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Free PostgreSQL connection (Neon.tech - 10GB free)
def get_db_connection():
    """Connect to free PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=st.secrets.get("DB_HOST", ""),
            database=st.secrets.get("DB_NAME", ""),
            user=st.secrets.get("DB_USER", ""),
            password=st.secrets.get("DB_PASSWORD", ""),
            port=st.secrets.get("DB_PORT", "5432")
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def create_tables():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id VARCHAR(50) PRIMARY KEY,
            supplier_id VARCHAR(50),
            product_id VARCHAR(50),
            category VARCHAR(50),
            abc_class VARCHAR(10),
            order_date DATE,
            planned_delivery DATE,
            delivery_date DATE,
            quantity INTEGER,
            unit_cost DECIMAL(10,2),
            total_value DECIMAL(12,2),
            lead_time INTEGER,
            mrp_compliance VARCHAR(20),
            setup_compliance VARCHAR(20),
            defect_rate DECIMAL(5,2),
            quality_cost DECIMAL(10,2),
            late_penalty DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Inventory table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id VARCHAR(50) PRIMARY KEY,
            current_stock INTEGER,
            safety_stock INTEGER,
            eoq INTEGER,
            rop INTEGER,
            inventory_value DECIMAL(12,2),
            carrying_cost DECIMAL(10,2),
            stock_status VARCHAR(20),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Suppliers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id VARCHAR(50) PRIMARY KEY,
            supplier_name VARCHAR(100),
            lead_time_target INTEGER,
            quality_rating DECIMAL(3,1),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(50) PRIMARY KEY,
            product_name VARCHAR(100),
            category VARCHAR(50),
            abc_class VARCHAR(10),
            unit_cost DECIMAL(10,2),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Table creation failed: {e}")
        return False

def load_data_to_db(orders_df, inventory_df, suppliers_df, products_df):
    """Load dataframes to PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        # Clear existing data (for daily refresh)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'")
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM suppliers")
        cursor.execute("DELETE FROM products")
        
        # Load new data
        orders_df.to_sql('orders', conn, if_exists='append', index=False, method='multi')
        inventory_df.to_sql('inventory', conn, if_exists='append', index=False, method='multi')
        suppliers_df.to_sql('suppliers', conn, if_exists='append', index=False, method='multi')
        products_df.to_sql('products', conn, if_exists='append', index=False, method='multi')
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Data loaded successfully at {datetime.now()}")
        return True
    except Exception as e:
        print(f"Data loading failed: {e}")
        return False

def load_data_from_db():
    """Load data from PostgreSQL for the app"""
    conn = get_db_connection()
    if not conn:
        # Fallback to CSV files
        return load_csv_fallback()
    
    try:
        orders = pd.read_sql("SELECT * FROM orders ORDER BY order_date DESC", conn)
        inventory = pd.read_sql("SELECT * FROM inventory", conn)
        suppliers = pd.read_sql("SELECT * FROM suppliers", conn)
        products = pd.read_sql("SELECT * FROM products", conn)
        
        # Convert date columns
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        orders['planned_delivery'] = pd.to_datetime(orders['planned_delivery'])
        orders['delivery_date'] = pd.to_datetime(orders['delivery_date'])
        
        conn.close()
        return orders, inventory, products, suppliers
    except Exception as e:
        print(f"Database load failed: {e}")
        return load_csv_fallback()

def load_csv_fallback():
    """Fallback to CSV files if database fails"""
    try:
        orders = pd.read_csv('data/orders.csv', parse_dates=['order_date', 'planned_delivery', 'delivery_date'])
        inventory = pd.read_csv('data/inventory.csv')
        products = pd.read_csv('data/products.csv')
        suppliers = pd.read_csv('data/suppliers.csv')
        return orders, inventory, products, suppliers
    except:
        return None, None, None, None