"""
Streamlit Dashboard for Sales Data Analysis
Interactive dashboard with multiple visualizations and KPIs
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Sales Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:5000/api"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data from {endpoint}: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Please ensure the Flask backend is running on port 5000.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def create_kpi_cards(kpis):
    """Create KPI cards display"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Sales",
            value=f"${kpis['total_sales']:,.2f}",
            delta=f"{kpis['growth_rate']:.1f}% growth"
        )
    
    with col2:
        st.metric(
            label="📦 Total Orders",
            value=f"{kpis['total_orders']:,}",
            delta="Active orders"
        )
    
    with col3:
        st.metric(
            label="💵 Avg Order Value",
            value=f"${kpis['avg_order_value']:.2f}",
            delta="Per order"
        )
    
    with col4:
        st.metric(
            label="🌍 Countries Served",
            value=f"{kpis['total_customers']}",
            delta="Global reach"
        )

def create_sales_over_time_chart(data, period):
    """Create sales over time chart"""
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
    
    try:
        if period == 'monthly':
            # Ensure we have the required columns
            if 'YEAR_ID' in df.columns and 'MONTH_ID' in df.columns:
                # Create a proper date string first, then convert
                df['date_str'] = df['YEAR_ID'].astype(str) + '-' + df['MONTH_ID'].astype(str).str.zfill(2) + '-01'
                df['date'] = pd.to_datetime(df['date_str'], format='%Y-%m-%d', errors='coerce')
                # Remove any rows with invalid dates
                df = df.dropna(subset=['date'])
                if not df.empty:
                    x_col = 'date'
                    title = "Monthly Sales Trend"
                else:
                    # Fallback to year-month string if date conversion fails
                    df = pd.DataFrame(data)  # Reset df
                    df['period'] = df['YEAR_ID'].astype(str) + '-' + df['MONTH_ID'].astype(str).str.zfill(2)
                    x_col = 'period'
                    title = "Monthly Sales Trend"
            else:
                # Fallback to yearly if monthly data not available
                x_col = 'YEAR_ID'
                title = "Yearly Sales Trend"
        elif period == 'quarterly':
            if 'YEAR_ID' in df.columns and 'QTR_ID' in df.columns:
                df['period'] = df['YEAR_ID'].astype(str) + '-Q' + df['QTR_ID'].astype(str)
                x_col = 'period'
                title = "Quarterly Sales Trend"
            else:
                x_col = 'YEAR_ID'
                title = "Yearly Sales Trend"
        else:
            x_col = 'YEAR_ID'
            title = "Yearly Sales Trend"
    except Exception as e:
        st.error(f"Error creating time chart: {e}")
        return go.Figure().add_annotation(text="Error creating chart", xref="paper", yref="paper", x=0.5, y=0.5)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Sales line
    fig.add_trace(
        go.Scatter(
            x=df[x_col], 
            y=df['total_sales'],
            mode='lines+markers',
            name='Total Sales',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ),
        secondary_y=False,
    )
    
    # Order count bars
    fig.add_trace(
        go.Bar(
            x=df[x_col], 
            y=df['order_count'],
            name='Order Count',
            opacity=0.6,
            marker_color='#ff7f0e'
        ),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="Time Period")
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig.update_yaxes(title_text="Order Count", secondary_y=True)
    
    fig.update_layout(
        title=title,
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_category_chart(data):
    """Create sales by category chart"""
    df = pd.DataFrame(data)
    
    # Pie chart for sales distribution
    fig_pie = px.pie(
        df, 
        values='total_sales', 
        names='category',
        title='Sales Distribution by Product Category',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # Bar chart for detailed metrics
    fig_bar = px.bar(
        df, 
        x='category', 
        y='total_sales',
        color='avg_order_value',
        title='Sales and Average Order Value by Category',
        color_continuous_scale='viridis'
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    
    return fig_pie, fig_bar

def create_country_chart(data):
    """Create sales by country chart"""
    df = pd.DataFrame(data)
    
    # Horizontal bar chart
    fig = px.bar(
        df.head(10), 
        x='total_sales', 
        y='COUNTRY',
        orientation='h',
        title='Top 10 Countries by Sales',
        color='total_sales',
        color_continuous_scale='blues'
    )
    fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
    
    return fig

def create_monthly_trends_chart(data):
    """Create monthly trends heatmap"""
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No monthly data available", xref="paper", yref="paper", x=0.5, y=0.5)
    
    try:
        # Check if required columns exist
        if 'MONTH_ID' not in df.columns or 'YEAR_ID' not in df.columns or 'total_sales' not in df.columns:
            return go.Figure().add_annotation(text="Missing required data columns", xref="paper", yref="paper", x=0.5, y=0.5)
        
        # Create pivot table for heatmap
        pivot_df = df.pivot(index='MONTH_ID', columns='YEAR_ID', values='total_sales')
        
        if pivot_df.empty:
            return go.Figure().add_annotation(text="No data to display", xref="paper", yref="paper", x=0.5, y=0.5)
        
        # Fill NaN values with 0 for better visualization
        pivot_df = pivot_df.fillna(0)
        
        # Ensure we have all 12 months (reindex to show all months)
        all_months = list(range(1, 13))
        pivot_df = pivot_df.reindex(all_months, fill_value=0)
        
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Year", y="Month", color="Sales"),
            title="Sales Heatmap by Month and Year (0 = No Sales)",
            color_continuous_scale='RdYlBu_r'
        )
        
        # Update y-axis to show month names
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        fig.update_yaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=month_names
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating monthly trends chart: {e}")
        return go.Figure().add_annotation(text="Error creating heatmap", xref="paper", yref="paper", x=0.5, y=0.5)

def main():
    """Main dashboard function"""
    # Header
    st.markdown('<h1 class="main-header">📊 Sales Data Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Time period selector
    time_period = st.sidebar.selectbox(
        "Select Time Period",
        ["monthly", "quarterly", "yearly"],
        index=0
    )
    
    # Top customers limit
    top_customers_limit = st.sidebar.slider(
        "Top Customers to Show",
        min_value=5,
        max_value=20,
        value=10
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 This dashboard updates every 5 minutes automatically.")
    
    # Fetch data
    with st.spinner("Loading dashboard data..."):
        kpis_data = fetch_data("kpis")
        sales_time_data = fetch_data(f"sales-over-time?period={time_period}")
        category_data = fetch_data("sales-by-category")
        country_data = fetch_data("sales-by-country")
        customers_data = fetch_data(f"top-customers?limit={top_customers_limit}")
        monthly_trends_data = fetch_data("monthly-trends")
    
    # Check if data is available
    if not all([kpis_data, sales_time_data, category_data, country_data]):
        st.error("Unable to load data. Please check if the Flask API is running.")
        st.stop()
    
    # KPI Cards
    st.markdown("## 📈 Key Performance Indicators")
    create_kpi_cards(kpis_data['data'])
    
    st.markdown("---")
    
    # Sales over time
    st.markdown("## 📅 Sales Trends Over Time")
    if sales_time_data and sales_time_data['data']:
        fig_time = create_sales_over_time_chart(sales_time_data['data'], time_period)
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.warning("No sales trend data available.")
    
    # Two column layout for category and country analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🏷️ Sales by Category")
        if category_data and category_data['data']:
            fig_pie, fig_bar = create_category_chart(category_data['data'])
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("No category data available.")
    
    with col2:
        st.markdown("## 🌍 Sales by Country")
        if country_data and country_data['data']:
            fig_country = create_country_chart(country_data['data'])
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.warning("No country data available.")
    
    # Category details bar chart
    if category_data and category_data['data']:
        st.markdown("## 📊 Detailed Category Analysis")
        _, fig_bar = create_category_chart(category_data['data'])
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Monthly trends heatmap
    if monthly_trends_data and monthly_trends_data['data']:
        st.markdown("## 🔥 Monthly Sales Heatmap")
        fig_heatmap = create_monthly_trends_chart(monthly_trends_data['data'])
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Top customers table
    st.markdown(f"## 🏆 Top {top_customers_limit} Customers")
    if customers_data and customers_data['data']:
        df_customers = pd.DataFrame(customers_data['data'])
        df_customers['total_sales'] = df_customers['total_sales'].apply(lambda x: f"${x:,.2f}")
        df_customers['avg_order_value'] = df_customers['avg_order_value'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(
            df_customers,
            column_config={
                "customer": "Customer",
                "total_sales": "Total Sales",
                "total_orders": "Total Orders",
                "avg_order_value": "Avg Order Value",
                "last_order_date": "Last Order"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("No customer data available.")
    
    # Order status distribution
    if kpis_data and 'status_distribution' in kpis_data['data']:
        st.markdown("## 📋 Order Status Distribution")
        status_df = pd.DataFrame(kpis_data['data']['status_distribution'])
        
        fig_status = px.bar(
            status_df,
            x='STATUS',
            y='count',
            color='percentage',
            title='Order Count by Status',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Sales Data Dashboard | Built with Streamlit & Flask | ArysGarage Assignment</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
