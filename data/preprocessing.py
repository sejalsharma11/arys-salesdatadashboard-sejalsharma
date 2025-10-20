"""
Sales Data Preprocessing Script
This script downloads, cleans, and preprocesses the sales data for the dashboard.
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime
import requests
from io import StringIO

def download_data():
    """Load the sales data from the Kaggle dataset"""
    print("Loading Kaggle sales data...")
    
    # Load the real Kaggle dataset
    csv_path = 'data/raw/sales_data_sample.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Dataset not found at {csv_path}")
        print("Please ensure the Kaggle dataset is placed in data/raw/sales_data_sample.csv")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path, encoding='latin-1')  # Use latin-1 encoding for special characters
        print(f"✅ Successfully loaded {len(df)} records from Kaggle dataset")
        
        # Convert ORDERDATE to datetime
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
        
        # Extract date components if not present
        if 'YEAR_ID' not in df.columns:
            df['YEAR_ID'] = df['ORDERDATE'].dt.year
        if 'MONTH_ID' not in df.columns:
            df['MONTH_ID'] = df['ORDERDATE'].dt.month
        if 'QTR_ID' not in df.columns:
            df['QTR_ID'] = df['ORDERDATE'].dt.quarter
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None

def preprocess_data(df):
    """Clean and preprocess the sales data"""
    print("Preprocessing data...")
    
    if df is None:
        return None
    
    # Keep only required columns (use available columns from Kaggle dataset)
    required_columns = [
        'ORDERNUMBER', 'QUANTITYORDERED', 'PRICEEACH', 'ORDERLINENUMBER',
        'SALES', 'ORDERDATE', 'STATUS', 'QTR_ID', 'MONTH_ID', 'YEAR_ID',
        'COUNTRY', 'PRODUCTLINE', 'CUSTOMERNAME'  # Added for better analysis
    ]
    
    # Check which columns are available
    available_columns = [col for col in required_columns if col in df.columns]
    df = df[available_columns].copy()
    
    # Handle missing values
    df = df.dropna()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Normalize categories
    df['STATUS'] = df['STATUS'].str.title()
    df['COUNTRY'] = df['COUNTRY'].str.title()
    df['PRODUCTLINE'] = df['PRODUCTLINE'].str.title()
    if 'CUSTOMERNAME' in df.columns:
        df['CUSTOMERNAME'] = df['CUSTOMERNAME'].str.title()
    
    # Ensure data types
    df['ORDERNUMBER'] = df['ORDERNUMBER'].astype(str)
    df['QUANTITYORDERED'] = df['QUANTITYORDERED'].astype(int)
    df['PRICEEACH'] = df['PRICEEACH'].astype(float)
    df['SALES'] = df['SALES'].astype(float)
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    
    # Add additional calculated fields
    df['REVENUE_PER_UNIT'] = df['SALES'] / df['QUANTITYORDERED']
    df['ORDER_SIZE'] = df.groupby('ORDERNUMBER')['QUANTITYORDERED'].transform('sum')
    
    print(f"Data preprocessing complete. Final dataset shape: {df.shape}")
    return df

def save_to_database(df, db_path='data/sales_data.db'):
    """Save processed data to SQLite database"""
    print("Saving data to database...")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    
    # Save to database
    df.to_sql('sales_data', conn, if_exists='replace', index=False)
    
    # Create indexes for better query performance
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orderdate ON sales_data(ORDERDATE)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_country ON sales_data(COUNTRY)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_productline ON sales_data(PRODUCTLINE)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON sales_data(STATUS)')
    
    conn.close()
    
    print(f"Data saved to database: {db_path}")

def generate_summary_stats(df):
    """Generate summary statistics"""
    print("Generating summary statistics...")
    
    # Filter out cancelled orders for business metrics (same as dashboard)
    active_df = df[df['STATUS'] != 'Cancelled'].copy()
    
    summary = {
        'total_records': len(df),
        'active_records': len(active_df),
        'cancelled_records': len(df) - len(active_df),
        'total_sales': active_df['SALES'].sum(),  # Exclude cancelled orders
        'avg_order_value': active_df['SALES'].sum() / active_df['ORDERNUMBER'].nunique(),  # Sales per unique order
        'avg_sales_per_record': active_df['SALES'].mean(),  # Sales per record
        'unique_orders': active_df['ORDERNUMBER'].nunique(),
        'unique_countries': df['COUNTRY'].nunique(),
        'date_range': f"{df['ORDERDATE'].min()} to {df['ORDERDATE'].max()}",
        'top_country': active_df.groupby('COUNTRY')['SALES'].sum().idxmax(),
        'top_product_line': active_df.groupby('PRODUCTLINE')['SALES'].sum().idxmax()
    }
    
    # Save summary to file
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/summary_stats.txt', 'w') as f:
        for key, value in summary.items():
            f.write(f"{key}: {value}\n")
    
    print("Summary statistics saved to data/processed/summary_stats.txt")
    return summary

def main():
    """Main preprocessing pipeline"""
    print("Starting data preprocessing pipeline...")
    
    # Create directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Download and load data
    df = download_data()
    
    if df is None:
        print("❌ Failed to load data. Exiting...")
        return
    
    # Delete old raw data file if it exists
    old_raw_file = 'data/raw/sales_data_raw.csv'
    if os.path.exists(old_raw_file):
        os.remove(old_raw_file)
        print(f"✅ Removed old file: {old_raw_file}")
    
    # Preprocess data
    df_processed = preprocess_data(df)
    
    if df_processed is None:
        print("❌ Failed to preprocess data. Exiting...")
        return
    
    # Save processed data
    df_processed.to_csv('data/processed/sales_data_processed.csv', index=False)
    print("Processed data saved to data/processed/sales_data_processed.csv")
    
    # Save to database
    save_to_database(df_processed)
    
    # Generate summary statistics
    summary = generate_summary_stats(df_processed)
    
    print("\nPreprocessing complete!")
    print(f"Total records processed: {summary['total_records']}")
    print(f"Active records (non-cancelled): {summary['active_records']}")
    print(f"Cancelled records: {summary['cancelled_records']}")
    print(f"Total sales value (active): ${summary['total_sales']:,.2f}")
    print(f"Average order value: ${summary['avg_order_value']:.2f}")
    print(f"Average sales per record: ${summary['avg_sales_per_record']:.2f}")

if __name__ == "__main__":
    main()
