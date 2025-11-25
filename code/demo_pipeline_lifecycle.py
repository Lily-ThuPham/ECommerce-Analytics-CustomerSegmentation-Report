import pandas as pd
import random
import time
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the current directory to sys.path to allow importing from sibling scripts
sys.path.append(str(Path(__file__).resolve().parent))

# Import the inference logic directly
from inference_pipeline import run_inference

load_dotenv()

# Database Connection
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_ANALYTICS")

conn_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(conn_string)

def simulate_transactions():
    print("\n1.Simulating New Transactions")
    
    orders_list = []
    items_list = []
    
    # Define Test Cases
    # Customer 1: The "Whale" (High Spend) -> Should become 'Champions'
    # Customer 2: The "Standard" (Low Spend) -> Should become 'New / Promising' or 'Loyal'
    test_cases = [
        {'cust_sk': 1, 'price': 5000.0, 'desc': 'High Value (Whale)'},
        {'cust_sk': 2, 'price': 50.0,   'desc': 'Low Value (Standard)'}
    ]
    
    for case in test_cases:
        cust_sk = case['cust_sk']
        price = case['price']
        new_order_sk = random.randint(200000, 999999)
        order_id = f'simulated_{new_order_sk}'
        
        print(f"   Generating Order #{new_order_sk} for Customer SK {cust_sk} ({case['desc']})...")

        # Order Data
        orders_list.append({
            'order_sk': new_order_sk,
            'customer_sk': cust_sk,
            'order_id': order_id,
            'order_status': 'delivered',
            'order_purchase_timestamp': datetime.now()
        })

        # Item Data
        items_list.append({
            'order_sk': new_order_sk,
            'order_id': order_id,
            'order_item_id': 1,
            'product_sk': 1, 
            'seller_sk': 1,  
            'price': price,
            'freight_value': 15.0
        })

    # Append to Database
    try:
        df_orders = pd.DataFrame(orders_list)
        df_items = pd.DataFrame(items_list)
        
        df_orders.to_sql('fct_orders', engine, if_exists='append', index=False)
        df_items.to_sql('fct_order_items', engine, if_exists='append', index=False)
        print(f"Transactions successfully added to MySQL.")
    except Exception as e:
        print(f"Simulation failed: {e}")
        sys.exit(1) # Stop if simulation fails

def verify_results():
    print("\n3.Verifying Results")
    
    # We check the specific customers we just updated
    target_customers = [1, 2]
    
    # Helper query to get unique_sk from sk
    query = f"""
    SELECT c.customer_sk, s.recency_days, s.Segment_Name, s.monetary_value
    FROM analytics_rfm_segments s
    JOIN dim_customers c ON s.customer_unique_sk = c.customer_unique_sk
    WHERE c.customer_sk IN ({','.join(map(str, target_customers))})
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("Verification Failed: Test customers not found in analytics table.")
            return

        print("\n Latest Customer Profiles:")
        print(df.to_string(index=False))
        print("-" * 30)

        # --- Assertions ---
        # Check Customer 1 (Whale)
        whale = df[df['customer_sk'] == 1].iloc[0]
        if whale['recency_days'] == 0 and whale['Segment_Name'] == 'Champions':
            print("Test Case 1 Passed: Whale Customer is active (Recency=0) and classified as 'Champions'.")
        else:
            print(f"Test Case 1 Warning: Whale Customer is '{whale['Segment_Name']}' with Recency {whale['recency_days']}.")

        # Check Customer 2 (Standard)
        standard = df[df['customer_sk'] == 2].iloc[0]
        if standard['recency_days'] == 0:
             print(f"Test Case 2 Passed: Standard Customer data is fresh (Recency=0). Segment: '{standard['Segment_Name']}'.")
        else:
             print(f"Test Case 2 Failed: Recency is {standard['recency_days']} (Expected 0).")

    except Exception as e:
        print(f"Verification Query Failed: {e}")

if __name__ == "__main__":
    print("Starting End-to-End Pipeline Demo")
    print("=" * 40)
    
    # Step 1: Simulate Data
    simulate_transactions()
    
    # Wait a moment to ensure DB commitment (rarely needed but good practice)
    time.sleep(1)
    
    # Step 2: Run the Inference Engine
    print("\n2.Running Inference Pipeline")
    run_inference()
    
    # Step 3: Test & Verify
    verify_results()
    
    print("\n=" * 40)
    print("✅ Demo Complete!")