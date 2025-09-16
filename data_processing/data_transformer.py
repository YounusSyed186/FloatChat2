import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUALITY_FLAGS = {
    1: 'Good data',
    2: 'Probably good data',
    3: 'Bad data potentially correctable',
    4: 'Bad data',
    5: 'Value changed',
    6: 'Not used',
    7: 'Not used',
    8: 'Estimated value',
    9: 'Missing value'
}

class DataTransformer:
    """
    Transform and clean ARGO data for analysis and database storage
    """

    def __init__(self):
        self.parameter_ranges = {
            'temperature': (-5, 50),  # Celsius
            'salinity': (0, 50),      # PSU
            'pressure': (0, 10000),   # dbar
            'depth': (0, 10000),      # meters
            'oxygen': (0, 500),       # micromole/kg
            'nitrate': (0, 100),      # micromole/kg
            'ph': (6, 9),             # pH units
            'chlorophyll': (0, 100)   # mg/m3
        }

    def clean_measurements(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean ARGO measurements and align with schema"""
        df = df.copy()
        measurement_cols = ['temperature', 'salinity', 'pressure', 'oxygen', 'nitrate', 'ph', 'chlorophyll']
        available_cols = [c for c in measurement_cols if c in df.columns]

        # Drop rows where all measurement columns are null
        df = df.dropna(subset=available_cols, how='all')

        # Apply parameter ranges and update quality_flag
        for param, (min_val, max_val) in self.parameter_ranges.items():
            if param in df.columns:
                invalid_mask = (df[param] < min_val) | (df[param] > max_val)
                df.loc[invalid_mask, param] = np.nan
                if 'quality_flag' in df.columns:
                    df.loc[invalid_mask, 'quality_flag'] = 4  # Bad data

        # Remove duplicate depths
        if 'depth' in df.columns:
            df = df.drop_duplicates(subset=['depth'], keep='first')
            df = df.sort_values('depth')
        elif 'pressure' in df.columns:
            df = df.sort_values('pressure')

        return df

    def interpolate_missing_depth(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing depth values using pressure"""
        df = df.copy()
        if 'depth' not in df.columns and 'pressure' in df.columns:
            df['depth'] = df['pressure']
        elif 'depth' in df.columns and 'pressure' in df.columns:
            mask = df['depth'].isna() & df['pressure'].notna()
            df.loc[mask, 'depth'] = df.loc[mask, 'pressure']
        return df

    def calculate_derived_parameters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate potential_temperature, density, mixed_layer_depth"""
        df = df.copy()
        if 'temperature' in df.columns and 'pressure' in df.columns:
            df['potential_temperature'] = df['temperature'] - 0.1 * (df['pressure'] / 1000)
        if 'temperature' in df.columns and 'salinity' in df.columns:
            df['density'] = 1000 + 0.8 * df['salinity'] - 0.2 * df['temperature']
        if 'temperature' in df.columns and 'depth' in df.columns:
            surface_temp = df[df['depth'] <= 10]['temperature'].mean()
            if not np.isnan(surface_temp):
                temp_diff = np.abs(df['temperature'] - surface_temp)
                mld_idx = np.where(temp_diff > 0.2)[0]
                if len(mld_idx) > 0:
                    df['mixed_layer_depth'] = df.iloc[mld_idx[0]]['depth']
        return df

    def create_profile_summary(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate profile summary compatible with ARGO schema"""
        summary = metadata.copy()
        if df.empty:
            summary['summary_text'] = "Empty profile with no measurements"
            return summary

        # Compute stats
        stats = {}
        for param in ['temperature', 'salinity', 'pressure', 'depth', 'oxygen', 'nitrate', 'ph', 'chlorophyll']:
            if param in df.columns:
                param_data = df[param].dropna()
                if not param_data.empty:
                    stats[param] = {
                        'min': float(param_data.min()),
                        'max': float(param_data.max()),
                        'mean': float(param_data.mean()),
                        'std': float(param_data.std())
                    }
        summary['statistics'] = stats

        # Depth range
        if 'depth' in df.columns:
            depth_data = df['depth'].dropna()
            if not depth_data.empty:
                summary['depth_range'] = {
                    'min_depth': float(depth_data.min()),
                    'max_depth': float(depth_data.max())
                }

        # Data quality
        total = len(df)
        good_quality = len(df[df.get('quality_flag', 1) <= 2])
        summary['data_quality'] = {
            'total_measurements': total,
            'good_quality_measurements': good_quality,
            'quality_percentage': (good_quality / total * 100) if total else 0
        }

        # Summary text
        text_parts = []
        lat, lon = summary.get('latitude', 0), summary.get('longitude', 0)
        text_parts.append(f"ARGO float {summary.get('float_id', 'unknown')} profile at {lat:.2f}°N, {lon:.2f}°E")
        if 'measurement_date' in summary:
            date = summary['measurement_date']
            if isinstance(date, str):
                date = pd.to_datetime(date)
            text_parts.append(f"measured on {date.strftime('%Y-%m-%d')}")
        if 'depth_range' in summary:
            dr = summary['depth_range']
            text_parts.append(f"depth range {dr['min_depth']:.1f}m to {dr['max_depth']:.1f}m")
        for p in ['temperature', 'salinity', 'oxygen']:
            if p in stats:
                s = stats[p]
                units = '°C' if p=='temperature' else 'PSU' if p=='salinity' else 'μmol/kg'
                text_parts.append(f"{p} {s['min']:.2f}{units} to {s['max']:.2f}{units}")
        summary['summary_text'] = ". ".join(text_parts) + "."
        return summary

    def aggregate_profiles_by_region(self, df: pd.DataFrame, grid_size: float = 1.0) -> pd.DataFrame:
        """Aggregate profiles geographically"""
        if df.empty:
            return pd.DataFrame()
        df = df.copy()
        df['lat_grid'] = np.floor(df['latitude'] / grid_size) * grid_size
        df['lon_grid'] = np.floor(df['longitude'] / grid_size) * grid_size
        agg = df.groupby(['lat_grid', 'lon_grid']).agg({
            'id': 'count',
            'float_id': 'nunique',
            'measurement_date': ['min', 'max'],
            'latitude': 'mean',
            'longitude': 'mean'
        }).reset_index()
        agg.columns = [
            'lat_grid', 'lon_grid', 'profile_count', 'unique_floats',
            'earliest_date', 'latest_date', 'mean_latitude', 'mean_longitude'
        ]
        return agg

    def create_time_series(self, df: pd.DataFrame, parameter: str, depth_levels: List[float] = None) -> pd.DataFrame:
        """Time series for parameter at standard depths"""
        if df.empty or parameter not in df.columns:
            return pd.DataFrame()
        if depth_levels is None:
            depth_levels = [10, 50, 100, 200, 500, 1000]
        series = []
        for depth in depth_levels:
            if 'depth' in df.columns:
                diff = np.abs(df['depth'] - depth)
                idx = diff.idxmin()
                if diff.iloc[idx] <= 50:
                    val = df.loc[idx, parameter]
                    if not np.isnan(val):
                        series.append({'depth_level': depth, 'value': val, 'actual_depth': df.loc[idx, 'depth']})
        return pd.DataFrame(series)

    def detect_anomalies(self, df: pd.DataFrame, parameter: str) -> pd.DataFrame:
        """Detect anomalies using Z-score + IQR"""
        if df.empty or parameter not in df.columns:
            return df
        df = df.copy()
        data = df[parameter].dropna()
        if len(data) < 10:
            df['anomaly_flag'] = False
            return df
        mean_val, std_val = data.mean(), data.std()
        z_scores = np.abs((df[parameter] - mean_val) / std_val)
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        df['anomaly_flag'] = (z_scores > 3) | (df[parameter] < lower) | (df[parameter] > upper)
        df['z_score'] = z_scores
        return df
