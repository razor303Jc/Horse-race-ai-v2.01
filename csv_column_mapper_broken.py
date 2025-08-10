#!/usr/bin/env python3
"""
Column Mapping Solution for Database Upload
===========================================

Maps CSV columns from horseracedatabase.com to our PostgreSQL schema.
Handles the mismatch between downloaded CSV structure and database tables.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Maps CSV columns to database columns for each table
    """

    def __init__(self):
        # Define column mappings for each table
        self.column_mappings = {
        "data/daily_downloads/results_data/race_results/race_results.csv":
            "race_results",
        "data/daily_downloads/results_data/horses/horses.csv": "horses",
        "data/daily_downloads/results_data/jockeys_stats/jockeys_stats.csv":
            "jockey_stats",
        "data/daily_downloads/results_data/trainers_stats/trainers_stats.csv":
            "trainer_stats",
        "data/daily_downloads/cards_data/races/races.csv": "races_cards",
        "data/daily_downloads/cards_data/racecard_details/racecard_details.csv":
            "racecard_details",
    }

    def map_dataframe_columns(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Map CSV DataFrame columns to database columns
        
        Args:
            df: Input DataFrame with CSV columns
            table_name: Target database table name
            
        Returns:
            DataFrame with mapped columns
        """
        if table_name not in self.column_mappings:
            logger.warning(f"No column mapping defined for table: {table_name}")
            return df
            
        mapping = self.column_mappings[table_name]
        mapped_df = pd.DataFrame()
        
        logger.info(f"Mapping columns for {table_name}:")
        
        # Map each column that exists in both CSV and mapping
        for csv_col, db_col in mapping.items():
            if csv_col in df.columns:
                mapped_df[db_col] = df[csv_col].copy()
                
                # Handle special data type conversions
                if (db_col == 'uptodate' and
                        table_name in ['trainer_stats', 'jockey_stats']):
                    # Convert UptoDate column to proper date format
                    # If it's 0, convert to None (NULL), otherwise convert to date
                    mapped_df[db_col] = pd.to_datetime(
                        mapped_df[db_col], errors='coerce'
                    )
                    # Replace NaT with None for SQL NULL
                    mapped_df[db_col] = mapped_df[db_col].where(
                        pd.notna(mapped_df[db_col]), None
                    )
                
                # Convert percentage columns from basis points to percentages
                if (db_col in ['win_percentage', 'place_percentage'] and
                        table_name in ['trainer_stats', 'jockey_stats', 'horses']):
                    # Convert from basis points (10000 = 100%) to percentage (100.00)
                    mapped_df[db_col] = mapped_df[db_col] / 100.0
                
                # Convert horse age to foaled year
                if db_col == 'foaled' and table_name == 'horses':
                    # Calculate foaled year: current_year - age
                    # Assuming current year is 2025 based on the data
                    current_year = 2025
                    mapped_df[db_col] = current_year - mapped_df[db_col]
                
                logger.info(f"  {csv_col} -> {db_col}")
            else:
                logger.warning(f"  CSV column '{csv_col}' not found in data")
        
        # Add any required database columns that aren't mapped
        required_cols = self._get_required_database_columns(table_name)
        for col in required_cols:
            if col not in mapped_df.columns:
                mapped_df[col] = None  # or appropriate default
                logger.info(f"  Added missing required column: {col}")
        
        logger.info(f"Mapped DataFrame shape: {mapped_df.shape}")
        return mapped_df

    def _get_required_database_columns(self, table_name: str) -> List[str]:
        """Get list of required columns for database table"""
        # This would ideally query the database schema
        # For now, return common required columns
        common_required = []
        
        # Don't add auto-generated columns
        excluded_cols = ['id', 'created_at', 'updated_at']
        
        return [col for col in common_required if col not in excluded_cols]

    def validate_mapped_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """
        Validate that mapped data is suitable for database insertion
        
        Args:
            df: Mapped DataFrame
            table_name: Target table name
            
        Returns:
            True if validation passes
        """
        if df.empty:
            logger.error(f"Empty DataFrame for {table_name}")
            return False
            
        # Check for completely null columns
        null_cols = df.columns[df.isnull().all()].tolist()
        if null_cols:
            logger.warning(f"Completely null columns in {table_name}: {null_cols}")
        
        # Specific validations per table
        if table_name == "race_results":
            return self._validate_race_results(df)
        elif table_name == "horses":
            return self._validate_horses(df)
        elif table_name in ["jockey_stats", "trainer_stats"]:
            return self._validate_stats(df, table_name)
        
        return True

    def _validate_race_results(self, df: pd.DataFrame) -> bool:
        """Validate race results data"""
        required_cols = ['race_id', 'horse_name']
        
        for col in required_cols:
            if col not in df.columns:
                logger.error(f"Missing required column for race_results: {col}")
                return False
                
            if df[col].isnull().all():
                logger.error(f"All null values in required column: {col}")
                return False
        
        return True

    def _validate_horses(self, df: pd.DataFrame) -> bool:
        """Validate horses data"""
        if 'horse_name' in df.columns and df['horse_name'].isnull().all():
            logger.error("All horse names are null")
            return False
        return True

    def _validate_stats(self, df: pd.DataFrame, table_name: str) -> bool:
        """Validate jockey/trainer stats data"""
        name_col = 'jockey_name' if 'jockey' in table_name else 'trainer_name'
        
        if name_col in df.columns and df[name_col].isnull().all():
            logger.error(f"All {name_col} values are null")
            return False
        return True

    def get_sample_mapping(self, csv_file: str, table_name: str) -> Dict[str, str]:
        """
        Get sample of CSV columns and their database mappings
        
        Returns:
            Dictionary showing CSV -> DB column mapping
        """
        try:
            # Read just the header
            df_sample = pd.read_csv(csv_file, nrows=0)
            csv_columns = df_sample.columns.tolist()
            
            mapping = self.column_mappings.get(table_name, {})
            
            result = {}
            for csv_col in csv_columns:
                db_col = mapping.get(csv_col, "** NO MAPPING **")
                result[csv_col] = db_col
                
            return result
            
        except Exception as e:
            logger.error(f"Error reading CSV sample: {e}")
            return {}


def main():
    """Test the column mapper"""
    mapper = ColumnMapper()
    
    # Test with actual files
    test_files = {
        "data/daily_downloads/results_data/records/records.csv": "race_results",
        "data/daily_downloads/results_data/horses/horses.csv": "horses", 
        "data/daily_downloads/results_data/jockeys_stats/jockeys_stats.csv": "jockey_stats",
        "data/daily_downloads/results_data/trainers_stats/trainers_stats.csv": "trainer_stats",
    }
    
    for csv_file, table_name in test_files.items():
        print(f"\n=== {table_name.upper()} MAPPING ===")
        mapping = mapper.get_sample_mapping(csv_file, table_name)
        
        print("CSV Column -> Database Column:")
        for csv_col, db_col in mapping.items():
            status = "✅" if db_col != "** NO MAPPING **" else "❌"
            print(f"{status} {csv_col} -> {db_col}")


if __name__ == "__main__":
    main()
