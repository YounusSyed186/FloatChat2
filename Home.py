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
        --shadow: 0 4px 20px rgba(0,0,0,0.08);
        --gradient-blue: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-green: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --gradient-orange: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
        --gradient-purple: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%);
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
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow);
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
    
    /* Modern Feature Cards */
    .feature-card {
        background: var(--bg-card);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-blue);
    }
    
    .feature-card:nth-child(2)::before {
        background: var(--gradient-green);
    }
    
    .feature-card:nth-child(3)::before {
        background: var(--gradient-orange);
    }
    
    .feature-card:nth-child(4)::before {
        background: var(--gradient-purple);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--ocean-blue) 0%, var(--deep-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .feature-title {
        color: #2D3748;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .feature-description {
        color: #718096;
        line-height: 1.6;
        margin: 0;
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
        border-radius: 12px;
        border: none;
        background: linear-gradient(135deg, var(--ocean-blue) 0%, var(--deep-blue) 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.4);
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background: var(--bg-card);
        border: 1px solid #E0E4E7;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: var(--shadow);
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
        border-radius: 12px;
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(135deg, var(--ocean-blue) 0%, var(--deep-blue) 100%);
        border-radius: 12px;
    }

    /* Clickable cards */
    .clickable-card {
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-radius: 16px;
        padding: 1.5rem;
        background: white;
        box-shadow: var(--shadow);
    }
    
    .clickable-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    /* Card grid layout */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Modern badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .badge-blue {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        color: #1976D2;
    }
    
    .badge-green {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        color: #388E3C;
    }
    
    .badge-orange {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        color: #F57C00;
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
            <h3 class="feature-title">Data Ingestion & Processing</h3>
            <p class="feature-description">Upload and process ARGO NetCDF files with automated quality control and metadata extraction.</p>
            <div style="margin-top: 1rem;">
                <span class="badge badge-blue">Automated</span>
                <span class="badge badge-green">QC</span>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">AI-Powered Analysis</h3>
            <p class="feature-description">Ask questions in natural language using advanced MCP tools and Groq-powered AI assistance.</p>
            <div style="margin-top: 1rem;">
                <span class="badge badge-blue">Natural Language</span>
                <span class="badge badge-orange">MCP Tools</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">Interactive Exploration</h3>
            <p class="feature-description">Browse and filter oceanographic datasets with advanced search and filtering capabilities.</p>
            <div style="margin-top: 1rem;">
                <span class="badge badge-blue">Advanced Search</span>
                <span class="badge badge-green">Filtering</span>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3 class="feature-title">Advanced Visualizations</h3>
            <p class="feature-description">Create interactive maps, depth profiles, and scientific plots with real-time data updates.</p>
            <div style="margin-top: 1rem;">
                <span class="badge badge-blue">Interactive</span>
                <span class="badge badge-orange">Real-time</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions section
    st.markdown("### ⚡ Quick Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("📁 Upload Data", use_container_width=True):
            st.switch_page("pages/1_Data_Ingestion.py")
    
    with action_col2:
        if st.button("🔍 Explore Data", use_container_width=True):
            st.switch_page("pages/2_Data_Explorer.py")
    
    with action_col3:
        if st.button("🤖 AI Chat", use_container_width=True):
            st.switch_page("pages/3_AI_Chat.py")
    
    with action_col4:
        if st.button("📊 Visualize", use_container_width=True):
            st.switch_page("pages/4_Visualizations.py")
    
    # Modern footer with helpful tips
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #F8FAFC 0%, #EDF2F7 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-top: 3rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    ">
        <h4 style="color: #1E88E5; margin-bottom: 1.5rem; font-size: 1.3rem;">💡 Pro Tips</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
            <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <strong style="color: #2D3748;">🚀 Quick Start</strong><br>
                <span style="color: #718096; font-size: 0.9rem;">Begin with Data Ingestion to upload ARGO files</span>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <strong style="color: #2D3748;">🤖 AI Assistant</strong><br>
                <span style="color: #718096; font-size: 0.9rem;">Ask natural questions about your ocean data</span>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <strong style="color: #2D3748;">🛠️ Advanced Tools</strong><br>
                <span style="color: #718096; font-size: 0.9rem;">Use MCP tools for sophisticated analysis</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()