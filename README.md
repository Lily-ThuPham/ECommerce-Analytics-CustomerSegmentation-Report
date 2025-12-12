# **Olist E-Commerce: Full-Stack Analytics & Customer Segmentation**
**Author**: Thu Pham | **Date**: 10/2025

## *Table of Contents*
1. [Project Background](#1-project-background)  
2. [Data Structure & Initial Checks](#2-data-structure--initial-checks)  
3. [Executive Summary](#3-executive-summary)  
4. [Insights Deep Dive](#4-insights-deep-dive)  
5. [Sales Forecasting Model](#5-sales-forecasting-model)  
6. [Recommendations](#6-recommendations)  

## _**1. Project Background**_
**Olist** is a E-commerce marketplace that connects small businesses (sellers) to customers across the country. As an internal Data Analyst, I have been tasked with analyzing the company's performance from 2016 to 2018 to identify growth opportunities and operational bottlenecks.

The business has seen rapid volume growth since the first operation in 2016, However, this scale has introduced challenges: _weak customers retention and negative reviews_. This project aims to deliver a comprehensive assessment of the company’s operations,  turning raw data into practical strategic insights that strengthen the fulfillment funnel and unlock long‑term customer value.

**_Insights and recommendations are provided on the following key areas:_**
- **Executive Sales Overview:** Assess the overall health of the business by tracking GMV, order volume trends, and _**Average Order Value (AOV)**_ to distinguish between growth driven by acquisition versus customer value.
- **Logistics & Operations:** Identify bottlenecks in the fulfillment funnel and evaluate customers satisfaction.
- **Product & Category:** Identify top-performing categories (Pareto analysis) and high-risk to optimize inventory management.
- **Customer Insights:** Segment the customer base using RFM analysis and K-Means clustering to distinguish "Champions" from "Lost" customers and develop targeted strategies.

_**Technical Stack:**_
- SQL (MySQL): Data warehousing, ETL, and logic views.
- Python (Pandas/Scikit-Learn): Data cleaning, feature engineering, and K-Means clustering.
- Power BI: Visualizing and Storytelling with interactive dashboards.

The Python scripts used for the ELT pipeline and Inference Engine can be found here [link to scripts folder].

The Python and SQL scripts to data preparation and EDA can be found [here](code\Data_preparation.ipynb) and [here](code\EDA.ipynb).

The SQL views used for dynamic scoring can be found [here](code\view_rmf_base_script.sql).

An interactive Power BI dashboard used to explore these insights can be found [here](https://app.powerbi.com/view?r=eyJrIjoiYzRlM2QzYmQtY2I1Yi00NDg0LWI0MzItMjFhZjM0YThjMGE2IiwidCI6IjE2NzIwYmVkLTY1ZWItNGFhMi04ZjMwLWQxY2UxNzBjZjAwMCIsImMiOjEwfQ%3D%3D&pageName=000e5656b61190d4c961).






