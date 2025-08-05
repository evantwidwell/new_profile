# Evan Twidwell - Portfolio & Profile Site

**Live Site:** [evantwidwell.info](http://evantwidwell.info)

## Overview

This is a full-stack web application serving as my professional portfolio and profile site. The project demonstrates expertise in data engineering, web development, and modern software architecture through a real-world implementation using NYC taxi data.

## 🚀 Key Features

### 1. **Content Management System**
- Custom Django-based CMS with markdown support
- Admin interface for content creation and management
- Python-frontmatter integration for structured content
- Dynamic post rendering with SEO optimization

### 2. **Data Engineering Pipeline**
- **Data Source**: NYC Taxi & Limousine Commission public datasets (millions of records)
- **Database Engine**: DuckDB for high-performance analytics
- **Data Format**: Optimized Parquet files for fast querying
- **Caching Strategy**: LRU cache implementation for API response optimization
- **API Design**: RESTful endpoints using Django REST Framework

### 3. **Interactive Data Visualization**
- **Frontend Framework**: React 19 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Mapping**: Interactive Leaflet maps showing taxi zone data
- **Charts**: Recharts for statistical visualizations
- **UI Framework**: Tailwind CSS for responsive design
- **Features**: Date range filtering, real-time statistics, geographic data visualization

### 4. **Professional Resume & About Page**
- Comprehensive resume with work experience and skills
- Professional presentation of background and expertise

## 🛠 Technical Stack

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Database**: DuckDB (analytical), PostgreSQL (application data)
- **Data Processing**: Pandas, PyArrow
- **Deployment**: Gunicorn, WhiteNoise for static files
- **CORS**: Django-CORS-Headers for cross-origin requests

### Frontend
- **Framework**: React 19 with TypeScript
- **Build System**: Vite
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS v4
- **Maps**: Leaflet with React-Leaflet
- **Charts**: Recharts
- **Date Handling**: date-fns

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Process Management**: Makefile for development workflow
- **Code Quality**: ESLint, TypeScript strict mode

## 📊 Data Engineering Highlights

- **Scale**: Processing millions of NYC taxi trip records
- **Performance**: Sub-second query responses through DuckDB optimization
- **Architecture**: Separation of analytical (DuckDB) and transactional (PostgreSQL) workloads
- **Efficiency**: Parquet columnar storage for 10x faster analytics vs traditional formats
- **Caching**: Intelligent cache warming and LRU eviction strategies

## 🏗 Architecture

```
Frontend (React/TypeScript)
    ↓ HTTP/REST
Django REST API
    ↓ SQL
DuckDB + PostgreSQL
    ↓
Parquet Files
```

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/evantwidwell/new_profile.git
cd new_profile

# Or use the Makefile
make up
```
