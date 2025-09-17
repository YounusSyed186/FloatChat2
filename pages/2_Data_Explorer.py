import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.connection import DatabaseManager
from visualization.plots import OceanographicPlots
from visualization.maps import OceanographicMaps
from config.settings import load_config
from utils.helpers import format_data_for_display, create_download_link
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Data Explorer - ARGO Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    /* Sub Headers */
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        background-color: #eef6fb;
        transform: translateY(-2px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        font-weight: 600;
        color: #444;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e4e9f0;
        color: #1f77b4;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #1f77b4, #155d91);
        color: white !important;
        box-shadow: 0px -2px 8px rgba(0,0,0,0.2);
        border: none;
    }

    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    div[data-testid="stSidebarUserContent"] {
        padding: 1rem;
    }

    /* Filter Section */
    .filter-section {
        background-color: white;
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    /* Info Box */
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

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

def main():
    """Main data explorer interface"""
    
    st.markdown('<h1 class="main-header">🔍 ARGO Data Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Browse, filter, and explore ARGO oceanographic data.")
    
    # Initialize components
    if not initialize_components():
        st.stop()
    
    # Display options sidebar
    st.sidebar.subheader("📊 Display Options")
    
    records_per_page = st.sidebar.selectbox(
        "Records per page",
        [10, 25, 50, 100, 200],
        index=2
    )
    
    show_coordinates = st.sidebar.checkbox("Show coordinates", value=True)
    show_metadata = st.sidebar.checkbox("Show metadata", value=False)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Profile Browser", "🗺️ Geographic View", "📊 Quick Statistics", "💾 Data Export"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Profile Browser</h2>', unsafe_allow_html=True)
        
        try:
            # Get profiles based on filters
            with st.spinner("Loading profiles..."):
                profiles_df = st.session_state.db_manager.get_profiles(
                    limit=records_per_page * 5  # Get more records for pagination
                )
            
            if profiles_df.empty:
                st.info("No profiles found matching your criteria. Try adjusting the filters.")
            else:
                # Apply quality filter on display
                display_df = profiles_df.copy()
                
                # Pagination
                total_records = len(display_df)
                total_pages = max(1, (total_records - 1) // records_per_page + 1)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    page = st.selectbox(
                        f"Page (showing {records_per_page} of {total_records} records)",
                        range(1, total_pages + 1)
                    )
                
                # Calculate page slice
                start_idx = (page - 1) * records_per_page
                end_idx = min(start_idx + records_per_page, total_records)
                page_df = display_df.iloc[start_idx:end_idx]
                
                # Format data for display
                formatted_df = format_data_for_display(page_df, show_coordinates, show_metadata)
                
                # Display profiles table
                st.dataframe(formatted_df, use_container_width=True)
                
                # Profile details section
                if not page_df.empty:
                    st.markdown('<h3 class="sub-header">Profile Details</h3>', unsafe_allow_html=True)
                    
                    # Profile selector
                    profile_options = {}
                    for idx, row in page_df.iterrows():
                        label = f"Float {row['float_id']} - Cycle {row['cycle_number']} ({row['measurement_date']})"
                        profile_options[label] = row['id']
                    
                    selected_profile_label = st.selectbox(
                        "Select profile to view details",
                        list(profile_options.keys())
                    )
                    
                    if selected_profile_label:
                        profile_id = profile_options[selected_profile_label]
                        
                        # Get measurements for selected profile
                        with st.spinner("Loading measurements..."):
                            measurements_df = st.session_state.db_manager.get_measurements_by_profile(profile_id)
                                            
                        if not measurements_df.empty:
                            # Profile overview
                            profile_info = page_df[page_df['id'] == profile_id].iloc[0]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Float ID", profile_info['float_id'])
                                st.markdown('</div>', unsafe_allow_html=True)
                            with col2:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Cycle Number", profile_info['cycle_number'])
                                st.markdown('</div>', unsafe_allow_html=True)
                            with col3:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Measurements", len(measurements_df))
                                st.markdown('</div>', unsafe_allow_html=True)
                            with col4:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.metric("Max Depth", f"{measurements_df['depth'].max():.1f} m")
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Measurement plots
                            st.markdown('<h3 class="sub-header">Measurement Profiles</h3>', unsafe_allow_html=True)
                            
                            # Parameter selection for plotting
                            available_params = [col for col in measurements_df.columns 
                                              if col in ['temperature', 'salinity', 'pressure', 'oxygen', 'nitrate', 'ph', 'chlorophyll']
                                              and measurements_df[col].notna().any()]
                            
                            if available_params:
                                selected_params = st.multiselect(
                                    "Select parameters to plot",
                                    available_params,
                                    default=available_params[:2]
                                )
                                
                                if selected_params:
                                    # Create depth profile plot
                                    profile_title = f"Float {profile_info['float_id']} - Cycle {profile_info['cycle_number']}"
                                    fig = st.session_state.plotter.create_depth_profile(
                                        measurements_df, selected_params, profile_title
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # T-S diagram if both temperature and salinity are available
                                    if 'temperature' in measurements_df.columns and 'salinity' in measurements_df.columns:
                                        ts_fig = st.session_state.plotter.create_ts_diagram(measurements_df)
                                        st.plotly_chart(ts_fig, use_container_width=True)
                            
                            # Raw data table
                            with st.expander("📋 View Raw Measurements"):
                                st.dataframe(measurements_df, use_container_width=True)
                        
                        else:
                            st.warning("No measurements found for this profile.")
        
        except Exception as e:
            st.error(f"Error loading profiles: {str(e)}")
    
    with tab2:
        st.markdown('<h2 class="sub-header">Geographic View</h2>', unsafe_allow_html=True)
        
        try:
            # Get profiles for mapping
            with st.spinner("Loading geographic data..."):
                profiles_df = st.session_state.db_manager.get_profiles(
                    limit=1000  # Limit for map performance
                )
            
            if profiles_df.empty:
                st.info("No profiles found for mapping. Try adjusting the filters.")
            else:
                # Map type selection
                map_type = st.selectbox(
                    "Select map type",
                    ["Float Trajectories", "Profile Density", "Parameter Values"]
                )
                
                if map_type == "Float Trajectories":
                    # Float selection for trajectory
                    unique_floats = profiles_df['float_id'].unique()
                    if len(unique_floats) > 20:
                        st.info(f"Showing trajectories for all {len(unique_floats)} floats. This may take a moment to load.")
                    
                    selected_float = st.selectbox(
                        "Select specific float (optional)",
                        ["All floats"] + list(unique_floats)
                    )
                    
                    float_id = None if selected_float == "All floats" else selected_float
                    
                    # Create trajectory map
                    with st.spinner("Generating trajectory map..."):
                        trajectory_map = st.session_state.mapper.create_float_trajectory_map(
                            profiles_df, float_id
                        )
                        st.components.v1.html(trajectory_map._repr_html_(), height=600)
                
                elif map_type == "Profile Density":
                    # Create density heatmap
                    with st.spinner("Generating density map..."):
                        density_map = st.session_state.mapper.create_density_map(profiles_df)
                        st.components.v1.html(density_map._repr_html_(), height=600)
                
                elif map_type == "Parameter Values":
                    # Parameter mapping requires measurements
                    st.info("Loading measurement data for parameter mapping...")
                    
                    # Get a sample of measurements for mapping
                    sample_profiles = profiles_df.head(100)  # Limit for performance
                    
                    measurements_list = []
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
                            selected_param = st.selectbox("Select parameter to map", available_params)
                            
                            # Depth range selection
                            depth_option = st.selectbox(
                                "Depth range",
                                ["Surface (0-50m)", "Intermediate (50-500m)", "Deep (>500m)", "All depths"]
                            )
                            
                            depth_ranges = {
                                "Surface (0-50m)": (0, 50),
                                "Intermediate (50-500m)": (50, 500),
                                "Deep (>500m)": (500, 10000),
                                "All depths": None
                            }
                            
                            depth_range = depth_ranges[depth_option]
                            
                            # Create parameter map
                            with st.spinner("Generating parameter map..."):
                                param_map = st.session_state.mapper.create_parameter_map(
                                    sample_profiles, all_measurements, selected_param, depth_range
                                )
                                st.components.v1.html(param_map._repr_html_(), height=600)
                        else:
                            st.warning("No suitable parameters found for mapping.")
                    else:
                        st.warning("No measurement data available for parameter mapping.")
        
        except Exception as e:
            st.error(f"Error creating maps: {str(e)}")
    
    with tab3:
        st.markdown('<h2 class="sub-header">Quick Statistics</h2>', unsafe_allow_html=True)
        
        try:
            # Get database statistics
            with st.spinner("Loading statistics..."):
                stats = st.session_state.db_manager.get_summary_statistics()
            
            if stats:
                # Overview metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Total Profiles", f"{stats.get('total_profiles', 0):,}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Total Measurements", f"{stats.get('total_measurements', 0):,}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Unique Floats", f"{stats.get('unique_floats', 0):,}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    if stats.get('total_measurements', 0) > 0 and stats.get('total_profiles', 0) > 0:
                        avg_measurements = stats['total_measurements'] / stats['total_profiles']
                        st.metric("Avg Measurements/Profile", f"{avg_measurements:.0f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Temporal coverage
                if stats.get('date_range'):
                    date_range = stats['date_range']
                    if date_range['earliest'] and date_range['latest']:
                        st.markdown('<h3 class="sub-header">Temporal Coverage</h3>', unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.write(f"**Earliest measurement:** {date_range['earliest'].strftime('%Y-%m-%d')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.write(f"**Latest measurement:** {date_range['latest'].strftime('%Y-%m-%d')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Duration
                        duration = date_range['latest'] - date_range['earliest']
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.write(f"**Data span:** {duration.days} days ({duration.days / 365.25:.1f} years)")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Geographic coverage
                if stats.get('geographic_coverage'):
                    geo = stats['geographic_coverage']
                    if all(v is not None for v in geo.values()):
                        st.markdown('<h3 class="sub-header">Geographic Coverage</h3>', unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.write(f"**Latitude range:** {geo['min_latitude']:.2f}°N to {geo['max_latitude']:.2f}°N")
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.write(f"**Longitude range:** {geo['min_longitude']:.2f}°E to {geo['max_longitude']:.2f}°E")
                            st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
    
    with tab4:
        st.markdown('<h2 class="sub-header">Data Export</h2>', unsafe_allow_html=True)
        
        try:
            # Export options
            export_format = st.selectbox(
                "Select export format",
                ["CSV", "Parquet", "NetCDF", "JSON"]
            )
            
            export_scope = st.selectbox(
                "Select data scope",
                ["All profiles", "Specific float", "Date range"]
            )
            
            # Additional export parameters based on scope
            export_filters = {}
            
            if export_scope == "Specific float":
                float_id = st.text_input("Enter Float ID")
                if float_id:
                    export_filters['float_id'] = float_id
            
            elif export_scope == "Date range":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start date", key="export_start")
                with col2:
                    end_date = st.date_input("End date", key="export_end")
                
                if start_date and end_date:
                    export_filters['start_date'] = datetime.combine(start_date, datetime.min.time())
                    export_filters['end_date'] = datetime.combine(end_date, datetime.max.time())
            
            # Include measurements option
            include_measurements = st.checkbox(
                "Include detailed measurements",
                help="Include individual depth measurements (increases file size significantly)"
            )
            
            # Export button
            if st.button("Generate Export", type="primary"):
                with st.spinner("Preparing export..."):
                    # Get profiles
                    export_profiles = st.session_state.db_manager.get_profiles(
                        limit=50000,  # Reasonable limit for export
                        filters=export_filters
                    )
                    
                    if export_profiles.empty:
                        st.warning("No data found for export with current criteria.")
                    else:
                        # Create download link
                        if include_measurements:
                            # Get measurements for all profiles
                            st.info("Loading detailed measurements... This may take a moment.")
                            
                            measurements_list = []
                            for profile_id in export_profiles['id']:
                                measurements = st.session_state.db_manager.get_measurements_by_profile(profile_id)
                                if not measurements.empty:
                                    measurements['profile_id'] = profile_id
                                    measurements_list.append(measurements)
                            
                            if measurements_list:
                                all_measurements = pd.concat(measurements_list, ignore_index=True)
                                # Merge with profile info
                                export_data = export_profiles.merge(
                                    all_measurements, left_on='id', right_on='profile_id'
                                )
                            else:
                                export_data = export_profiles
                        else:
                            export_data = export_profiles
                        
                        # Create download link
                        download_link = create_download_link(export_data, export_format)
                        
                        if download_link:
                            st.success(f"Export ready! {len(export_data)} records prepared.")
                            st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.error("Failed to create export file.")
        
        except Exception as e:
            st.error(f"Error preparing export: {str(e)}")

if __name__ == "__main__":
    main()