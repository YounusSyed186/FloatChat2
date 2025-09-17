import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import load_config
from database.connection import DatabaseManager
from vector_store.faiss_manager import FAISSManager

# Page configuration
st.set_page_config(
    page_title="FloatChat",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/argo/argo-platform',
        'Report a bug': 'https://github.com/argo/argo-platform/issues',
        'About': 'AI-Powered Conversational Interface for ARGO Ocean Data Discovery and Visualization'
    }
)

def initialize_app():
    """Initialize the application components"""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize database connection
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager(config)
            
        # Initialize vector store
        if 'vector_store' not in st.session_state:
            st.session_state.vector_store = FAISSManager()
            
        # Initialize session state variables
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
            
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            
        return True
        
    except Exception as e:
        st.error(f"Failed to initialize application: {str(e)}")
        st.error("Please check your configuration and database connection.")
        return False

def add_custom_css():
    """Add modern custom CSS styling"""
    st.markdown("""
    <style>
    /* Modern color palette */
    :root {
        --ocean-blue: #1E88E5;
        --deep-blue: #0D47A1;
        --light-blue: #E3F2FD;
        --success-green: #4CAF50;
        --warning-orange: #FF9800;
        --error-red: #F44336;
        --text-dark: #1A1A1A;
        --text-light: #666666;
        --bg-card: #FFFFFF;
        --shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, var(--ocean-blue) 0%, var(--deep-blue) 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* Feature cards */
    .feature-card {
        background: var(--bg-card);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--ocean-blue);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Status indicators */
    .status-connected {
        color: var(--success-green);
        font-weight: 600;
    }
    
    .status-warning {
        color: var(--warning-orange);
        font-weight: 600;
    }
    
    .status-error {
        color: var(--error-red);
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, var(--ocean-blue) 0%, var(--deep-blue) 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background: var(--bg-card);
        border: 1px solid #E0E4E7;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: var(--shadow);
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
        border-radius: 8px;
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(135deg, var(--ocean-blue) 0%, var(--deep-blue) 100%);
        border-radius: 8px;
    }

    /* Style for the clickable cards */
    .clickable-card {
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .clickable-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Add custom CSS
    add_custom_css()
    
    # Initialize the application
    if not initialize_app():
        st.stop()
    
    # Modern sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #1E88E5; margin: 0;">🌊 FloatChat</h1>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Interactive Oceanographic Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick status overview
        st.markdown("### 📊 System Status")
        
        # Database status
        db_status = "🟢 Connected" if st.session_state.get('db_manager') else "🔴 Disconnected"
        st.markdown(f"**Database:** {db_status}")
        
        # AI status
        ai_status = "🟢 Ready" if os.getenv('GROQ_API_KEY') else "🟡 API Key Missing"
        st.markdown(f"**AI Engine:** {ai_status}")
        
        # Vector store status
        vector_status = "🟢 Ready" if st.session_state.get('vector_store') else "🟡 Not Ready"
        st.markdown(f"**Vector Store:** {vector_status}")
        
        st.markdown("---")
        
        # Navigation help
        st.markdown("""
        ### 🧭 Navigation Guide
        
        **📁 Data Ingestion** - Upload ARGO files 
        **🔍 Data Explorer** - Browse datasets 
        **🤖 AI Chat** - Natural language queries 
        **📊 Visualizations** - Interactive plots 
        
        ---
        
        💡 **Tip:** Start with Data Ingestion to upload your ARGO NetCDF files!
        """)
    
    # Hero section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🌊 FloatChat</div>
        <div class="hero-subtitle">AI-Powered Conversational Interface for ARGO Ocean Data Discovery and Visualization</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Platform features in modern cards
    st.markdown("### 🚀 Platform Capabilities")
    
    # Feature cards in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 style="color: #1E88E5; margin-bottom: 0.5rem;">Data Ingestion & Processing</h3>
            <p style="color: #666; margin: 0;">Upload and process ARGO NetCDF files with automated quality control and metadata extraction.</p>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 style="color: #1E88E5; margin-bottom: 0.5rem;">AI-Powered Analysis</h3>
            <p style="color: #666; margin: 0;">Ask questions in natural language using advanced MCP tools and Groq-powered AI assistance.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 style="color: #1E88E5; margin-bottom: 0.5rem;">Interactive Exploration</h3>
            <p style="color: #666; margin: 0;">Browse and filter oceanographic datasets with advanced search and filtering capabilities.</p>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3 style="color: #1E88E5; margin-bottom: 0.5rem;">Advanced Visualizations</h3>
            <p style="color: #666; margin: 0;">Create interactive maps, depth profiles, and scientific plots with real-time data updates.</p>
        </div>
        """, unsafe_allow_html=True)
    
    
    st.markdown("---")
    

    

    
    # Modern footer with helpful tips
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 2rem;
        border: 1px solid #CBD5E0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    ">
        <h4 style="color: #1E88E5; margin-bottom: 1rem;">💡 Pro Tips</h4>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1rem;">
            <div style="flex: 1; min-width: 200px;">
                <strong>🚀 Quick Start:</strong><br>
                <span style="color: #64748B;">Begin with Data Ingestion to upload ARGO files</span>
            </div>
            <div style="flex: 1; min-width: 200px;">
                <strong>🤖 AI Assistant:</strong><br>
                <span style="color: #64748B;">Ask natural questions about your ocean data</span>
            </div>
            <div style="flex: 1; min-width: 200px;">
                <strong>🛠️ Advanced Tools:</strong><br>
                <span style="color: #64748B;">Use MCP tools for sophisticated analysis</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()