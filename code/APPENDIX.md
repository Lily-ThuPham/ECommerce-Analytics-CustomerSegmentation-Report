# Appendix: Project Framework & Technical Architecture
This document outlines the analytics framework I am using to guide the analysis of the Olist e-commerce dataset. The goal is to ensure that my exploratory data analysis (EDA) and final Power BI reports are focused, efficient, and directly answer key business questions.

For the complete analysis and actionable recommendations, see the full report: [Olist E-Commerce: Full-Stack Analytics & Customer Segmentation](../README.md). 

## _**1. Data Architecture & ETL Strategy**_

This project simulates a comprehensive Business Intelligence (BI) workflow, engineered to transform raw, disconnected logs into a high-performance Star Schema optimized for analytics and machine learning.

### **1.1 About the Dataset**

The analysis is based on the Olist E-Commerce Dataset, a relational collection of ~100,000 anonymized orders from 2016 to 2018. It consists of 9 distinct tables capturing the full 360-degree view of the marketplace:
- Core: `Orders`, `Customers`, `Sellers`.
- Details: `Order_Items` (SKU level), `Payments`, `Reviews`.
- Context: `Products` (Attributes), `Geolocation` (Zip codes).

### **1.2 The ELT Pipeline (Extract, Load, Transform)**
A modular ELT pattern is implemented rather than traditional ETL to prioritize raw data preservation and reproducibility.

1. Extract & Load (Staging):
    - Source: Raw .csv files.
    - Destination: `db_olist_raw` (MySQL).
    - Method: 1:1 ingestion without modification.

2. Transform (Production):
    - Tool: Python (Pandas & SQLAlchemy) & SQL.
    - Destination: db_olist_analytics (MySQL).
    - Logic:
        - Cleaning: Removal of orphan records (e.g., reviews linked to non-existent orders) and type-casting.
        - Validation: Removing "ghost" orders where status = delivered but delivered_date is NULL.
        - Modeling: Structuring data into Fact and Dimension tables for the Star Schema.

### **1.3 Data Lineage Flow**

```
graph LR
    A[Raw CSVs] -->|Ingest| B(MySQL: db_olist_raw)
    B -->|Python Cleaning| C(MySQL: db_olist_analytics)
    C -->|Import| D[Power BI Dashboard]
    C -->|Query| E[Python ML Pipeline]
    E -->|Scores| F[Customer Segments]
```
## _**2. Analytic Framework**_

The analysis is guided by four strategic pillars designed to answer specific business questions for key stakeholders.

| Report / Dashboard & Audience                                         | Business Questions to Answer                                                                                                                                                      | Key Metrics & KPIs (Type)                                                                                                                                                                            | Key Dimensions (for Slicing)                                                                                      |
| :-------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| **1. Executive Sales Overview**<br>(Audience: C-Suite, Sales Heads)   | • How is the business performing overall?<br>• Are we growing month-over-month?<br>• Are we acquiring new customers?<br>• How much is each order worth?                           | • **Total GMV (Revenue)** (Lagging)<br>• **Total Orders** (Lagging)<br>• **Average Order Value (AOV)** (Lagging)<br>• **Total Unique Customers** (Lagging)<br>• **New Customer Growth %** (Leading)  | • **Time** (Year, Quarter, Month)<br>• **Geolocation** (State)                                                    |
| **2. Logistics & Operations**<br>(Audience: Ops Managers, Support)    | • Are we meeting our delivery promises?<br>• How does delivery time impact satisfaction?<br>• Where are our operational bottlenecks?<br>• What is our order cancellation rate?    | • **Avg. Delivery Time (Days)** (Leading)<br>• **Estimated vs. Actual Delivery Delta** (Leading)<br>• **Average Review Score** (Leading)<br>• **Order Status %** (% Delivered, % Canceled) (Lagging) | • **Geolocation** (Customer State, Seller State)<br>• **Time** (Month, Day of Week)<br>• **Seller** (`seller_id`) |
| **3. Product & Category**<br>(Audience: Category Managers, Marketing) | • What are our best-selling categories?<br>• What are our worst-selling categories?<br>• Are there regional product preferences?<br>• How do price and freight cost affect sales? | • **Revenue by Category** (Lagging)<br>• **Units Sold by Category** (Lagging)<br>• **Revenue per Seller** (Lagging)<br>• **Avg. Freight Value** (Lagging)<br>• **Avg. Price** (Lagging)              | • **Product Category** (English)<br>• **Geolocation** (Customer State)<br>• **Time** (Month)                      |
| **4. Customer Insights**<br>(Audience: Marketing, CRM)                | • Who are our best customers ("Champions")?<br>• Which customers are "At-Risk" of churning?<br>• How many customers are new vs. loyal?<br>• How do our customer segments behave?  | • **RFM Segments** (Calculated)<br>• **Customer Lifetime Value (CLV) Proxy** (Lagging)<br>• **New vs. Returning Customer %** (Leading)<br>• **Count of Customers by Segment**                        | • **RFM Segment**<br>• **Payment Type**<br>• **Geolocation** (Customer State)                                     |

## _**3. The Technical Engine (Power BI & ML)**_

The completed project utilizes a hybrid engine: SQL for structure, Scikit-Learn for clustering, and DAX for dynamic reporting.

