#!/usr/bin/env python3
"""
Advanced CSV Column Mapper and Processor
======================================

Comprehensive CSV processing system that handles column mapping between CSV files
and PostgreSQL database schemas with proper data type conversion and validation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


class AdvancedCSVMapper:
    """Advanced CSV processor with comprehensive column mapping"""

    def __init__(self, mapping_config_path: str = "config/csv_column_mapping.json"):
        self.mapping_config_path = Path(mapping_config_path)
        self.column_mappings = {}
        self.load_column_mappings()

    def load_column_mappings(self):
        """Load column mapping configuration"""
        try:
            if self.mapping_config_path.exists():
                with open(self.mapping_config_path, "r") as f:
                    config = json.load(f)
                    self.column_mappings = config.get("table_mappings", {})
                console.print(
                    f"✅ Loaded column mappings for {len(self.column_mappings)} tables"
                )
            else:
                console.print(
                    f"[yellow]⚠️ Mapping config not found: {self.mapping_config_path}[/yellow]"
                )
                self.column_mappings = {}
        except Exception as e:
            console.print(f"[red]❌ Failed to load column mappings: {e}[/red]")
            self.column_mappings = {}

    def clean_and_convert_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean and convert data types appropriately"""
        cleaned_df = df.copy()

        # Handle common data cleaning
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == "object":
                # Clean string columns
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                cleaned_df[col] = cleaned_df[col].replace(["nan", "None", ""], None)

                # Handle specific conversions based on column name
                if any(x in col.lower() for x in ["id", "number"]):
                    # Try to convert ID columns to appropriate format
                    try:
                        # Keep as string for IDs but clean them
                        cleaned_df[col] = cleaned_df[col].str.replace(
                            r"[^\w\-]", "", regex=True
                        )
                    except:
                        pass

                elif any(x in col.lower() for x in ["age", "position", "runners"]):
                    # Convert numeric columns
                    try:
                        cleaned_df[col] = pd.to_numeric(
                            cleaned_df[col], errors="coerce"
                        )
                    except:
                        pass

                elif any(x in col.lower() for x in ["date"]):
                    # Convert date columns
                    try:
                        cleaned_df[col] = pd.to_datetime(
                            cleaned_df[col], errors="coerce"
                        )
                    except:
                        pass

                elif any(x in col.lower() for x in ["rate", "percentage"]):
                    # Convert percentage/rate columns
                    try:
                        cleaned_df[col] = pd.to_numeric(
                            cleaned_df[col], errors="coerce"
                        )
                    except:
                        pass

        return cleaned_df

    def map_csv_columns(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Map CSV columns to database schema columns"""
        if table_name not in self.column_mappings:
            console.print(
                f"[yellow]⚠️ No column mapping found for table: {table_name}[/yellow]"
            )
            return df

        mapping = self.column_mappings[table_name]["column_mapping"]
        mapped_df = pd.DataFrame()

        console.print(f"\n📋 Mapping columns for table: [bold]{table_name}[/bold]")

        # Create mapping table for display
        mapping_table = Table(title=f"Column Mapping: {table_name}")
        mapping_table.add_column("Database Column", style="cyan")
        mapping_table.add_column("CSV Column(s)", style="green")
        mapping_table.add_column("Status", style="yellow")

        for db_col, csv_cols in mapping.items():
            if csv_cols is None:
                # Handle null mappings (columns not in CSV)
                mapped_df[db_col] = None
                mapping_table.add_row(db_col, "NULL", "🔴 Missing")
                continue

            # Handle both single strings and lists of possible column names
            if isinstance(csv_cols, str):
                csv_cols = [csv_cols]

            # Find the first matching column
            found_col = None
            for csv_col in csv_cols:
                if csv_col in df.columns:
                    found_col = csv_col
                    break

            if found_col:
                mapped_df[db_col] = df[found_col]
                mapping_table.add_row(db_col, found_col, "✅ Mapped")
            else:
                mapped_df[db_col] = None
                missing_cols = ", ".join(csv_cols)
                mapping_table.add_row(db_col, missing_cols, "🔴 Not Found")

        console.print(mapping_table)

        # Clean and convert the mapped data
        mapped_df = self.clean_and_convert_data(mapped_df, table_name)

        return mapped_df

    def process_csv_file(
        self, csv_path: str, table_name: str
    ) -> Optional[pd.DataFrame]:
        """Process a single CSV file for a specific table"""
        try:
            console.print(
                f"\n📄 Processing: [bold]{csv_path}[/bold] → [cyan]{table_name}[/cyan]"
            )

            if not Path(csv_path).exists():
                console.print(f"[red]❌ File not found: {csv_path}[/red]")
                return None

            # Read CSV
            df = pd.read_csv(csv_path)
            console.print(f"   📊 Original: {len(df)} rows, {len(df.columns)} columns")

            if df.empty:
                console.print(f"[yellow]⚠️ Empty CSV file: {csv_path}[/yellow]")
                return None

            # Map columns
            mapped_df = self.map_csv_columns(df, table_name)
            console.print(
                f"   ✅ Mapped: {len(mapped_df)} rows, {len(mapped_df.columns)} columns"
            )

            # Basic data validation
            non_null_cols = mapped_df.count()
            total_cells = len(mapped_df.columns) * len(mapped_df)
            filled_cells = non_null_cols.sum()
            coverage = (filled_cells / total_cells * 100) if total_cells > 0 else 0
            console.print(
                f"   📈 Data coverage: {coverage:.1f}% ({filled_cells}/{total_cells} cells)"
            )

            return mapped_df

        except Exception as e:
            console.print(f"[red]❌ Failed to process {csv_path}: {e}[/red]")
            logger.error(f"Error processing {csv_path}: {e}")
            return None

    def process_all_tables(self) -> Dict[str, pd.DataFrame]:
        """Process all CSV files according to the mapping configuration"""
        results = {}

        console.print("\n🔄 [bold blue]Advanced CSV Processing Started[/bold blue]")

        for table_name, config in self.column_mappings.items():
            csv_files = config.get("csv_files", [])

            console.print(f"\n📋 Processing table: [bold cyan]{table_name}[/bold cyan]")
            console.print(f"   📁 CSV files: {len(csv_files)}")

            dataframes = []
            for csv_file in csv_files:
                df = self.process_csv_file(csv_file, table_name)
                if df is not None and not df.empty:
                    dataframes.append(df)

            # Combine dataframes for this table
            if dataframes:
                combined_df = self.combine_dataframes(dataframes, table_name)
                results[table_name] = combined_df
                console.print(f"   ✅ Combined result: {len(combined_df)} rows")
            else:
                console.print(f"   [red]❌ No valid data for table: {table_name}[/red]")

        return results

    def combine_dataframes(
        self, dataframes: List[pd.DataFrame], table_name: str
    ) -> pd.DataFrame:
        """Combine multiple dataframes for the same table"""
        if not dataframes:
            return pd.DataFrame()

        if len(dataframes) == 1:
            return dataframes[0]

        console.print(f"   🔄 Combining {len(dataframes)} dataframes for {table_name}")

        # Combine all dataframes
        combined = pd.concat(dataframes, ignore_index=True)

        # Remove duplicates based on primary key if possible
        if not combined.empty and len(combined.columns) > 0:
            # Try to identify primary key column
            pk_candidates = [col for col in combined.columns if "ID" in col]
            if pk_candidates:
                pk_col = pk_candidates[0]
                before_count = len(combined)
                combined = combined.drop_duplicates(subset=[pk_col], keep="first")
                after_count = len(combined)
                if before_count != after_count:
                    console.print(
                        f"   🔄 Removed {before_count - after_count} duplicates based on {pk_col}"
                    )

        return combined

    def save_processed_data(
        self,
        processed_data: Dict[str, pd.DataFrame],
        output_dir: str = "data/daily_downloads",
    ) -> Dict[str, str]:
        """Save processed data to CSV files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        saved_files = {}

        for table_name, df in processed_data.items():
            if not df.empty:
                filename = f"mapped_{table_name}.csv"
                file_path = output_path / filename

                # Save with proper handling of null values
                df.to_csv(file_path, index=False, na_rep="")
                saved_files[table_name] = str(file_path)

                console.print(
                    f"✅ Saved: {file_path} ({len(df)} rows, {len(df.columns)} columns)"
                )

        return saved_files

    def generate_upload_manifest(
        self,
        processed_data: Dict[str, pd.DataFrame],
        output_dir: str = "data/daily_downloads",
    ) -> str:
        """Generate upload manifest for processed data"""
        # Save processed data first
        saved_files = self.save_processed_data(processed_data, output_dir)

        manifest_path = Path(output_dir) / "mapped_upload_manifest.json"

        manifest = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "processing_method": "advanced_csv_mapper",
            "files": {},
        }

        # Create manifest entries
        for table_name, file_path in saved_files.items():
            df = processed_data[table_name]
            manifest["files"][file_path] = {
                "table": table_name,
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "mapped": True,
                "column_count": int(len(df.columns)),
                "null_cells": int(df.isnull().sum().sum()),
            }

        # Save manifest
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        console.print(f"\n📋 Generated upload manifest: [bold]{manifest_path}[/bold]")
        return str(manifest_path)


