import pandas as pd
from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config.settings import get_database_connection_string
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages PostgreSQL database connections and operations for ARGO data
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_uri = get_database_connection_string(config)  # postgresql+psycopg2://user:pass@host:port/db
        self.engine = create_engine(self.db_uri, future=True)
        self._initialize_schema()

    def get_connection(self):
        """Return a new database connection."""
        try:
            return self.engine.connect()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get connection: {str(e)}")
            raise

    def _initialize_schema(self):
        """Create tables and indexes if they don't exist"""
        try:
            with self.engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS argo_profiles (
                        id SERIAL PRIMARY KEY,
                        float_id VARCHAR(50) NOT NULL,
                        cycle_number INTEGER,
                        latitude DECIMAL(10,6),
                        longitude DECIMAL(10,6),
                        measurement_date TIMESTAMP,
                        platform_number VARCHAR(50),
                        data_center VARCHAR(10),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_hash VARCHAR(64) UNIQUE
                    );
                """))

                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS argo_measurements (
                        id SERIAL PRIMARY KEY,
                        profile_id INTEGER REFERENCES argo_profiles(id) ON DELETE CASCADE,
                        pressure DECIMAL(10,4),
                        temperature DECIMAL(10,4),
                        salinity DECIMAL(10,4),
                        depth DECIMAL(10,4),
                        oxygen DECIMAL(10,4),
                        nitrate DECIMAL(10,4),
                        ph DECIMAL(10,4),
                        chlorophyll DECIMAL(10,4),
                        quality_flag INTEGER DEFAULT 1
                    );
                """))

                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS argo_metadata (
                        id SERIAL PRIMARY KEY,
                        profile_id INTEGER REFERENCES argo_profiles(id) ON DELETE CASCADE,
                        parameter_name VARCHAR(100),
                        parameter_value TEXT,
                        parameter_units VARCHAR(50)
                    );
                """))

                # Indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_argo_profiles_float_id ON argo_profiles(float_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_argo_profiles_date ON argo_profiles(measurement_date);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_argo_profiles_location ON argo_profiles(latitude, longitude);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_argo_measurements_profile ON argo_measurements(profile_id);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_argo_measurements_depth ON argo_measurements(depth);"))

                logger.info("Database schema initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize schema: {str(e)}")
            raise

    def insert_profile(self, profile_data: Dict[str, Any]) -> int:
        """Insert a new profile and return its ID"""
        try:
            with self.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO argo_profiles 
                        (float_id, cycle_number, latitude, longitude, measurement_date,
                         platform_number, data_center, file_hash)
                        VALUES (:float_id, :cycle_number, :latitude, :longitude, :measurement_date,
                                :platform_number, :data_center, :file_hash)
                        RETURNING id
                    """),
                    profile_data
                )
                profile_id = result.scalar()
                logger.info(f"Inserted profile with ID: {profile_id}")
                return profile_id
        except SQLAlchemyError as e:
            if "file_hash" in str(e):
                logger.warning(f"Profile already exists with hash: {profile_data.get('file_hash')}")
                return self.get_profile_id_by_hash(profile_data['file_hash'])
            else:
                logger.error(f"Failed to insert profile: {str(e)}")
                raise

    def insert_measurements(self, profile_id: int, measurements: List[Dict[str, Any]]):
        """Insert measurements for a profile"""
        try:
            with self.engine.begin() as conn:
                for measurement in measurements:
                    measurement['profile_id'] = profile_id
                conn.execute(
                    text("""
                        INSERT INTO argo_measurements
                        (profile_id, pressure, temperature, salinity, depth, oxygen, nitrate, ph, chlorophyll, quality_flag)
                        VALUES (:profile_id, :pressure, :temperature, :salinity, :depth, :oxygen, :nitrate, :ph, :chlorophyll, :quality_flag)
                    """),
                    measurements
                )
                logger.info(f"Inserted {len(measurements)} measurements for profile {profile_id}")
        except SQLAlchemyError as e:
            logger.error(f"Failed to insert measurements: {str(e)}")
            raise

    def get_profile_id_by_hash(self, file_hash: str) -> Optional[int]:
        """Get profile ID by file hash"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT id FROM argo_profiles WHERE file_hash = :hash"), {"hash": file_hash})
                row = result.fetchone()
                return row[0] if row else None
        except SQLAlchemyError as e:
            logger.error(f"Failed to get profile by hash: {str(e)}")
            return None

    def get_profiles(self, limit: int = 100, offset: int = 0, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """Get profiles with optional filters"""
        try:
            base_query = """
                SELECT id, float_id, cycle_number, latitude, longitude,
                       measurement_date, platform_number, data_center, created_at
                FROM argo_profiles
            """
            where_conditions = []
            params = {}

            if filters:
                if filters.get('float_id'):
                    where_conditions.append("float_id = :float_id")
                    params['float_id'] = filters['float_id']
                if filters.get('start_date'):
                    where_conditions.append("measurement_date >= :start_date")
                    params['start_date'] = filters['start_date']
                if filters.get('end_date'):
                    where_conditions.append("measurement_date <= :end_date")
                    params['end_date'] = filters['end_date']
                if filters.get('min_lat') is not None:
                    where_conditions.append("latitude >= :min_lat")
                    params['min_lat'] = filters['min_lat']
                if filters.get('max_lat') is not None:
                    where_conditions.append("latitude <= :max_lat")
                    params['max_lat'] = filters['max_lat']
                if filters.get('min_lon') is not None:
                    where_conditions.append("longitude >= :min_lon")
                    params['min_lon'] = filters['min_lon']
                if filters.get('max_lon') is not None:
                    where_conditions.append("longitude <= :max_lon")
                    params['max_lon'] = filters['max_lon']

            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)

            base_query += " ORDER BY measurement_date DESC LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = offset

            return pd.read_sql(text(base_query), self.engine, params=params)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get profiles: {str(e)}")
            return pd.DataFrame()

    def get_measurements_by_profile(self, profile_id: int) -> pd.DataFrame:
        """Get all measurements for a specific profile"""
        try:
            query = """
                SELECT pressure, temperature, salinity, depth, oxygen,
                       nitrate, ph, chlorophyll, quality_flag
                FROM argo_measurements
                WHERE profile_id = :profile_id
                ORDER BY depth
            """
            return pd.read_sql(text(query), self.engine, params={"profile_id": profile_id})
        except SQLAlchemyError as e:
            logger.error(f"Failed to get measurements for profile {profile_id}: {str(e)}")
            return pd.DataFrame()

    def get_total_records(self) -> int:
        """Get total number of profile records"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM argo_profiles"))
                return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get total records: {str(e)}")
            return 0

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Return summary statistics for Streamlit dashboard"""
        stats = {
            "total_profiles": 0,
            "total_measurements": 0,
            "unique_floats": 0,
            "date_range": {"earliest": None, "latest": None},
            "geographic_coverage": {"min_latitude": None, "max_latitude": None, "min_longitude": None, "max_longitude": None}
        }
        try:
            with self.engine.connect() as conn:
                # Total profiles
                stats["total_profiles"] = conn.execute(text("SELECT COUNT(*) FROM argo_profiles")).scalar() or 0
                # Total measurements
                stats["total_measurements"] = conn.execute(text("SELECT COUNT(*) FROM argo_measurements")).scalar() or 0
                # Unique floats
                stats["unique_floats"] = conn.execute(text("SELECT COUNT(DISTINCT float_id) FROM argo_profiles")).scalar() or 0
                # Date range
                earliest, latest = conn.execute(text("SELECT MIN(measurement_date), MAX(measurement_date) FROM argo_profiles")).fetchone()
                stats["date_range"]["earliest"] = earliest
                stats["date_range"]["latest"] = latest
                # Geographic coverage
                min_lat, max_lat, min_lon, max_lon = conn.execute(
                    text("SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude) FROM argo_profiles")
                ).fetchone()
                stats["geographic_coverage"].update({
                    "min_latitude": min_lat,
                    "max_latitude": max_lat,
                    "min_longitude": min_lon,
                    "max_longitude": max_lon
                })
        except SQLAlchemyError as e:
            logger.error(f"Failed to get summary statistics: {str(e)}")
        return stats

    def close(self):
        """Dispose SQLAlchemy engine"""
        self.engine.dispose()
        logger.info("Database connection closed")
