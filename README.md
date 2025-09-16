# ARGO Oceanographic Data Analysis Platform

An AI-powered oceanographic data analysis platform for ARGO float data with ultra-fast Groq LLM integration and interactive visualizations.

## Features

- **NetCDF Data Ingestion**: Process ARGO float NetCDF files and convert to structured formats.
- **Dual Database System**: PostgreSQL for relational data, FAISS for vector embeddings.
- **AI-Powered Queries**: Natural language processing using Groq API with RAG pipeline.
- **Interactive Visualizations**: Geospatial maps, depth-time plots, and profile comparisons.
- **Chat Interface**: Ask questions about oceanographic data in natural language.
- **Real-time Data Explorer**: Browse and filter ARGO float measurements.

## Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Groq API, LangChain, FAISS
- **Database**: PostgreSQL, Vector Database (FAISS)
- **Data Processing**: xarray, pandas, netCDF4
- **Visualization**: Plotly, Folium
- **Data Format**: NetCDF, Parquet

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Groq API key

## Environment Variables

Create a `.env` file in the root directory:

```env
# PostgreSQL Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=Argo-RAG
PGUSER=postgres
PGPASSWORD=your_postgres_password

# Full Database URL
DATABASE_URL=postgresql://postgres:your_postgres_password@localhost:5432/Argo-RAG

# Groq AI Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=deepseek-r1-distill-llama-70badd
