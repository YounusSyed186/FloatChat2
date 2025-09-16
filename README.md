# ARGO Oceanographic Data Analysis Platform

An AI-powered oceanographic data analysis platform for ARGO float data with ultra-fast Groq LLM integration and interactive visualizations.

## Features

- **NetCDF Data Ingestion**: Process ARGO float NetCDF files and convert to structured formats
- **Dual Database System**: PostgreSQL for relational data, FAISS for vector embeddings
- **AI-Powered Queries**: Natural language processing using Groq API with RAG pipeline
- **Interactive Visualizations**: Geospatial maps, depth-time plots, and profile comparisons
- **Chat Interface**: Ask questions about oceanographic data in natural language
- **Real-time Data Explorer**: Browse and filter ARGO float measurements

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
- Groq API key (stored as an environment variable)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install streamlit groq langchain-groq psycopg2-binary faiss-cpu xarray pandas plotly numpy chromadb netcdf4 folium streamlit-folium langchain langchain-community python-dotenv
