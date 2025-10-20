# 📊 Sales Data Dashboard - ArysGarage Assignment

## 🎯 Project Overview
This project creates a comprehensive, enterprise-level sales data dashboard using modern Python technologies. The system processes real-world sales data from Kaggle, stores it in a relational database, and provides interactive visualizations through a professional web interface. The architecture follows industry best practices with a clear separation between data processing, API services, and user interface components.

**Key Highlights:**
- 📈 Real-time sales analytics and KPI tracking
- 🌐 RESTful API architecture for scalable data access
- 📱 Interactive web dashboard with responsive design
- 🗄️ Robust data processing pipeline with quality assurance
- 📊 Advanced visualizations including heatmaps, trends, and geographic analysis

## 🏗️ System Architecture

### Backend Services
- **Flask REST API**: High-performance web service with CORS support
- **SQLite Database**: Optimized relational database with proper indexing
- **Data Processing Engine**: Pandas-based ETL pipeline with error handling

### Frontend Interface
- **Streamlit Dashboard**: Modern, responsive web interface
- **Interactive Charts**: Plotly-powered visualizations with real-time updates
- **User Controls**: Dynamic filtering and customization options

### Data Pipeline
- **Raw Data Ingestion**: Kaggle sales dataset processing
- **Data Validation**: Quality checks and business logic enforcement
- **Performance Optimization**: Efficient querying and caching strategies

## ✨ Key Features

### 📊 Analytics & Reporting
- **Key Performance Indicators (KPIs)**
  - Total sales revenue (excluding cancelled orders)
  - Average order value calculations
  - Customer acquisition metrics
  - Growth rate analysis
  
- **Time-Based Analysis**
  - Monthly sales trends with interactive charts
  - Quarterly performance comparisons
  - Yearly growth patterns
  - Seasonal trend identification

- **Geographic Intelligence**
  - Sales performance by country/region
  - Market penetration analysis
  - Geographic distribution visualization

- **Product Analytics**
  - Sales by product line with detailed breakdowns
  - Product performance rankings
  - Category-wise revenue analysis

### 🔧 Technical Features
- **Real-time Data Refresh**: Automatic dashboard updates every 5 minutes
- **Dynamic Filtering**: Customizable time periods and data segments
- **Responsive Design**: Mobile-friendly interface with adaptive layouts
- **Error Handling**: Comprehensive error management and user feedback
- **Data Consistency**: Business logic enforcement across all components

## 📁 Detailed Project Structure
```
ArysGarage/
├── backend/                    # API Services Layer
│   ├── app.py                  # Flask REST API with 8 endpoints
│   └── requirements.txt        # Backend dependencies (Flask, CORS, etc.)
│
├── frontend/                   # User Interface Layer
│   ├── dashboard.py           # Streamlit dashboard (500+ lines)
│   ├── requirements.txt       # Frontend dependencies (Streamlit, Plotly)
│   └── config.py              # Dashboard configuration settings
│
├── data/                       # Data Management Layer
│   ├── raw/                   # Original Kaggle dataset
│   │   └── sales_data_sample.csv  # Source data (2,823 records)
│   ├── processed/             # Cleaned and processed data
│   │   ├── sales_data_processed.csv
│   │   └── summary_stats.txt  # Data quality metrics
│   ├── preprocessing.py       # ETL pipeline with data validation
│   └── sales_data.db         # SQLite database with indexes
│
├── notebooks/                  # Data Analysis & Exploration
│   └── data_exploration.ipynb # Jupyter analysis
│
├── docs/                       # Documentation & Reports
│   └──  Report.pdf     # Complete Project documentation
│
└── README.md                  # This comprehensive guide
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ installed
- Git for version control
- 4GB+ RAM recommended for data processing

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd ArysGarage
   ```

2. **Install Dependencies**
   ```bash
   # Backend dependencies
   pip install -r backend/requirements.txt
   
   # Frontend dependencies  
   pip install -r frontend/requirements.txt
   ```

3. **Initialize the Data Pipeline**
   ```bash
   # Process raw data and create database
   python data/preprocessing.py
   ```

