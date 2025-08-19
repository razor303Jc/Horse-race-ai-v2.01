#!/usr/bin/env python3
"""
Interactive Charting and Visualization Engine for Horse Racing AI V2.03
Provides advanced data visualization capabilities with interactive charts
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

# Plotting libraries
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.animation import FuncAnimation

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import bokeh
    from bokeh.plotting import figure, save, output_file
    from bokeh.models import HoverTool, ColumnDataSource
    from bokeh.layouts import column, row
    from bokeh.palettes import Category20

    BOKEH_AVAILABLE = True
except ImportError:
    BOKEH_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChartConfig:
    """Configuration for chart generation"""

    chart_id: str
    chart_type: str  # 'line', 'bar', 'scatter', 'histogram', 'heatmap', 'box', 'pie'
    title: str
    x_column: str
    y_column: Optional[str]
    group_by: Optional[str]
    aggregation: Optional[str]  # 'sum', 'mean', 'count', 'max', 'min'
    filters: Dict[str, Any]
    styling: Dict[str, Any]
    interactive: bool
    export_format: str  # 'png', 'html', 'svg'


class InteractiveChartEngine:
    """
    Interactive Chart Engine providing advanced visualization capabilities
    using Matplotlib, Plotly, and Bokeh
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Interactive Chart Engine"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.output_dir = Path(self.config.get("output_directory", "reports/charts"))

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Available chart libraries
        self.chart_libraries = ["matplotlib"]
        if PLOTLY_AVAILABLE:
            self.chart_libraries.append("plotly")
        if BOKEH_AVAILABLE:
            self.chart_libraries.append("bokeh")

        # Setup plotting styles
        self._setup_plotting_styles()

        logger.info(f"Chart Engine initialized. Libraries: {self.chart_libraries}")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        return {
            "database_path": "data/racing_data_tracking.db",
            "output_directory": "reports/charts",
            "default_width": 1200,
            "default_height": 800,
            "dpi": 300,
            "color_palette": "viridis",
            "style_theme": "seaborn-v0_8",
            "interactive_library": "plotly",  # 'plotly', 'bokeh', 'matplotlib'
        }

    def _setup_plotting_styles(self):
        """Setup plotting styles for different libraries"""
        try:
            # Matplotlib styling
            plt.style.use(self.config.get("style_theme", "seaborn-v0_8"))
            sns.set_palette(self.config.get("color_palette", "viridis"))

            plt.rcParams.update(
                {
                    "figure.figsize": (12, 8),
                    "figure.dpi": self.config.get("dpi", 300),
                    "savefig.dpi": self.config.get("dpi", 300),
                    "font.size": 10,
                    "axes.titlesize": 14,
                    "axes.labelsize": 12,
                }
            )

            # Plotly default template
            if PLOTLY_AVAILABLE:
                pio.templates.default = "plotly_white"

        except Exception as e:
            logger.warning(f"Could not setup plotting styles: {e}")

    async def get_chart_data(
        self, data_source: str, filters: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """Get data for charting from database"""

        try:
            conn = sqlite3.connect(self.db_path)

            # Define queries for different data sources
            queries = {
                "performance_trends": """
                    SELECT pr.*, r.race_date, r.track_code, r.race_type
                    FROM prediction_results pr
                    JOIN races r ON pr.race_id = r.race_id
                    WHERE pr.actual_outcome IS NOT NULL
                    ORDER BY r.race_date
                """,
                "track_analysis": """
                    SELECT r.track_code, t.track_name, 
                           AVG(pr.roi) as avg_roi,
                           AVG(pr.prediction_confidence) as avg_confidence,
                           COUNT(*) as total_races,
                           SUM(CASE WHEN pr.predicted_outcome = pr.actual_outcome THEN 1 ELSE 0 END) as correct_predictions
                    FROM races r
                    JOIN tracks t ON r.track_code = t.track_code
                    LEFT JOIN prediction_results pr ON r.race_id = pr.race_id
                    GROUP BY r.track_code, t.track_name
                    HAVING COUNT(*) >= 5
                """,
                "monthly_summary": """
                    SELECT strftime('%Y-%m', r.race_date) as month,
                           COUNT(*) as total_races,
                           AVG(pr.roi) as avg_roi,
                           SUM(pr.profit_loss) as total_profit,
                           AVG(CASE WHEN pr.predicted_outcome = pr.actual_outcome THEN 1.0 ELSE 0.0 END) as accuracy
                    FROM races r
                    LEFT JOIN prediction_results pr ON r.race_id = pr.race_id
                    WHERE pr.actual_outcome IS NOT NULL
                    GROUP BY strftime('%Y-%m', r.race_date)
                    ORDER BY month
                """,
                "distance_analysis": """
                    SELECT r.distance,
                           COUNT(*) as race_count,
                           AVG(pr.roi) as avg_roi,
                           AVG(pr.prediction_confidence) as avg_confidence
                    FROM races r
                    LEFT JOIN prediction_results pr ON r.race_id = pr.race_id
                    WHERE pr.actual_outcome IS NOT NULL
                    GROUP BY r.distance
                    HAVING COUNT(*) >= 3
                    ORDER BY r.distance
                """,
            }

            if data_source not in queries:
                raise ValueError(f"Unknown data source: {data_source}")

            query = queries[data_source]
            params = []

            # Apply date filters if provided
            if filters and filters.get("start_date"):
                if "WHERE" in query:
                    query = query.replace(
                        "WHERE", f"WHERE r.race_date >= '{filters['start_date']}' AND"
                    )
                else:
                    query += f" WHERE r.race_date >= '{filters['start_date']}'"

            if filters and filters.get("end_date"):
                if "WHERE" in query:
                    query = query.replace(
                        "WHERE", f"WHERE r.race_date <= '{filters['end_date']}' AND"
                    )
                else:
                    query += f" WHERE r.race_date <= '{filters['end_date']}'"

            df = pd.read_sql_query(query, conn)
            conn.close()

            # Convert date columns
            date_columns = ["race_date", "month"]
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            logger.info(f"Retrieved {len(df)} records for charting from {data_source}")
            return df

        except Exception as e:
            logger.error(f"Error getting chart data from {data_source}: {e}")
            return pd.DataFrame()

    async def create_matplotlib_chart(
        self, data: pd.DataFrame, config: ChartConfig
    ) -> str:
        """Create chart using Matplotlib"""

        try:
            fig, ax = plt.subplots(
                figsize=(
                    self.config.get("default_width", 1200) / 100,
                    self.config.get("default_height", 800) / 100,
                )
            )

            # Apply styling
            styling = config.styling or {}
            color = styling.get("color", None)
            alpha = styling.get("alpha", 0.7)

            if config.chart_type == "line":
                if config.group_by:
                    groups = data.groupby(config.group_by)
                    for name, group in groups:
                        ax.plot(
                            group[config.x_column],
                            group[config.y_column],
                            label=name,
                            marker="o",
                            linewidth=2,
                        )
                    ax.legend()
                else:
                    ax.plot(
                        data[config.x_column],
                        data[config.y_column],
                        marker="o",
                        linewidth=2,
                        color=color,
                    )

            elif config.chart_type == "bar":
                if config.aggregation:
                    if config.group_by:
                        plot_data = data.groupby(config.x_column)[config.y_column].agg(
                            config.aggregation
                        )
                    else:
                        plot_data = data.groupby(config.x_column)[config.y_column].agg(
                            config.aggregation
                        )
                    plot_data.plot(kind="bar", ax=ax, color=color, alpha=alpha)
                else:
                    ax.bar(
                        data[config.x_column],
                        data[config.y_column],
                        color=color,
                        alpha=alpha,
                    )

            elif config.chart_type == "scatter":
                scatter = ax.scatter(
                    data[config.x_column],
                    data[config.y_column],
                    c=data[config.group_by] if config.group_by else color,
                    alpha=alpha,
                    s=50,
                )
                if config.group_by:
                    plt.colorbar(scatter, ax=ax, label=config.group_by)

            elif config.chart_type == "histogram":
                ax.hist(
                    data[config.x_column],
                    bins=30,
                    color=color,
                    alpha=alpha,
                    edgecolor="black",
                )

            elif config.chart_type == "box":
                if config.group_by:
                    data.boxplot(column=config.y_column, by=config.group_by, ax=ax)
                else:
                    ax.boxplot(data[config.y_column])

            # Set labels and title
            ax.set_title(config.title, fontsize=16, fontweight="bold")
            ax.set_xlabel(config.x_column.replace("_", " ").title(), fontsize=12)
            if config.y_column:
                ax.set_ylabel(config.y_column.replace("_", " ").title(), fontsize=12)

            # Add grid
            ax.grid(True, alpha=0.3)

            # Tight layout
            plt.tight_layout()

            # Save chart
            output_path = self.output_dir / f"{config.chart_id}.{config.export_format}"
            plt.savefig(
                output_path, dpi=self.config.get("dpi", 300), bbox_inches="tight"
            )
            plt.close()

            logger.info(f"Matplotlib chart created: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating matplotlib chart: {e}")
            raise

    async def create_plotly_chart(self, data: pd.DataFrame, config: ChartConfig) -> str:
        """Create interactive chart using Plotly"""

        if not PLOTLY_AVAILABLE:
            raise RuntimeError(
                "Plotly not available. Install plotly: pip install plotly"
            )

        try:
            styling = config.styling or {}

            if config.chart_type == "line":
                if config.group_by:
                    fig = px.line(
                        data,
                        x=config.x_column,
                        y=config.y_column,
                        color=config.group_by,
                        title=config.title,
                        markers=True,
                        line_shape="linear",
                    )
                else:
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=data[config.x_column],
                            y=data[config.y_column],
                            mode="lines+markers",
                            name=config.y_column,
                            line=dict(width=3),
                        )
                    )

            elif config.chart_type == "bar":
                if config.aggregation and config.group_by:
                    agg_data = (
                        data.groupby(config.x_column)[config.y_column]
                        .agg(config.aggregation)
                        .reset_index()
                    )
                    fig = px.bar(
                        agg_data,
                        x=config.x_column,
                        y=config.y_column,
                        title=config.title,
                    )
                else:
                    fig = px.bar(
                        data, x=config.x_column, y=config.y_column, title=config.title
                    )

            elif config.chart_type == "scatter":
                fig = px.scatter(
                    data,
                    x=config.x_column,
                    y=config.y_column,
                    color=config.group_by if config.group_by else None,
                    title=config.title,
                    hover_data=data.columns.tolist()[:5],
                )

            elif config.chart_type == "histogram":
                fig = px.histogram(
                    data,
                    x=config.x_column,
                    title=config.title,
                    color=config.group_by if config.group_by else None,
                )

            elif config.chart_type == "box":
                if config.group_by:
                    fig = px.box(
                        data, x=config.group_by, y=config.y_column, title=config.title
                    )
                else:
                    fig = px.box(data, y=config.y_column, title=config.title)

            elif config.chart_type == "pie":
                if config.aggregation:
                    pie_data = (
                        data.groupby(config.x_column)[config.y_column]
                        .agg(config.aggregation)
                        .reset_index()
                    )
                    fig = px.pie(
                        pie_data,
                        values=config.y_column,
                        names=config.x_column,
                        title=config.title,
                    )
                else:
                    fig = px.pie(
                        data,
                        values=config.y_column,
                        names=config.x_column,
                        title=config.title,
                    )

            elif config.chart_type == "heatmap":
                # Create correlation heatmap
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                corr_matrix = data[numeric_cols].corr()
                fig = px.imshow(corr_matrix, title=config.title, aspect="auto")

            # Update layout
            fig.update_layout(
                width=self.config.get("default_width", 1200),
                height=self.config.get("default_height", 800),
                title_font_size=16,
                showlegend=True,
            )

            # Save chart
            if config.export_format == "html":
                output_path = self.output_dir / f"{config.chart_id}.html"
                fig.write_html(str(output_path))
            else:
                output_path = (
                    self.output_dir / f"{config.chart_id}.{config.export_format}"
                )
                fig.write_image(
                    str(output_path),
                    width=self.config.get("default_width", 1200),
                    height=self.config.get("default_height", 800),
                )

            logger.info(f"Plotly chart created: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating plotly chart: {e}")
            raise

    async def create_dashboard(
        self, charts: List[ChartConfig], title: str = "Analytics Dashboard"
    ) -> str:
        """Create interactive dashboard with multiple charts"""

        if not PLOTLY_AVAILABLE:
            raise RuntimeError(
                "Dashboard requires Plotly. Install plotly: pip install plotly"
            )

        try:
            # Create subplots
            rows = (len(charts) + 1) // 2  # 2 charts per row
            fig = make_subplots(
                rows=rows,
                cols=2,
                subplot_titles=[chart.title for chart in charts],
                specs=[
                    [{"secondary_y": False}, {"secondary_y": False}]
                    for _ in range(rows)
                ],
            )

            for i, chart_config in enumerate(charts):
                row = (i // 2) + 1
                col = (i % 2) + 1

                # Get data for this chart
                data = await self.get_chart_data(
                    chart_config.chart_type, chart_config.filters
                )

                if data.empty:
                    continue

                # Add trace based on chart type
                if chart_config.chart_type == "line":
                    fig.add_trace(
                        go.Scatter(
                            x=data[chart_config.x_column],
                            y=data[chart_config.y_column],
                            mode="lines+markers",
                            name=chart_config.title,
                        ),
                        row=row,
                        col=col,
                    )

                elif chart_config.chart_type == "bar":
                    fig.add_trace(
                        go.Bar(
                            x=data[chart_config.x_column],
                            y=data[chart_config.y_column],
                            name=chart_config.title,
                        ),
                        row=row,
                        col=col,
                    )

                elif chart_config.chart_type == "scatter":
                    fig.add_trace(
                        go.Scatter(
                            x=data[chart_config.x_column],
                            y=data[chart_config.y_column],
                            mode="markers",
                            name=chart_config.title,
                        ),
                        row=row,
                        col=col,
                    )

            # Update layout
            fig.update_layout(
                title=title, height=600 * rows, showlegend=True, title_font_size=20
            )

            # Save dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"dashboard_{timestamp}.html"
            fig.write_html(str(output_path))

            logger.info(f"Dashboard created: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise

    async def generate_standard_charts(self) -> List[str]:
        """Generate a set of standard analytics charts"""

        chart_paths = []

        try:
            # Chart 1: Monthly Performance Trend
            monthly_data = await self.get_chart_data("monthly_summary")
            if not monthly_data.empty:
                config = ChartConfig(
                    chart_id=f"monthly_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    chart_type="line",
                    title="Monthly Performance Trends",
                    x_column="month",
                    y_column="avg_roi",
                    group_by=None,
                    aggregation=None,
                    filters={},
                    styling={"color": "blue"},
                    interactive=True,
                    export_format="html" if PLOTLY_AVAILABLE else "png",
                )

                if PLOTLY_AVAILABLE and config.interactive:
                    chart_path = await self.create_plotly_chart(monthly_data, config)
                else:
                    chart_path = await self.create_matplotlib_chart(
                        monthly_data, config
                    )
                chart_paths.append(chart_path)

            # Chart 2: Track Performance Analysis
            track_data = await self.get_chart_data("track_analysis")
            if not track_data.empty:
                config = ChartConfig(
                    chart_id=f"track_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    chart_type="bar",
                    title="Track Performance Analysis",
                    x_column="track_code",
                    y_column="avg_roi",
                    group_by=None,
                    aggregation=None,
                    filters={},
                    styling={"color": "green"},
                    interactive=True,
                    export_format="html" if PLOTLY_AVAILABLE else "png",
                )

                if PLOTLY_AVAILABLE and config.interactive:
                    chart_path = await self.create_plotly_chart(track_data, config)
                else:
                    chart_path = await self.create_matplotlib_chart(track_data, config)
                chart_paths.append(chart_path)

            # Chart 3: Distance vs Performance Scatter
            distance_data = await self.get_chart_data("distance_analysis")
            if not distance_data.empty:
                config = ChartConfig(
                    chart_id=f"distance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    chart_type="scatter",
                    title="Distance vs ROI Analysis",
                    x_column="distance",
                    y_column="avg_roi",
                    group_by=None,
                    aggregation=None,
                    filters={},
                    styling={"color": "red"},
                    interactive=True,
                    export_format="html" if PLOTLY_AVAILABLE else "png",
                )

                if PLOTLY_AVAILABLE and config.interactive:
                    chart_path = await self.create_plotly_chart(distance_data, config)
                else:
                    chart_path = await self.create_matplotlib_chart(
                        distance_data, config
                    )
                chart_paths.append(chart_path)

            # Chart 4: Confidence Distribution
            performance_data = await self.get_chart_data("performance_trends")
            if not performance_data.empty:
                config = ChartConfig(
                    chart_id=f"confidence_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    chart_type="histogram",
                    title="Prediction Confidence Distribution",
                    x_column="prediction_confidence",
                    y_column=None,
                    group_by=None,
                    aggregation=None,
                    filters={},
                    styling={"color": "purple"},
                    interactive=True,
                    export_format="html" if PLOTLY_AVAILABLE else "png",
                )

                if PLOTLY_AVAILABLE and config.interactive:
                    chart_path = await self.create_plotly_chart(
                        performance_data, config
                    )
                else:
                    chart_path = await self.create_matplotlib_chart(
                        performance_data, config
                    )
                chart_paths.append(chart_path)

            logger.info(f"Generated {len(chart_paths)} standard charts")
            return chart_paths

        except Exception as e:
            logger.error(f"Error generating standard charts: {e}")
            return chart_paths

    async def create_custom_chart(
        self,
        data_source: str,
        chart_type: str,
        x_column: str,
        y_column: str = None,
        title: str = None,
        group_by: str = None,
        filters: Dict[str, Any] = None,
        styling: Dict[str, Any] = None,
        interactive: bool = True,
    ) -> str:
        """Create a custom chart with specified parameters"""

        try:
            # Get data
            data = await self.get_chart_data(data_source, filters)

            if data.empty:
                raise ValueError(f"No data available for {data_source}")

            # Create chart configuration
            config = ChartConfig(
                chart_id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                chart_type=chart_type,
                title=title or f"{chart_type.title()} Chart",
                x_column=x_column,
                y_column=y_column,
                group_by=group_by,
                aggregation=None,
                filters=filters or {},
                styling=styling or {},
                interactive=interactive,
                export_format="html" if interactive and PLOTLY_AVAILABLE else "png",
            )

            # Create chart
            if interactive and PLOTLY_AVAILABLE:
                chart_path = await self.create_plotly_chart(data, config)
            else:
                chart_path = await self.create_matplotlib_chart(data, config)

            logger.info(f"Custom chart created: {chart_path}")
            return chart_path

        except Exception as e:
            logger.error(f"Error creating custom chart: {e}")
            raise

    async def cleanup_old_charts(self, days_to_keep: int = 14):
        """Clean up old chart files"""

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            for chart_file in self.output_dir.glob("*"):
                if (
                    chart_file.is_file()
                    and chart_file.stat().st_mtime < cutoff_date.timestamp()
                ):
                    chart_file.unlink()
                    logger.info(f"Deleted old chart: {chart_file}")

            logger.info(
                f"Chart cleanup completed - removed files older than {days_to_keep} days"
            )

        except Exception as e:
            logger.error(f"Error during chart cleanup: {e}")


async def main():
    """Main function for testing the Interactive Chart Engine"""

    print("📊 Interactive Chart Engine V2.03")
    print("=" * 45)

    try:
        # Initialize chart engine
        engine = InteractiveChartEngine()

        # Generate standard charts
        print("📈 Generating Standard Charts...")
        chart_paths = await engine.generate_standard_charts()

        for i, chart_path in enumerate(chart_paths, 1):
            print(f"   {i}. Chart created: {Path(chart_path).name}")

        # Test custom chart
        print("\n🎨 Creating Custom Chart...")
        custom_chart = await engine.create_custom_chart(
            data_source="monthly_summary",
            chart_type="line",
            x_column="month",
            y_column="accuracy",
            title="Monthly Accuracy Trends",
            interactive=True,
            styling={"color": "orange"},
        )
        print(f"   Custom chart: {Path(custom_chart).name}")

        # Test interactive dashboard (if Plotly available)
        if PLOTLY_AVAILABLE:
            print("\n🖥️  Creating Interactive Dashboard...")

            chart_configs = [
                ChartConfig(
                    chart_id="dash_chart_1",
                    chart_type="monthly_summary",
                    title="Monthly ROI",
                    x_column="month",
                    y_column="avg_roi",
                    group_by=None,
                    aggregation=None,
                    filters={},
                    styling={},
                    interactive=True,
                    export_format="html",
                ),
                ChartConfig(
                    chart_id="dash_chart_2",
                    chart_type="track_analysis",
                    title="Track Performance",
                    x_column="track_code",
                    y_column="avg_roi",
                    group_by=None,
                    aggregation=None,
                    filters={},
                    styling={},
                    interactive=True,
                    export_format="html",
                ),
            ]

            dashboard_path = await engine.create_dashboard(
                chart_configs, "Racing Analytics Dashboard"
            )
            print(f"   Dashboard: {Path(dashboard_path).name}")
        else:
            print("\n⚠️  Interactive dashboard requires Plotly (pip install plotly)")

        # Cleanup
        print("\n🧹 Cleaning up old charts...")
        await engine.cleanup_old_charts(days_to_keep=14)

        print(f"\n✅ Chart Engine testing completed!")
        print(f"   - Total charts generated: {len(chart_paths) + 1}")
        print(f"   - Available libraries: {engine.chart_libraries}")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
