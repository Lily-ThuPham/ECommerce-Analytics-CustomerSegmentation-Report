# This simulates a production environment where 
# I run a script (e.g., daily or weekly) to refresh your analysis.

# Import the libraries 
import pandas as pd 
import numpy as np
import joblib 
from sqlalchemy import create_engine
import os 
from dotenv import load_dotenv 

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

MODEL_PATH = 'models/kmeans_model.pkl'
SCALER_PATH = 'models/scaler.pkl'

# Create a function to dynamically assign the segment/persona names to clusters 
def assign_segment_name(cluster_centers,cluster_id):
    """
    Dynamically assigns a business name to a cluster ID based on its centroid values.
    Logic (based on Scaled Log Data):
    - High Monetary + High Frequency = Champions
    - Low Recency (Negative scaled value) + Low Frequency = New / Promising
    - High Recency (Positive scaled value) = Lost
    - Everything else = Loyal / Active
    
    Args:
        cluster_centers (np.array): The array of centroids from kmeans.cluster_centers_
        cluster_id (int): The cluster ID to name.
    
    Returns:
        str: The business segment name.
    """   
    # Get the centroid for a cluster 
    centroid = cluster_centers[cluster_id]
    
    r_score = centroid[0] # recency
    m_score = centroid[1] # monetary
    f_score = centroid[2] # frequency 
    
    if m_score > 0.5 and f_score > 0.5:
        return 'Champions'
    elif r_score > 0.5:
        return 'Lost'
    elif r_score < -0.5 and f_score < 0:
        return 'New / Promising'
    else:
        return 'Loyal / Active'

# Create a function 
def run_interence():
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
    except FileNotFoundError:
        print("Model not found. Please run and check Notebook 04.")
        return
    # Preprocessing: Transform the data to normalize the distribution 
    print("Preprocessing data...")
    df_log = df_rmf[['recency','frequency','monetary']].copy()
    df_log = np.log1p(df_log)
    
    # Scale using the LOADED scaler model
    rmf_scaled = scaler.transform(df_log)
    
    # Predict segment with the loaded model 
    print("Predict with K-Means model...")
    df_rmf['Cluster'] = kmeans_model.predict(rmf_scaled)

    # Map the segment names
    print("Generating dynamic segment map...")
    centers = kmeans_model.cluster_centers_
    num_clusters = len(centers)
    dynamic_map = {}
    
    for i in range(num_clusters):
        dynamic_map[i] = assign_segment_name(centers,i)
        
    print(f"Map created: {dynamic_map}")
    df_rmf['Segment_name'] = df_rmf['Cluster'].map(dynamic_map)
    
    # Save to production table 
    print("Save results to 'analytics_rmf_segments'...")
    df_rmf.to_sql('analytics_rmf_segments',engine, if_exists='replace',index=False)
    print("Pipeline Completed. Data is refreshed")

if __name__ == "__main__":
    run_interence()

    