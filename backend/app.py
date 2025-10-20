"""
Flask Backend API for Sales Data Dashboard
Provides RESTful endpoints for sales data analysis
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sales_data.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    """Execute query and return results as list of dictionaries"""
    conn = get_db_connection()
    if params:
        cursor = conn.execute(query, params)
    else:
        cursor = conn.execute(query)
    
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return results

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "message": "Sales Data Dashboard API",
        "version": "1.0",
        "endpoints": [
            "/api/sales-over-time",
            "/api/sales-by-category",
            "/api/sales-by-country",
            "/api/kpis",
            "/api/top-customers",
            "/api/monthly-trends",
            "/api/quarterly-analysis"
        ]
    })

@app.route('/api/sales-over-time')
def sales_over_time():
    """Get sales data over time"""
    try:
        period = request.args.get('period', 'monthly')  # daily, monthly, quarterly, yearly
        
        if period == 'daily':
            query = """
                SELECT DATE(ORDERDATE) as date, SUM(SALES) as total_sales, COUNT(*) as order_count
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY DATE(ORDERDATE)
                ORDER BY date
            """
        elif period == 'monthly':
            query = """
                SELECT YEAR_ID, MONTH_ID, SUM(SALES) as total_sales, COUNT(*) as order_count
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY YEAR_ID, MONTH_ID
                ORDER BY YEAR_ID, MONTH_ID
            """
        elif period == 'quarterly':
            query = """
                SELECT YEAR_ID, QTR_ID, SUM(SALES) as total_sales, COUNT(*) as order_count
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY YEAR_ID, QTR_ID
                ORDER BY YEAR_ID, QTR_ID
            """
        else:  # yearly
            query = """
                SELECT YEAR_ID, SUM(SALES) as total_sales, COUNT(*) as order_count
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY YEAR_ID
                ORDER BY YEAR_ID
            """
        
        results = execute_query(query)
        return jsonify({"data": results, "period": period})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales-by-category')
def sales_by_category():
    """Get sales data by product category"""
    try:
        query = """
            SELECT PRODUCTLINE as category, 
                   SUM(SALES) as total_sales,
                   COUNT(*) as order_count,
                   AVG(SALES) as avg_order_value,
                   SUM(QUANTITYORDERED) as total_quantity
            FROM sales_data 
            WHERE STATUS != 'Cancelled'
            GROUP BY PRODUCTLINE
            ORDER BY total_sales DESC
        """
        
        results = execute_query(query)
        return jsonify({"data": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sales-by-country')
def sales_by_country():
    """Get sales data by country"""
    try:
        query = """
            SELECT COUNTRY, 
                   SUM(SALES) as total_sales,
                   COUNT(*) as order_count,
                   AVG(SALES) as avg_order_value,
                   COUNT(DISTINCT ORDERNUMBER) as unique_orders
            FROM sales_data 
            WHERE STATUS != 'Cancelled'
            GROUP BY COUNTRY
            ORDER BY total_sales DESC
        """
        
        results = execute_query(query)
        return jsonify({"data": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/kpis')
def get_kpis():
    """Get key performance indicators"""
    try:
        # Total sales
        total_sales_query = "SELECT SUM(SALES) as total_sales FROM sales_data WHERE STATUS != 'Cancelled'"
        total_sales = execute_query(total_sales_query)[0]['total_sales']
        
        # Total orders
        total_orders_query = "SELECT COUNT(DISTINCT ORDERNUMBER) as total_orders FROM sales_data WHERE STATUS != 'Cancelled'"
        total_orders = execute_query(total_orders_query)[0]['total_orders']
        
        # Average order value
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # Total customers (using country as proxy)
        total_customers_query = "SELECT COUNT(DISTINCT COUNTRY) as total_customers FROM sales_data"
        total_customers = execute_query(total_customers_query)[0]['total_customers']
        
        # Monthly growth rate
        monthly_growth_query = """
            WITH monthly_sales AS (
                SELECT YEAR_ID, MONTH_ID, SUM(SALES) as monthly_total
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY YEAR_ID, MONTH_ID
                ORDER BY YEAR_ID, MONTH_ID
            )
            SELECT 
                (MAX(monthly_total) - MIN(monthly_total)) / MIN(monthly_total) * 100 as growth_rate
            FROM monthly_sales
        """
        growth_rate = execute_query(monthly_growth_query)[0]['growth_rate'] or 0
        
        # Order status distribution
        status_query = """
            SELECT STATUS, COUNT(*) as count, 
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales_data), 2) as percentage
            FROM sales_data 
            GROUP BY STATUS
        """
        status_distribution = execute_query(status_query)
        
        kpis = {
            "total_sales": round(total_sales, 2),
            "total_orders": total_orders,
            "avg_order_value": round(avg_order_value, 2),
            "total_customers": total_customers,
            "growth_rate": round(growth_rate, 2),
            "status_distribution": status_distribution
        }
        
        return jsonify({"data": kpis})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-customers')
def top_customers():
    """Get top customers by sales"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Use CUSTOMERNAME if available, otherwise fall back to COUNTRY
        query = """
            SELECT 
                CASE 
                    WHEN EXISTS(SELECT 1 FROM pragma_table_info('sales_data') WHERE name='CUSTOMERNAME') 
                    THEN CUSTOMERNAME 
                    ELSE COUNTRY 
                END as customer,
                SUM(SALES) as total_sales,
                COUNT(DISTINCT ORDERNUMBER) as total_orders,
                AVG(SALES) as avg_order_value,
                MAX(ORDERDATE) as last_order_date
            FROM sales_data 
            WHERE STATUS != 'Cancelled'
            GROUP BY customer
            ORDER BY total_sales DESC
            LIMIT ?
        """
        
        # First check if CUSTOMERNAME column exists
        conn = get_db_connection()
        cursor = conn.execute("PRAGMA table_info(sales_data)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        if 'CUSTOMERNAME' in columns:
            query = """
                SELECT CUSTOMERNAME as customer, 
                       SUM(SALES) as total_sales,
                       COUNT(DISTINCT ORDERNUMBER) as total_orders,
                       AVG(SALES) as avg_order_value,
                       MAX(ORDERDATE) as last_order_date
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY CUSTOMERNAME
                ORDER BY total_sales DESC
                LIMIT ?
            """
        else:
            query = """
                SELECT COUNTRY as customer, 
                       SUM(SALES) as total_sales,
                       COUNT(DISTINCT ORDERNUMBER) as total_orders,
                       AVG(SALES) as avg_order_value,
                       MAX(ORDERDATE) as last_order_date
                FROM sales_data 
                WHERE STATUS != 'Cancelled'
                GROUP BY COUNTRY
                ORDER BY total_sales DESC
                LIMIT ?
            """
        
        results = execute_query(query, (limit,))
        return jsonify({"data": results, "limit_requested": limit, "results_count": len(results)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monthly-trends')
def monthly_trends():
    """Get monthly sales trends"""
    try:
        query = """
            SELECT 
                YEAR_ID,
                MONTH_ID,
                SUM(SALES) as total_sales,
                COUNT(DISTINCT ORDERNUMBER) as order_count,
                AVG(SALES) as avg_order_value,
                SUM(QUANTITYORDERED) as total_quantity
            FROM sales_data 
            WHERE STATUS != 'Cancelled'
            GROUP BY YEAR_ID, MONTH_ID
            ORDER BY YEAR_ID, MONTH_ID
        """
        
        results = execute_query(query)
        return jsonify({"data": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quarterly-analysis')
def quarterly_analysis():
    """Get quarterly analysis"""
    try:
        query = """
            SELECT 
                YEAR_ID,
                QTR_ID,
                SUM(SALES) as total_sales,
                COUNT(DISTINCT ORDERNUMBER) as order_count,
                AVG(SALES) as avg_order_value,
                COUNT(DISTINCT COUNTRY) as countries_served
            FROM sales_data 
            WHERE STATUS != 'Cancelled'
            GROUP BY YEAR_ID, QTR_ID
            ORDER BY YEAR_ID, QTR_ID
        """
        
        results = execute_query(query)
        return jsonify({"data": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/product-performance')
def product_performance():
    """Get product performance metrics"""
    try:
        query = """
            SELECT 
                PRODUCTLINE,
                SUM(SALES) as total_sales,
                SUM(QUANTITYORDERED) as total_quantity,
                AVG(PRICEEACH) as avg_price,
                COUNT(DISTINCT ORDERNUMBER) as order_count,
                COUNT(DISTINCT COUNTRY) as countries
            FROM sales_data 
            WHERE STATUS != 'Cancelled'
            GROUP BY PRODUCTLINE
            ORDER BY total_sales DESC
        """
        
        results = execute_query(query)
        return jsonify({"data": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        print("Please run the data preprocessing script first: python data/preprocessing.py")
    else:
        print("Starting Flask API server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
