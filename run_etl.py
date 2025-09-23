#!/usr/bin/env python3
"""
Simple script to run ETL pipeline and show data growth
"""
import subprocess
import time
from datetime import datetime

def run_etl():
    """Run the ETL pipeline and show results"""
    print(f"\n{'='*50}")
    print(f"Running ETL at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(['python', 'etl_data_generator.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ ETL completed successfully")
            print(result.stdout)
        else:
            print("❌ ETL failed")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running ETL: {e}")

def show_data_stats():
    """Show current data statistics"""
    try:
        # Count orders
        with open('data/orders.csv', 'r') as f:
            order_count = len(f.readlines()) - 1  # Subtract header
        
        # Show latest supplier update
        with open('data/suppliers.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                latest_supplier = lines[1].split(',')
                supplier_name = latest_supplier[1]
                quality = latest_supplier[3]
                timestamp = latest_supplier[4].strip()
        
        print(f"\n📊 Current Data Stats:")
        print(f"   • Total Orders: {order_count}")
        print(f"   • Latest Supplier Update: {supplier_name} (Quality: {quality})")
        print(f"   • Last Updated: {timestamp}")
        
    except Exception as e:
        print(f"❌ Error reading data stats: {e}")

if __name__ == "__main__":
    print("🚀 Supply Chain ETL Runner")
    print("This script will run the ETL pipeline and show data evolution")
    
    # Run ETL once
    run_etl()
    show_data_stats()
    
    print(f"\n💡 To run ETL continuously, use:")
    print(f"   python run_etl.py --continuous")
    
    # Check if continuous mode requested
    import sys
    if '--continuous' in sys.argv:
        print(f"\n🔄 Running in continuous mode (every 30 seconds)")
        print(f"   Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(30)
                run_etl()
                show_data_stats()
        except KeyboardInterrupt:
            print(f"\n👋 ETL runner stopped")