def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    mapper = AdvancedCSVMapper()

    # Process all tables
    results = mapper.process_all_tables()

    # Generate summary
    console.print("\n📊 [bold green]Processing Summary[/bold green]")
    summary_table = Table(title="Advanced CSV Mapping Results")
    summary_table.add_column("Table", style="cyan")
    summary_table.add_column("Rows", style="green")
    summary_table.add_column("Columns", style="yellow")
    summary_table.add_column("Status", style="magenta")

    total_rows = 0
    for table_name, df in results.items():
        if not df.empty:
            rows = len(df)
            cols = len(df.columns)
            total_rows += rows
            status = "✅ Success"
            summary_table.add_row(table_name, str(rows), str(cols), status)
        else:
            summary_table.add_row(table_name, "0", "0", "❌ No Data")

    console.print(summary_table)
    console.print(f"\n📊 Total rows processed: [bold green]{total_rows}[/bold green]")

    # Generate upload manifest
    if results:
        manifest_path = mapper.generate_upload_manifest(results)
        console.print(
            f"\n🎯 Ready for upload with manifest: [bold green]{manifest_path}[/bold green]"
        )
    else:
        console.print(
            f"\n[red]❌ No data processed - check CSV files and mappings[/red]"
        )


if __name__ == "__main__":
    main()