4. **Launch the Application**
   ```bash
   # Terminal 1: Start Flask API (Port 5000)
   python backend/app.py
   
   # Terminal 2: Start Streamlit Dashboard (Port 8501)
   streamlit run frontend/dashboard.py
   ```

5. **Access the Dashboard**
   - Open your browser to: `http://localhost:8501`

## 📊 Data Overview

### Dataset Information
- **Source**: Kaggle Sales Dataset (Real-world e-commerce data)
- **Records**: 2,823 total transactions
- **Active Records**: 2,763 (excluding 60 cancelled orders)
- **Time Period**: January 2003 - May 2005
- **Geographic Coverage**: 19 countries worldwide
- **Product Categories**: 7 distinct product lines

### Business Metrics
- **Total Revenue**: $9,838,141.37 (active orders only)
- **Average Order Value**: $32,469.11
- **Total Orders**: 303 unique orders
- **Customer Base**: 92 unique customers across 19 countries

### Data Quality Assurance
- ✅ No missing values in critical fields
- ✅ Date range validation and consistency checks
- ✅ Business logic enforcement (cancelled orders excluded)
- ✅ Cross-component data consistency verification
- ✅ Automated testing and validation scripts

## 🔌 API Endpoints

The Flask backend provides 8 RESTful endpoints:

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/kpis` | GET | Key performance indicators | None |
| `/api/sales-over-time` | GET | Time-based sales data | `period` (monthly/quarterly/yearly) |
| `/api/sales-by-category` | GET | Product line performance | None |
| `/api/sales-by-country` | GET | Geographic sales distribution | None |
| `/api/top-customers` | GET | Customer rankings | `limit` (number of customers) |
| `/api/monthly-trends` | GET | Monthly sales patterns | None |
| `/api/data-refresh` | POST | Trigger data refresh | None |

## 🎨 Dashboard Features

### Interactive Visualizations
- **📈 KPI Cards**: Real-time metrics with trend indicators
- **📅 Time Series Charts**: Monthly/quarterly sales trends
- **🗺️ Geographic Analysis**: Sales by country with interactive maps
- **📊 Product Performance**: Category-wise sales breakdowns
- **🔥 Customer Rankings**: Top customers with dynamic limits
- **🌡️ Sales Heatmap**: Monthly performance visualization

### User Controls
- **🔄 Data Refresh**: Manual refresh button with cache clearing
- **⚙️ Time Period Selection**: Monthly, quarterly, yearly views
- **🎯 Customer Limits**: Adjustable top customer display (5-20)
- **📱 Responsive Layout**: Mobile-friendly design

## 🤖 AI Usage Disclosure

This project was developed with **limited and specific** AI assistance by **Claude Sonnet 4** in the following areas:

### ✅ AI-Assisted Components
- **Frontend Styling Issues**: Help with Streamlit layout and CSS customization
- **Streamlit Basic Code**: Getting to know Streamlit basic code and components
- **Flask CORS Configuration**: Assistance with cross-origin resource sharing setup
- **Basic Flask Routing**: Initial guidance on REST API endpoint structure
- **SQLite Query Optimization**: Minor help with database query performance

## 🚀 Future Enhancements

### Planned Features
- **User Authentication**: Role-based access control
- **Advanced Analytics**: Predictive modeling and forecasting
- **Export Functionality**: PDF/Excel report generation
- **Real-time Data**: Live data streaming capabilities
- **Mobile App**: Native mobile application development

### Technical Improvements
- **Database Migration**: PostgreSQL for production deployment
- **Containerization**: Docker deployment configuration
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Application performance monitoring

## 👨‍💻 Author & Contact

**Developer**: Sejal Sharma
**Email**: sejalsharmawork11@gmail.com  
**GitHub**: https://github.com/sejalsharma11
**LinkedIn**: https://www.linkedin.com/in/sejalsharma11/
**Technology Stack**: Python, Flask, Streamlit, SQLite, Pandas, Plotly  

---

*This project demonstrates proficiency in full-stack development, data engineering, and modern web technologies with minimal AI assistance, showcasing strong independent development capabilities.*
