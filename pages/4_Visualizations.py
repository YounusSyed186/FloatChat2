import streamlit as st
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.connection import DatabaseManager
from visualization.plots import OceanographicPlots
from visualization.maps import OceanographicMaps
from config.settings import load_config
import logging
import plotly.express as px

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for styling with animations
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes wave {
        0% { transform: rotate(0deg); }
        10% { transform: rotate(14deg); }
        20% { transform: rotate(-8deg); }
        30% { transform: rotate(14deg); }
        40% { transform: rotate(-4deg); }
        50% { transform: rotate(10deg); }
        60% { transform: rotate(0deg); }
        100% { transform: rotate(0deg); }
    }
    
    .animated-element {
        animation: fadeIn 1s ease-out;
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    .waving {
        display: inline-block;
        animation: wave 2s infinite;
        transform-origin: 70% 70%;
    }
    
    .main-header {
        font-size: 3rem;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a73e8 0%, #0066cc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fadeIn 1.5s ease-out;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #1a73e8;
        border-bottom: 2px solid #1a73e8;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 1s ease-out;
    }
    
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 1s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #e3f2fd;
        border-radius: 12px;
        gap: 8px;
        padding: 15px 20px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        margin: 4px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #bbdefb;
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a73e8 0%, #0066cc 100%);
        color: white;
        transform: scale(1.05);
        border: 2px solid #1a73e8;
        box-shadow: 0 6px 12px rgba(26, 115, 232, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .data-point {
        background-color: #e8f5e9;
        padding: 8px 12px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .data-point:hover {
        background-color: #c8e6c9;
        transform: translateX(5px);
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1a73e8;
        margin: 10px 0;
        animation: fadeIn 1s ease-out;
        transition: all 0.3s ease;
    }
    
    .info-box:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-3px);
    }
    
    .progress-bar {
        height: 5px;
        background: linear-gradient(90deg, #1a73e8 0%, #0066cc 100%);
        width: 0%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 9999;
        animation: progress 1s ease-in-out;
    }
    
    @keyframes progress {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    
    .fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.8s ease, transform 0.8s ease;
    }
    
    .fade-in.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .water-effect {
        position: relative;
        overflow: hidden;
    }
    
    .water-effect::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: rgba(255, 255, 255, 0.1);
        transform: rotate(30deg);
        animation: shine 3s infinite linear;
    }
    
    @keyframes shine {
        from { transform: translateY(-100%) rotate(30deg); }
        to { transform: translateY(100%) rotate(30deg); }
    }
    
    /* Filter section styling */
    .filter-section {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .filter-header {
        font-size: 1.4rem;
        color: #1a73e8;
        margin-bottom: 15px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="ARGO Visualizations - Ocean Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def initialize_components():
    """Initialize application components"""
    try:
        if 'config' not in st.session_state:
            st.session_state.config = load_config()
        
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager(st.session_state.config)
        
        if 'plotter' not in st.session_state:
            st.session_state.plotter = OceanographicPlots()
            
        if 'mapper' not in st.session_state:
            st.session_state.mapper = OceanographicMaps()
            
        return True
    except Exception as e:
        st.error(f"Failed to initialize components: {str(e)}")
        return False

def load_data_for_visualization():
    """Load and prepare data for visualization"""
    try:
        # Show loading animation
        with st.spinner('🌊 Diving into ocean data...'):
            # Get recent profiles for visualization
            profiles_df = st.session_state.db_manager.get_profiles(limit=1000)
            
            if profiles_df.empty:
                return None, None, "No profile data available"
            
            # Get sample measurements for plotting
            sample_profiles = profiles_df.head(50)  # Limit for performance
            measurements_list = []
            
            for profile_id in sample_profiles['id']:
                measurements = st.session_state.db_manager.get_measurements_by_profile(profile_id)
                if not measurements.empty:
                    measurements['profile_id'] = profile_id
                    measurements_list.append(measurements)
            
            if measurements_list:
                all_measurements = pd.concat(measurements_list, ignore_index=True)
                return profiles_df, all_measurements, None
            else:
                return profiles_df, pd.DataFrame(), "No measurement data available"
    
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        return None, None, f"Error loading data: {str(e)}"

def create_filters():
    """Create filters for visualization"""
    filters = {}
    quality_filter = "All Data"
    
    return filters, quality_filter

def display_data_summary(profiles_df, measurements_df):
    """Display a summary of the loaded data"""
    if profiles_df is not None and not profiles_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
            st.metric("Total Profiles", f"{len(profiles_df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
            st.metric("Unique Floats", profiles_df['float_id'].nunique())
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
            if 'measurement_date' in profiles_df.columns:
                date_range = f"{profiles_df['measurement_date'].min().date()} to {profiles_df['measurement_date'].max().date()}"
                st.metric("Date Range", date_range)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
            if not measurements_df.empty:
                st.metric("Measurements", f"{len(measurements_df):,}")
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main visualizations interface"""
    
    # Progress bar
    st.markdown('<div class="progress-bar"></div>', unsafe_allow_html=True)
    
    # Header with ocean theme
    st.markdown('<h1 class="main-header"><span class="waving">🌊</span> ARGO Ocean Data Explorer</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;' class="animated-element">
        <p style='font-size: 1.2rem; color: #5f6368;'>
        Explore interactive visualizations of oceanographic data collected by ARGO floats worldwide
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    if not initialize_components():
        st.stop()
    
    # Create filters
    filters, quality_filter = create_filters()
    
    # Load data with animation
    with st.spinner('🌊 Diving into ocean data...'):
        time.sleep(1)  # Simulate loading for animation effect
        profiles_df, measurements_df, error_msg = load_data_for_visualization()
    
    if error_msg:
        st.error(error_msg)
    else:
        # Display data summary
        display_data_summary(profiles_df, measurements_df)
    
    # Main content tabs with improved styling
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌊 Profile Analysis", 
        "🗺️ Geographic Maps", 
        "📈 Time Series", 
        "🔄 Parameter Comparison",
        "📊 Statistical Insights"
    ])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Ocean Profile Analysis</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            Analyze vertical profiles of ocean parameters like temperature, salinity, and oxygen at different depths.
        </div>
        """, unsafe_allow_html=True)
        
        try:
            if profiles_df is not None and not measurements_df.empty:
                
                # Apply filters
                with st.spinner('Filtering data...'):
                    filtered_profiles = st.session_state.db_manager.get_profiles(
                        limit=100, filters=filters
                    )
                
                if filtered_profiles.empty:
                    st.info("No profiles found with current filters.")
                else:
                    # Profile selection with better UI
                    st.markdown("### Select Ocean Profile")
                    profile_options = {}
                    for idx, row in filtered_profiles.head(20).iterrows():
                        date_str = row['measurement_date'].strftime('%Y-%m-%d') if 'measurement_date' in row else 'Unknown date'
                        label = f"Float {row['float_id']} - Cycle {row['cycle_number']} - {date_str} - ({row['latitude']:.2f}°N, {row['longitude']:.2f}°E)"
                        profile_options[label] = row['id']
                    
                    selected_profile = st.selectbox(
                        "Choose a profile to analyze:",
                        list(profile_options.keys()),
                        help="Select an ARGO float profile to visualize"
                    )
                    
                    if selected_profile:
                        profile_id = profile_options[selected_profile]
                        
                        # Get measurements for selected profile
                        with st.spinner('Loading profile data...'):
                            measurements = st.session_state.db_manager.get_measurements_by_profile(profile_id)
                        
                        if not measurements.empty:
                            # Filter by quality if requested
                            if quality_filter == "Good Quality Only" and 'quality_flag' in measurements.columns:
                                measurements = measurements[measurements['quality_flag'] <= 2]
                            
                            # Parameter selection with better UI
                            available_params = [col for col in measurements.columns 
                                              if col in ['temperature', 'salinity', 'pressure', 'oxygen', 'nitrate', 'ph', 'chlorophyll']
                                              and measurements[col].notna().any()]
                            
                            if available_params:
                                # Multi-parameter depth profile
                                st.markdown("### Depth Profile Visualization")
                                
                                selected_params = st.multiselect(
                                    "Select parameters to display:",
                                    available_params,
                                    default=available_params[:3] if len(available_params) >= 3 else available_params,
                                    help="Choose which ocean parameters to visualize in the depth profile"
                                )
                                
                                if selected_params:
                                    profile_info = filtered_profiles[filtered_profiles['id'] == profile_id].iloc[0]
                                    title = f"Float {profile_info['float_id']} - Cycle {profile_info['cycle_number']}"
                                    
                                    with st.spinner('Generating depth profile...'):
                                        depth_fig = st.session_state.plotter.create_depth_profile(
                                            measurements, selected_params, title
                                        )
                                    st.plotly_chart(depth_fig, use_container_width=True)
                                
                                # T-S Diagram
                                if 'temperature' in measurements.columns and 'salinity' in measurements.columns:
                                    st.markdown("### Temperature-Salinity Diagram")
                                    with st.spinner('Generating T-S diagram...'):
                                        ts_fig = st.session_state.plotter.create_ts_diagram(measurements)
                                    st.plotly_chart(ts_fig, use_container_width=True)
                                
                                # Parameter distributions
                                st.markdown("### Parameter Distribution Analysis")
                                
                                param_for_hist = st.selectbox(
                                    "Select parameter for distribution analysis:",
                                    available_params
                                )
                                
                                with st.spinner('Generating histogram...'):
                                    hist_fig = st.session_state.plotter.create_histogram(measurements, param_for_hist)
                                st.plotly_chart(hist_fig, use_container_width=True)
                                
                                # Parameter comparison
                                if len(available_params) >= 2:
                                    st.markdown("### Parameter Relationships")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        param1 = st.selectbox("X-axis parameter:", available_params, key="param1")
                                    with col2:
                                        param2 = st.selectbox("Y-axis parameter:", 
                                                            [p for p in available_params if p != param1], key="param2")
                                    
                                    if param1 and param2:
                                        with st.spinner('Generating comparison chart...'):
                                            comparison_fig = st.session_state.plotter.create_parameter_comparison(
                                                measurements, param1, param2
                                            )
                                        st.plotly_chart(comparison_fig, use_container_width=True)
                            else:
                                st.warning("No suitable parameters found for visualization.")
                        else:
                            st.warning("No measurements found for selected profile.")
            else:
                st.info("No data available for visualization.")
                
        except Exception as e:
            st.error(f"Error creating profile visualizations: {str(e)}")
    
    with tab2:
        st.markdown('<h2 class="sub-header">Geographic Data Exploration</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            Explore spatial patterns and distributions of ocean parameters across different regions of the world's oceans.
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Load profiles for mapping
            with st.spinner('Loading geographic data...'):
                profiles_df = st.session_state.db_manager.get_profiles(
                    limit=2000, filters=filters
                )
            
            if profiles_df.empty:
                st.info("No profiles found for mapping.")
            else:
                # Map type selection with better UI
                st.markdown("### Select Map Visualization Type")
                map_type = st.selectbox(
                    "Choose visualization type:",
                    ["Float Trajectories", "Profile Density Heatmap", "Parameter Distribution", "Regional Analysis"],
                    help="Select the type of geographic visualization to display"
                )
                
                if map_type == "Float Trajectories":
                    st.markdown("### ARGO Float Trajectories")
                    
                    # Float selection for trajectory
                    unique_floats = profiles_df['float_id'].unique()
                    float_selection = st.selectbox(
                        "Select float for trajectory (optional):",
                        ["All Floats"] + list(unique_floats[:20]),  # Limit for performance
                        help="Choose a specific float to view its trajectory or view all floats"
                    )
                    
                    selected_float = None if float_selection == "All Floats" else float_selection
                    
                    with st.spinner('Generating trajectory map...'):
                        trajectory_map = st.session_state.mapper.create_float_trajectory_map(
                            profiles_df, selected_float
                        )
                    st.components.v1.html(trajectory_map._repr_html_(), height=600)
                
                elif map_type == "Profile Density Heatmap":
                    st.markdown("### Profile Density Distribution")
                    
                    with st.spinner('Generating density map...'):
                        density_map = st.session_state.mapper.create_density_map(profiles_df)
                    st.components.v1.html(density_map._repr_html_(), height=600)
                
                elif map_type == "Parameter Distribution":
                    st.markdown("### Parameter Spatial Distribution")
                    
                    # Load measurements for parameter mapping
                    sample_profiles = profiles_df.head(100)  # Limit for performance
                    measurements_list = []
                    
                    with st.spinner('Loading measurement data...'):
                        for profile_id in sample_profiles['id']:
                            measurements = st.session_state.db_manager.get_measurements_by_profile(profile_id)
                            if not measurements.empty:
                                measurements['profile_id'] = profile_id
                                measurements_list.append(measurements)
                    
                    if measurements_list:
                        all_measurements = pd.concat(measurements_list, ignore_index=True)
                        
                        # Parameter selection
                        available_params = [col for col in all_measurements.columns 
                                          if col in ['temperature', 'salinity', 'oxygen', 'nitrate', 'ph', 'chlorophyll']
                                          and all_measurements[col].notna().any()]
                        
                        if available_params:
                            selected_param = st.selectbox("Select parameter to map:", available_params)
                            
                            # Depth range selection
                            depth_ranges = {
                                "Surface (0-50m)": (0, 50),
                                "Intermediate (50-500m)": (50, 500),
                                "Deep (>500m)": (500, 10000),
                                "All depths": None
                            }
                            
                            depth_selection = st.selectbox("Select depth range:", list(depth_ranges.keys()))
                            depth_range = depth_ranges[depth_selection]
                            
                            with st.spinner('Generating parameter map...'):
                                param_map = st.session_state.mapper.create_parameter_map(
                                    sample_profiles, all_measurements, selected_param, depth_range
                                )
                            st.components.v1.html(param_map._repr_html_(), height=600)
                        else:
                            st.warning("No suitable parameters found for mapping.")
                    else:
                        st.warning("No measurement data available for parameter mapping.")
                
                elif map_type == "Regional Analysis":
                    st.markdown("### Regional Data Analysis")
                    
                    # Define analysis regions
                    regions = {
                        "Arabian Sea": {"min_lat": 10, "max_lat": 25, "min_lon": 50, "max_lon": 80},
                        "Bay of Bengal": {"min_lat": 5, "max_lat": 22, "min_lon": 80, "max_lon": 100},
                        "Equatorial Indian Ocean": {"min_lat": -10, "max_lat": 10, "min_lon": 50, "max_lon": 100},
                        "Southern Ocean": {"min_lat": -60, "max_lat": -30, "min_lon": 20, "max_lon": 120}
                    }
                    
                    selected_region = st.selectbox("Select region for analysis:", list(regions.keys()))
                    region_bounds = regions[selected_region]
                    
                    with st.spinner('Generating regional map...'):
                        regional_map = st.session_state.mapper.create_regional_map(profiles_df, region_bounds)
                    st.components.v1.html(regional_map._repr_html_(), height=600)
                    
                    # Regional statistics
                    regional_profiles = profiles_df[
                        (profiles_df['latitude'] >= region_bounds['min_lat']) &
                        (profiles_df['latitude'] <= region_bounds['max_lat']) &
                        (profiles_df['longitude'] >= region_bounds['min_lon']) &
                        (profiles_df['longitude'] <= region_bounds['max_lon'])
                    ]
                    
                    if not regional_profiles.empty:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
                            st.metric("Profiles in Region", len(regional_profiles))
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
                            st.metric("Unique Floats", regional_profiles['float_id'].nunique())
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col3:
                            if 'measurement_date' in regional_profiles.columns:
                                st.markdown('<div class="metric-card water-effect">', unsafe_allow_html=True)
                                date_span = (regional_profiles['measurement_date'].max() - 
                                           regional_profiles['measurement_date'].min()).days
                                st.metric("Date Span (days)", date_span)
                                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error creating geographic visualizations: {str(e)}")
    
    with tab3:
        st.markdown('<h2 class="sub-header">Time Series Analysis</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            Explore how ocean parameters change over time with interactive time series visualizations.
        </div>
        """, unsafe_allow_html=True)
        
        try:
            if profiles_df is not None and not profiles_df.empty:
                st.info("Time series analysis functionality would be implemented here.")
                
                # Example time series plot
                if 'measurement_date' in profiles_df.columns:
                    time_series_data = profiles_df.groupby('measurement_date').size().reset_index(name='profile_count')
                    time_series_fig = px.line(time_series_data, x='measurement_date', y='profile_count', 
                                            title='Number of Profiles Over Time')
                    st.plotly_chart(time_series_fig, use_container_width=True)
            else:
                st.info("No data available for time series analysis.")
                
        except Exception as e:
            st.error(f"Error creating time series visualizations: {str(e)}")
    
    with tab4:
        st.markdown('<h2 class="sub-header">Parameter Comparison</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            Compare different ocean parameters and explore their relationships through scatter plots and correlation analysis.
        </div>
        """, unsafe_allow_html=True)
        
        try:
            if profiles_df is not None and not measurements_df.empty:
                st.info("Parameter comparison functionality would be implemented here.")
                
                # Example scatter plot
                if 'temperature' in measurements_df.columns and 'salinity' in measurements_df.columns:
                    sample_data = measurements_df.sample(min(1000, len(measurements_df)))
                    scatter_fig = px.scatter(sample_data, x='temperature', y='salinity', 
                                           title='Temperature vs Salinity Relationship')
                    st.plotly_chart(scatter_fig, use_container_width=True)
            else:
                st.info("No data available for parameter comparison.")
                
        except Exception as e:
            st.error(f"Error creating parameter comparison visualizations: {str(e)}")
    
    with tab5:
        st.markdown('<h2 class="sub-header">Statistical Insights</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            Gain statistical insights from the oceanographic data with advanced analytics and visualizations.
        </div>
        """, unsafe_allow_html=True)
        
        try:
            if profiles_df is not None and not profiles_df.empty:
                st.info("Statistical insights functionality would be implemented here.")
                
                # Example statistical summary
                if not measurements_df.empty:
                    numeric_cols = measurements_df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 0:
                        st.dataframe(measurements_df[numeric_cols].describe(), use_container_width=True)
            else:
                st.info("No data available for statistical analysis.")
                
        except Exception as e:
            st.error(f"Error creating statistical visualizations: {str(e)}")
    
    # Footer with attribution
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #5f6368;' class="animated-element">
        <p>ARGO Ocean Data Explorer | Powered by Streamlit</p>
        <p>Data provided by the international ARGO program</p>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript for scroll animations
    st.markdown("""
    <script>
    // Function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Add scroll event listener for fade-in animations
    document.addEventListener('DOMContentLoaded', function() {
        const fadeElements = document.querySelectorAll('.fade-in');
        
        function checkFade() {
            fadeElements.forEach(function(element) {
                if (isInViewport(element)) {
                    element.classList.add('visible');
                }
            });
        }
        
        // Check on load and scroll
        checkFade();
        window.addEventListener('scroll', checkFade);
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()