#!/usr/bin/env python3
"""
Data Export Utilities for Horse Racing AI V2.03
Provides comprehensive data export capabilities (CSV, PDF, Excel, JSON)
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import io
import base64

# PDF and Excel libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        Image,
    )
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.chart import LineChart, BarChart, Reference

    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExportRequest:
    """Data class for export requests"""

    export_id: str
    format_type: str  # 'csv', 'excel', 'pdf', 'json'
    data_source: str
    filters: Dict[str, Any]
    columns: Optional[List[str]]
    output_path: Optional[str]
    options: Dict[str, Any]
    created_at: datetime


class DataExporter:
    """
    Data Export Engine providing comprehensive export capabilities
    for CSV, Excel, PDF, and JSON formats
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Data Exporter"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.output_dir = Path(self.config.get("output_directory", "reports/exports"))

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Export format support
        self.supported_formats = ["csv", "json"]
        if EXCEL_AVAILABLE:
            self.supported_formats.append("excel")
        if PDF_AVAILABLE:
            self.supported_formats.append("pdf")

        logger.info(
            f"Data Exporter initialized. Supported formats: {self.supported_formats}"
        )

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        # Default configuration
        return {
            "database_path": "data/racing_data_tracking.db",
            "output_directory": "reports/exports",
            "max_rows_per_export": 100000,
            "excel_sheet_max_rows": 1048576,
            "pdf_rows_per_page": 50,
            "date_format": "%Y-%m-%d",
            "datetime_format": "%Y-%m-%d %H:%M:%S",
        }

    async def get_data_from_source(
        self, source: str, filters: Dict[str, Any] = None, columns: List[str] = None
    ) -> pd.DataFrame:
        """Get data from specified source with optional filtering"""

        try:
            conn = sqlite3.connect(self.db_path)

            # Define available data sources and their queries
            queries = {
                "races": """
                    SELECT r.*, t.track_name, t.surface_type, t.distance_unit
                    FROM races r
                    LEFT JOIN tracks t ON r.track_code = t.track_code
                """,
                "predictions": """
                    SELECT pr.*, r.race_date, r.track_code, r.race_type, r.distance
                    FROM prediction_results pr
                    JOIN races r ON pr.race_id = r.race_id
                """,
                "horses": """
                    SELECT h.*, hr.rating, hr.form_rating
                    FROM horses h
                    LEFT JOIN horse_ratings hr ON h.horse_id = hr.horse_id
                """,
                "jockeys": """
                    SELECT j.*, jr.win_rate, jr.place_rate
                    FROM jockeys j
                    LEFT JOIN jockey_stats jr ON j.jockey_id = jr.jockey_id
                """,
                "trainers": """
                    SELECT t.*, ts.win_rate, ts.place_rate, ts.total_runs
                    FROM trainers t
                    LEFT JOIN trainer_stats ts ON t.trainer_id = ts.trainer_id
                """,
                "betting_results": """
                    SELECT br.*, r.race_date, r.track_code, r.race_type
                    FROM betting_results br
                    JOIN races r ON br.race_id = r.race_id
                """,
            }

            if source not in queries:
                raise ValueError(f"Unknown data source: {source}")

            query = queries[source]
            params = []

            # Apply filters
            if filters:
                where_conditions = []

                # Date range filtering
                if filters.get("start_date"):
                    where_conditions.append("r.race_date >= ?")
                    params.append(filters["start_date"])

                if filters.get("end_date"):
                    where_conditions.append("r.race_date <= ?")
                    params.append(filters["end_date"])

                # Track filtering
                if filters.get("track_code"):
                    where_conditions.append("r.track_code = ?")
                    params.append(filters["track_code"])

                # Race type filtering
                if filters.get("race_type"):
                    where_conditions.append("r.race_type = ?")
                    params.append(filters["race_type"])

                # Add WHERE clause if conditions exist
                if where_conditions:
                    if "WHERE" in query.upper():
                        query += " AND " + " AND ".join(where_conditions)
                    else:
                        query += " WHERE " + " AND ".join(where_conditions)

            # Add ORDER BY for consistent results
            if "ORDER BY" not in query.upper():
                if "race_date" in source or source in [
                    "races",
                    "predictions",
                    "betting_results",
                ]:
                    query += " ORDER BY r.race_date DESC"
                else:
                    query += " ORDER BY created_at DESC"

            # Limit results to prevent memory issues
            max_rows = self.config.get("max_rows_per_export", 100000)
            query += f" LIMIT {max_rows}"

            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            # Filter columns if specified
            if columns and len(columns) > 0:
                available_columns = [col for col in columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
                else:
                    logger.warning(
                        f"None of the specified columns found in data: {columns}"
                    )

            logger.info(f"Retrieved {len(df)} records from {source}")
            return df

        except Exception as e:
            logger.error(f"Error retrieving data from {source}: {e}")
            return pd.DataFrame()

    async def export_to_csv(
        self, export_request: ExportRequest, data: pd.DataFrame
    ) -> str:
        """Export data to CSV format"""

        try:
            # Generate filename if not provided
            if not export_request.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{export_request.data_source}_{timestamp}.csv"
                output_path = self.output_dir / filename
            else:
                output_path = Path(export_request.output_path)

            # CSV export options
            options = export_request.options or {}
            csv_options = {
                "index": options.get("include_index", False),
                "sep": options.get("separator", ","),
                "encoding": options.get("encoding", "utf-8"),
                "date_format": self.config.get("date_format", "%Y-%m-%d"),
            }

            # Export to CSV
            data.to_csv(output_path, **csv_options)

            logger.info(f"Data exported to CSV: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise

    async def export_to_excel(
        self, export_request: ExportRequest, data: pd.DataFrame
    ) -> str:
        """Export data to Excel format with styling"""

        if not EXCEL_AVAILABLE:
            raise RuntimeError(
                "Excel export not available. Install openpyxl: pip install openpyxl"
            )

        try:
            # Generate filename if not provided
            if not export_request.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{export_request.data_source}_{timestamp}.xlsx"
                output_path = self.output_dir / filename
            else:
                output_path = Path(export_request.output_path)

            # Excel export options
            options = export_request.options or {}

            # Create Excel writer
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                # Check if data needs to be split across multiple sheets
                max_rows = (
                    self.config.get("excel_sheet_max_rows", 1048576) - 1
                )  # Leave room for header

                if len(data) <= max_rows:
                    # Single sheet
                    sheet_name = options.get("sheet_name", "Data")
                    data.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Apply styling
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]
                    self._style_excel_worksheet(worksheet, data)

                else:
                    # Multiple sheets
                    num_sheets = (len(data) + max_rows - 1) // max_rows

                    for i in range(num_sheets):
                        start_idx = i * max_rows
                        end_idx = min((i + 1) * max_rows, len(data))
                        sheet_data = data.iloc[start_idx:end_idx]

                        sheet_name = f"Data_Part_{i+1}"
                        sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

                        # Apply styling
                        workbook = writer.book
                        worksheet = writer.sheets[sheet_name]
                        self._style_excel_worksheet(worksheet, sheet_data)

            logger.info(f"Data exported to Excel: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise

    def _style_excel_worksheet(self, worksheet, data: pd.DataFrame):
        """Apply styling to Excel worksheet"""

        try:
            # Header styling
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(
                start_color="366092", end_color="366092", fill_type="solid"
            )
            header_alignment = Alignment(horizontal="center", vertical="center")

            # Apply header styling
            for col_num, column_title in enumerate(data.columns, 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Freeze header row
            worksheet.freeze_panes = "A2"

        except Exception as e:
            logger.warning(f"Could not apply Excel styling: {e}")

    async def export_to_pdf(
        self, export_request: ExportRequest, data: pd.DataFrame
    ) -> str:
        """Export data to PDF format"""

        if not PDF_AVAILABLE:
            raise RuntimeError(
                "PDF export not available. Install reportlab: pip install reportlab"
            )

        try:
            # Generate filename if not provided
            if not export_request.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{export_request.data_source}_{timestamp}.pdf"
                output_path = self.output_dir / filename
            else:
                output_path = Path(export_request.output_path)

            # PDF export options
            options = export_request.options or {}
            page_size = options.get("page_size", "A4")
            orientation = options.get("orientation", "portrait")

            # Create PDF document
            if page_size.upper() == "A4":
                pagesize = A4
            else:
                pagesize = letter

            if orientation == "landscape":
                pagesize = (pagesize[1], pagesize[0])

            doc = SimpleDocTemplate(str(output_path), pagesize=pagesize)
            story = []

            # Add title
            styles = getSampleStyleSheet()
            title = options.get(
                "title", f"{export_request.data_source.title()} Export Report"
            )
            story.append(Paragraph(title, styles["Title"]))
            story.append(Spacer(1, 12))

            # Add metadata
            story.append(
                Paragraph(
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    styles["Normal"],
                )
            )
            story.append(Paragraph(f"Records: {len(data)}", styles["Normal"]))
            story.append(Spacer(1, 12))

            # Convert DataFrame to table data
            rows_per_page = self.config.get("pdf_rows_per_page", 50)

            # Limit columns for PDF readability
            if len(data.columns) > 8:
                display_columns = data.columns[:8].tolist()
                table_data = data[display_columns]
                story.append(
                    Paragraph("Note: Showing first 8 columns only", styles["Normal"])
                )
                story.append(Spacer(1, 6))
            else:
                table_data = data

            # Process data in chunks
            for chunk_start in range(0, len(table_data), rows_per_page):
                chunk_end = min(chunk_start + rows_per_page, len(table_data))
                chunk_data = table_data.iloc[chunk_start:chunk_end]

                # Create table
                table_list = [chunk_data.columns.tolist()]
                table_list.extend(chunk_data.values.tolist())

                # Convert to strings and handle None values
                processed_table = []
                for row in table_list:
                    processed_row = [
                        str(cell) if cell is not None else "" for cell in row
                    ]
                    processed_table.append(processed_row)

                table = Table(processed_table)

                # Style the table
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 1), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                story.append(table)

                # Add page break if not the last chunk
                if chunk_end < len(table_data):
                    story.append(Spacer(1, 12))

            # Build PDF
            doc.build(story)

            logger.info(f"Data exported to PDF: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise

    async def export_to_json(
        self, export_request: ExportRequest, data: pd.DataFrame
    ) -> str:
        """Export data to JSON format"""

        try:
            # Generate filename if not provided
            if not export_request.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{export_request.data_source}_{timestamp}.json"
                output_path = self.output_dir / filename
            else:
                output_path = Path(export_request.output_path)

            # JSON export options
            options = export_request.options or {}
            orient = options.get(
                "orient", "records"
            )  # 'records', 'index', 'values', 'split', 'table'

            # Convert to JSON
            if orient == "table":
                # Include schema information
                json_data = data.to_json(orient="table", date_format="iso", indent=2)
            else:
                json_data = data.to_json(orient=orient, date_format="iso", indent=2)

            # Add metadata
            if options.get("include_metadata", True):
                export_metadata = {
                    "export_info": {
                        "export_id": export_request.export_id,
                        "data_source": export_request.data_source,
                        "export_date": datetime.now().isoformat(),
                        "total_records": len(data),
                        "columns": data.columns.tolist(),
                        "filters_applied": export_request.filters,
                    },
                    "data": json.loads(json_data),
                }

                with open(output_path, "w") as f:
                    json.dump(export_metadata, f, indent=2, default=str)
            else:
                with open(output_path, "w") as f:
                    f.write(json_data)

            logger.info(f"Data exported to JSON: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise

    async def export_data(
        self,
        data_source: str,
        format_type: str,
        filters: Dict[str, Any] = None,
        columns: List[str] = None,
        output_path: str = None,
        options: Dict[str, Any] = None,
    ) -> str:
        """
        Main export function - exports data in specified format

        Args:
            data_source: Source of data ('races', 'predictions', 'horses', etc.)
            format_type: Export format ('csv', 'excel', 'pdf', 'json')
            filters: Optional filters to apply to data
            columns: Optional list of specific columns to export
            output_path: Optional custom output path
            options: Format-specific options

        Returns:
            Path to exported file
        """

        if format_type not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {format_type}. Supported: {self.supported_formats}"
            )

        try:
            # Create export request
            export_request = ExportRequest(
                export_id=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                format_type=format_type,
                data_source=data_source,
                filters=filters or {},
                columns=columns,
                output_path=output_path,
                options=options or {},
                created_at=datetime.now(),
            )

            logger.info(f"Starting export: {export_request.export_id}")

            # Get data from source
            data = await self.get_data_from_source(data_source, filters, columns)

            if data.empty:
                raise ValueError(
                    f"No data found for source '{data_source}' with specified filters"
                )

            # Export based on format
            if format_type == "csv":
                output_file = await self.export_to_csv(export_request, data)
            elif format_type == "excel":
                output_file = await self.export_to_excel(export_request, data)
            elif format_type == "pdf":
                output_file = await self.export_to_pdf(export_request, data)
            elif format_type == "json":
                output_file = await self.export_to_json(export_request, data)
            else:
                raise ValueError(
                    f"Export handler not implemented for format: {format_type}"
                )

            logger.info(f"Export completed successfully: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error during export: {e}")
            raise

    async def get_available_data_sources(self) -> List[Dict[str, Any]]:
        """Get list of available data sources for export"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            sources = []
            for table in tables:
                table_name = table[0]

                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                sources.append(
                    {
                        "source_name": table_name,
                        "display_name": table_name.replace("_", " ").title(),
                        "columns": columns,
                        "row_count": row_count,
                        "description": f"Export data from {table_name} table",
                    }
                )

            conn.close()

            # Add custom data sources
            custom_sources = [
                {
                    "source_name": "races",
                    "display_name": "Race Data with Track Info",
                    "columns": [
                        "race_id",
                        "race_date",
                        "track_code",
                        "track_name",
                        "race_type",
                        "distance",
                        "prize_money",
                    ],
                    "description": "Complete race information with track details",
                },
                {
                    "source_name": "predictions",
                    "display_name": "Prediction Results",
                    "columns": [
                        "prediction_id",
                        "race_date",
                        "track_code",
                        "predicted_outcome",
                        "actual_outcome",
                        "profit_loss",
                        "roi",
                    ],
                    "description": "Prediction performance data with race context",
                },
            ]

            # Merge custom sources (replace duplicates)
            source_names = {s["source_name"] for s in sources}
            for custom_source in custom_sources:
                if custom_source["source_name"] not in source_names:
                    sources.append(custom_source)
                else:
                    # Update existing source with custom description
                    for i, source in enumerate(sources):
                        if source["source_name"] == custom_source["source_name"]:
                            sources[i].update(custom_source)
                            break

            return sorted(sources, key=lambda x: x["display_name"])

        except Exception as e:
            logger.error(f"Error getting available data sources: {e}")
            return []

    async def cleanup_old_exports(self, days_to_keep: int = 7):
        """Clean up old export files"""

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            for export_file in self.output_dir.glob("*"):
                if (
                    export_file.is_file()
                    and export_file.stat().st_mtime < cutoff_date.timestamp()
                ):
                    export_file.unlink()
                    logger.info(f"Deleted old export: {export_file}")

            logger.info(
                f"Export cleanup completed - removed files older than {days_to_keep} days"
            )

        except Exception as e:
            logger.error(f"Error during export cleanup: {e}")


async def main():
    """Main function for testing the Data Exporter"""

    print("📁 Data Export Utilities V2.03")
    print("=" * 40)

    try:
        # Initialize data exporter
        exporter = DataExporter()

        # Get available data sources
        print("📋 Available Data Sources:")
        sources = await exporter.get_available_data_sources()
        for source in sources[:5]:  # Show first 5
            row_count = source.get('row_count', 'Unknown')
            print(f"   - {source['display_name']}: {row_count} records")

        # Test CSV export
        print("\n📊 Testing CSV Export...")
        csv_file = await exporter.export_data(
            data_source="races",
            format_type="csv",
            filters={"start_date": "2024-01-01"},
            options={"include_index": False},
        )
        print(f"✅ CSV exported: {csv_file}")

        # Test JSON export
        print("\n📄 Testing JSON Export...")
        json_file = await exporter.export_data(
            data_source="predictions",
            format_type="json",
            filters={"start_date": "2024-01-01"},
            options={"orient": "records", "include_metadata": True},
        )
        print(f"✅ JSON exported: {json_file}")

        # Test Excel export (if available)
        if EXCEL_AVAILABLE:
            print("\n📈 Testing Excel Export...")
            excel_file = await exporter.export_data(
                data_source="races",
                format_type="excel",
                filters={"start_date": "2024-01-01"},
                options={"sheet_name": "Race_Data"},
            )
            print(f"✅ Excel exported: {excel_file}")
        else:
            print("\n⚠️  Excel export not available (install openpyxl)")

        # Test PDF export (if available)
        if PDF_AVAILABLE:
            print("\n📋 Testing PDF Export...")
            pdf_file = await exporter.export_data(
                data_source="races",
                format_type="pdf",
                filters={"start_date": "2024-01-01"},
                options={"title": "Race Data Report", "orientation": "landscape"},
            )
            print(f"✅ PDF exported: {pdf_file}")
        else:
            print("\n⚠️  PDF export not available (install reportlab)")

        # Cleanup
        print("\n🧹 Cleaning up old exports...")
        await exporter.cleanup_old_exports(days_to_keep=7)

        print("\n✅ Data Export Utilities testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
