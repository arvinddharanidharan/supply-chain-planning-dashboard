#!/usr/bin/env python3
"""
Supply Chain Planning Dashboard Launcher
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'streamlit', 'statsmodels']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Please install: pip install -r requirements.txt")
        return False
    
    print("All required packages available")
    return True

def check_data():
    """Check if data files exist"""
    data_files = ['data/orders.csv', 'data/inventory.csv', 'data/products.csv', 'data/suppliers.csv']
    missing_files = [f for f in data_files if not os.path.exists(f)]
    
    if missing_files:
        print("Missing data files. Generating...")
        try:
            subprocess.run([sys.executable, 'data_generator.py'], check=True)
            print("Data generated successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to generate data")
            return False
    
    print("Data files found")
    return True

def main():
    print("Supply Chain Planning & KPI Dashboard")
    print("=" * 50)
    
    if not check_requirements():
        return
    
    if not check_data():
        return
    
    print("\nStarting Supply Chain Planning Dashboard...")
    print("Dashboard will open in your browser at http://localhost:8501")
    print("\nDashboard Features:")
    print("   - Real-time KPI monitoring (OTD%, Process Compliance)")
    print("   - Supplier performance analytics")
    print("   - Inventory optimization recommendations")
    print("   - Process compliance tracking")
    print("   - Automated reorder alerts")
    print("\nTo stop the dashboard, press Ctrl+C")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()