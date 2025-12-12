# This simulates a production environment where 
# I run a script (e.g., daily or weekly) to refresh your analysis.

# Import the libraries 
import pandas as pd 
import numpy as np
import joblib 
from sqlalchemy import create_engine
import os 
from dotenv import load_dotenv 
from pathlib import Path

# Setup & Config
load_dotenv()

# Database Connection 
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_ANALYTICS")

conn_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine =create_engine(conn_string)

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR/'models'/'kmeans_model.pkl'
SCALER_PATH = BASE_DIR/'models'/'scaler.pkl'

# Create a function to dynamically assign the segment/persona names to clusters 
def assign_segment_name(row,cluster_centers):
    """
    Assigns a segment name based on a combination of the K-Means Cluster
    CONSTRAINT WITH business rules
    - (1) Champions: High Monetary + High Frequency + Low Recency
    - (2) New / Promising : Low Recency (Negative scaled value) + Low Frequency
    - (3) Lost Whales: High Recency + High Monetary + Low Frequency
    - (4) Loyal / Active: High Freq + Low Recency  
    - (5) Churn : Low Monetary + High Recency + Low Freq  
    
    Args:
        row (pd.Series): A single row of the dataframe with 'recency', 'frequency', 'monetary', and 'Cluster'.
        cluster_centers (np.array): The centroids from the model (used for fallback/context).
    
    Returns:
        str: The business segment name.
    """  
    # Extract raw values 
    recency = row['recency']
    freq = row['frequency']
    monetary = row['monetary']
    cluster_id = int(row['Cluster'])

    # Get the centroid for a cluster 
    centroid = cluster_centers[cluster_id]
    r_score = centroid[0] # recency
    f_score = centroid[1] # frequency
    m_score = centroid[2] # monetary
    
    # Setting the base_segment using centroid 
    
    base_segment = 'Lost' # Default 
    
    if m_score > 0.8 and f_score > 0.5 and r_score < 0.5: 
        base_segment = 'Champions'
    elif f_score > 0.2 and r_score < 0.5:
        base_segment = 'Loyal / Active'
    elif r_score < -0.5:
        base_segment = 'New / Promising'

    else:
        base_segment= 'Lost'
    
    # Before getting the centroid it, apply the business rules to override K-mean model's clusters
    # Rule 1: if the recency > 540 days (customers haven't bought for 2 years) --> "Lost" regardless of monetary value
    if recency > 540:
        if base_segment == 'Lost':
            return "Lost"
        else: 
            return f"Lost {base_segment}"
    # Rule 2: if the customers are very new (< 120 days) and have low freq, keep them as "New"
    elif recency < 120 and freq ==1: 
        return 'New / Promising'
    return base_segment

# Create a function for run_inference
def run_inference():
    # Load new data from SQL view 
    print("Reading updated...")
    df_rmf = pd.read_sql('SELECT * FROM view_rmf_base',engine)
    
    if df_rmf.empty:
        print("No data found in R-M-F view.")
    else: 
        print("First 5 rows of updated Customer RMF data")
        print(df_rmf.head(5)) 
    # Load re-trained model 
    try:
        kmeans_model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    except Exception as e:
        print(f"Error occurred: {e}. Please run and check Notebook 04.")
        return
    # Preprocessing: Transform the data to normalize the distribution 
    print("Preprocessing data...")
    df_log = df_rmf[['recency','frequency','monetary']].copy()
    df_log = np.log1p(df_log)
    
    # Scale using the LOADED scaler model
    rmf_scaled = scaler.transform(df_log)
    df_rmf_scaled = pd.DataFrame(rmf_scaled,columns=['recency','frequency','monetary'])
    
    # Predict segment with the loaded model 
    try:
        print("Predict with K-Means model...")
        df_rmf['Cluster'] = kmeans_model.predict(df_rmf_scaled)
    except Exception as e:
        print(f"Error occured: {e}. Stop the pipeline.")
        return

    # Map the segment names
    print("Generating dynamic segment map...")
    centers = kmeans_model.cluster_centers_
    
    # Apply the segment name function 
    df_rmf['Segment_name'] = df_rmf.apply(lambda row: assign_segment_name(row,centers), axis=1)
    
    df_segment = df_rmf.groupby('Cluster')['Segment_name'].unique()
    print("The final segmentation:")
    print(df_segment)
    # Create a column with less granularity 
    df_rmf['Segment_group'] = df_rmf['Segment_name'].apply(lambda x: "Lost" if "Lost" in str(x) else x)

    # Save to production table 
    print("Save results to 'analytics_rmf_segments'...")
    df_rmf.to_sql('analytics_rmf_segments',engine, if_exists='replace',index=False)
    print("Pipeline Completed. Data is refreshed.")

if __name__ == "__main__":
    run_inference()

    