### **3.1 Power BI Data Modeling (Star Schema)**

The model is optimized for high-cardinality filtering:
- **Fact Tables (Long/Narrow):** `fct_orders`, `fct_order_items`, `fct_order_reviews`,`fct_order_payment`
- **Dimension Tables (Wide):** `dim_products`, `dim_customers`, `dim_sellers`.
- **Schema Logic:** Strictly 1-to-Many relationships flowing from Dimensions to Facts to ensure accurate aggregation.

### **3.2 Key DAX Mechanisms**
- Dynamic Segmentation (Pareto): Implemented a windowing/ranking pattern to isolate the top N categories dynamically based on the selected metric (GMV or Volume).
- Context-Aware RFM Metrics:
    - Avg Days Between Orders: Calculated using a virtual table of VALUES(customer_unique_sk) to determine the precise gap for multi-purchase users only.
- Field Parameters: Used to construct the "Dynamic Matrix", allowing users to toggle between "Financial View" (Revenue, AOV) and "Operational View" (Freight, Delays) within a single visual.

### **3.3 Machine Learning (Customer Segmentation)**
- **Algorithm:** _K-Means Clustering (Scikit-Learn)_.
- **Features:** Recency (Days), Frequency (Count), Monetary (Sum).
- **Pipeline:**
    - Log Transformation to normalize skewed distributions.
    - Standard Scaling to ensure equal weighting of features.
    - Elbow Method to determine optimal K (3 Clusters).

## _**4. Business Application & Operational Workflow**_
To maintain the dashboard's relevance, the data pipeline is designed to be refreshed on a Weekly Cadence.

**Who Uses This?**
- *Analytics Engineer:* Responsible for scheduling the Python scripts (via Cron or Airflow) and monitoring database integrity.
- *Business Analyst:* Consumes the final Output in Power BI (refreshing the .pbix file after the pipeline runs).

**Execution Steps & Scripts:**

| Step                     | Script / File                  | Function                                                                 | Recommended Context                                                                                   |
|--------------------------|--------------------------------|---------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **1. Ingestion & Cleaning** | `code/Data_preparation.ipynb` | **ETL:** Extracts new raw data, validates referential integrity, and updates `db_olist_analytics`. | Run daily or weekly depending on order volume. In production, convert this notebook into a `.py` script. |
| **2. Customer Scoring**     | `code/inference_pipeline.py` | **ML Inference:** Connects to the database, loads the pre‑trained K‑Means model (`.pkl`), and assigns customer segments. | Run weekly. Customer segments (RFM) change slowly, so real‑time scoring is unnecessary.                 |
| **3. Reporting**            | Power BI Dashboard            | **Visualization:** Reads updated tables and refreshes measures.           | Manual refresh by analyst or scheduled refresh via Power BI Service.                                   |

**Customization for Business Context:**
- **Dynamic Recency:** The current `inference_pipeline.py` calculates Recency based on the dataset's static max date. For Live Business Context, the script logic is customizable to use `datetime.now()` to calculate Recency relative to the actual current date.
- **Environment Variables:** The pipeline uses a `.env` file for credentials (`DB_USER`, `DB_PASSWORD`), allowing seamless switching between Staging and Production environments without code changes.

## _**5. Assumptions, Caveats & Modifications**_

To align the dataset with the project's simulated business context, the following modifications and assumptions were applied:

### **5.1 Contextual Localization (USA)**

- **Geolocation Shift:** The original dataset is Brazilian. For the purpose of this analysis, geolocations have been mapped to United States regions to simulate a US-based marketplace context (e.g., State abbreviations mapped to US States).
- **Currency:** All monetary values are treated as US Dollars ($).

### **5.2 Data Constraints & Biases**

- **The "One-Time Buyer" Bias:** Since the dataset cuts off in late 2018, customers acquired recently appear as "One-Time Buyers" simply because they haven't had time to return. This may slightly inflate the "Low Retention" metrics.
- **Valid Order Definition:** We explicitly removed orders where `status = delivered` but `order_delivered_customer_date` was NULL (identified as system errors during EDA).
- **Freight Aggregation:** Freight is recorded at the item level. For multi-item orders, we assume total freight is the simple sum of item freights.

## **_6. Future Improvements & Self-Reflections_**

### **6.1 Data Model Limitations**

**The "Seller-Product" Disconnect:** Currently, dim_sellers and dim_products interact only via the high-volume fct_order_items table. This makes analyzing "Seller Portfolios" (which products a specific seller lists) computationally expensive. A bridge table or aggregated materialized view would optimize this.

### **6.2 Advanced Analytics**

**Predictive Churn:** The current model describes past behavior (Descriptive). The next iteration would involve training a Logistic Regression model to predict the probability of churn for active users in real-time.

## **_7. Repository Structure_**

```
├── code/
│   ├── Data_preparation.ipynb    # Cleaning & ELT Logic
│   ├── EDA.ipynb                 # Exploratory Analysis
│   ├── Customer_Segmentation.ipynb # K-Means Modeling
│   ├── inference_pipeline.py     # Production script for scoring
│   ├── view_rmf_base_script.sql  # SQL View definition
│   └── APPENDIX.md               # You are here (Technical Manual)
├── images/                       # Screenshots for README
├── README.md    
```