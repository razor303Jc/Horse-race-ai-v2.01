#!/usr/bin/env python3
"""
Advanced Analytics Engine for Horse Racing AI V2.03
Provides comprehensive statistical analysis, custom reporting, and data visualization
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import sqlite3
import asyncio
import logging
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalyticsReport:
    """Data class for analytics reports"""

    report_id: str
    title: str
    description: str
    data: Dict[str, Any]
    charts: List[Dict[str, Any]]
    created_at: datetime
    report_type: str
    metadata: Dict[str, Any]


@dataclass
class StatisticalSummary:
    """Data class for statistical summaries"""

    metric_name: str
    value: float
    confidence_interval: Tuple[float, float]
    p_value: Optional[float]
    significance: str
    sample_size: int


class AdvancedAnalyticsEngine:
    """
    Advanced Analytics Engine providing comprehensive statistical analysis,
    custom reporting, and data visualization capabilities
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Advanced Analytics Engine"""
        self.config = self._load_config(config_path)
        self.db_path = self.config.get("database_path", "data/racing_data_tracking.db")
        self.output_dir = Path(self.config.get("output_directory", "reports/analytics"))
        self.charts_dir = Path(self.config.get("charts_directory", "reports/charts"))

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        # Initialize plotting style
        self._setup_plotting_style()

        # Cache for frequently accessed data
        self.data_cache = {}

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        # Default configuration
        return {
            "database_path": "data/racing_data_tracking.db",
            "output_directory": "reports/analytics",
            "charts_directory": "reports/charts",
            "confidence_level": 0.95,
            "sample_size_threshold": 30,
            "chart_dpi": 300,
            "chart_style": "seaborn-v0_8",
            "color_palette": "viridis",
        }

    def _setup_plotting_style(self):
        """Setup matplotlib and seaborn plotting style"""
        try:
            plt.style.use(self.config.get("chart_style", "seaborn-v0_8"))
        except:
            plt.style.use("default")

        sns.set_palette(self.config.get("color_palette", "viridis"))

        # Set default figure parameters
        plt.rcParams.update(
            {
                "figure.figsize": (12, 8),
                "figure.dpi": self.config.get("chart_dpi", 300),
                "savefig.dpi": self.config.get("chart_dpi", 300),
                "font.size": 10,
                "axes.titlesize": 14,
                "axes.labelsize": 12,
                "xtick.labelsize": 10,
                "ytick.labelsize": 10,
                "legend.fontsize": 10,
            }
        )

    async def get_race_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        track_code: Optional[str] = None,
    ) -> pd.DataFrame:
        """Get race data with optional filtering"""

        cache_key = f"race_data_{start_date}_{end_date}_{track_code}"
        if cache_key in self.data_cache:
            logger.info(f"Using cached data for {cache_key}")
            return self.data_cache[cache_key]

        try:
            conn = sqlite3.connect(self.db_path)

            # Base query
            query = """
            SELECT r.*, t.track_name, t.surface_type, t.distance_unit,
                   pr.prediction_confidence, pr.predicted_outcome, pr.actual_outcome,
                   pr.profit_loss, pr.roi, pr.stake
            FROM races r
            LEFT JOIN tracks t ON r.track_code = t.track_code
            LEFT JOIN prediction_results pr ON r.race_id = pr.race_id
            WHERE 1=1
            """

            params = []

            # Add date filtering
            if start_date:
                query += " AND r.race_date >= ?"
                params.append(start_date.strftime("%Y-%m-%d"))

            if end_date:
                query += " AND r.race_date <= ?"
                params.append(end_date.strftime("%Y-%m-%d"))

            # Add track filtering
            if track_code:
                query += " AND r.track_code = ?"
                params.append(track_code)

            query += " ORDER BY r.race_date DESC, r.race_time DESC"

            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            # Convert date columns
            if "race_date" in df.columns:
                df["race_date"] = pd.to_datetime(df["race_date"])

            # Cache the result
            self.data_cache[cache_key] = df

            logger.info(f"Loaded {len(df)} race records")
            return df

        except Exception as e:
            logger.error(f"Error loading race data: {e}")
            return pd.DataFrame()

    async def get_prediction_performance_data(self) -> pd.DataFrame:
        """Get prediction performance data for analysis"""

        if "prediction_performance" in self.data_cache:
            return self.data_cache["prediction_performance"]

        try:
            conn = sqlite3.connect(self.db_path)

            query = """
            SELECT pr.*, r.race_date, r.track_code, r.race_type, r.distance,
                   r.prize_money, r.field_size, t.track_name, t.surface_type
            FROM prediction_results pr
            JOIN races r ON pr.race_id = r.race_id
            LEFT JOIN tracks t ON r.track_code = t.track_code
            WHERE pr.actual_outcome IS NOT NULL
            ORDER BY r.race_date DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            # Convert date columns
            if "race_date" in df.columns:
                df["race_date"] = pd.to_datetime(df["race_date"])

            # Calculate performance metrics
            df["prediction_correct"] = (
                df["predicted_outcome"] == df["actual_outcome"]
            ).astype(int)
            df["cumulative_profit"] = df["profit_loss"].cumsum()
            df["cumulative_roi"] = df["cumulative_profit"] / df["stake"].cumsum() * 100

            # Cache the result
            self.data_cache["prediction_performance"] = df

            logger.info(f"Loaded {len(df)} prediction performance records")
            return df

        except Exception as e:
            logger.error(f"Error loading prediction performance data: {e}")
            return pd.DataFrame()

    async def calculate_statistical_summary(
        self, data: pd.DataFrame, metric_column: str, group_by: Optional[str] = None
    ) -> List[StatisticalSummary]:
        """Calculate comprehensive statistical summary for a metric"""

        summaries = []
        confidence_level = self.config.get("confidence_level", 0.95)
        alpha = 1 - confidence_level

        try:
            if group_by:
                groups = data.groupby(group_by)

                for group_name, group_data in groups:
                    values = group_data[metric_column].dropna()

                    if len(values) < self.config.get("sample_size_threshold", 30):
                        continue

                    # Calculate statistics
                    mean_val = values.mean()
                    std_val = values.std()
                    n = len(values)

                    # Confidence interval for mean
                    margin_error = stats.t.ppf(1 - alpha / 2, n - 1) * (
                        std_val / np.sqrt(n)
                    )
                    ci_lower = mean_val - margin_error
                    ci_upper = mean_val + margin_error

                    # One-sample t-test (testing if mean is significantly different from 0)
                    t_stat, p_value = stats.ttest_1samp(values, 0)

                    # Determine significance
                    if p_value < 0.001:
                        significance = "Highly Significant (p < 0.001)"
                    elif p_value < 0.01:
                        significance = "Very Significant (p < 0.01)"
                    elif p_value < 0.05:
                        significance = "Significant (p < 0.05)"
                    else:
                        significance = "Not Significant (p >= 0.05)"

                    summaries.append(
                        StatisticalSummary(
                            metric_name=f"{metric_column}_{group_name}",
                            value=mean_val,
                            confidence_interval=(ci_lower, ci_upper),
                            p_value=p_value,
                            significance=significance,
                            sample_size=n,
                        )
                    )
            else:
                values = data[metric_column].dropna()

                if len(values) >= self.config.get("sample_size_threshold", 30):
                    # Calculate statistics
                    mean_val = values.mean()
                    std_val = values.std()
                    n = len(values)

                    # Confidence interval for mean
                    margin_error = stats.t.ppf(1 - alpha / 2, n - 1) * (
                        std_val / np.sqrt(n)
                    )
                    ci_lower = mean_val - margin_error
                    ci_upper = mean_val + margin_error

                    # One-sample t-test
                    t_stat, p_value = stats.ttest_1samp(values, 0)

                    # Determine significance
                    if p_value < 0.001:
                        significance = "Highly Significant (p < 0.001)"
                    elif p_value < 0.01:
                        significance = "Very Significant (p < 0.01)"
                    elif p_value < 0.05:
                        significance = "Significant (p < 0.05)"
                    else:
                        significance = "Not Significant (p >= 0.05)"

                    summaries.append(
                        StatisticalSummary(
                            metric_name=metric_column,
                            value=mean_val,
                            confidence_interval=(ci_lower, ci_upper),
                            p_value=p_value,
                            significance=significance,
                            sample_size=n,
                        )
                    )

        except Exception as e:
            logger.error(f"Error calculating statistical summary: {e}")

        return summaries

    async def generate_performance_analytics_report(self) -> AnalyticsReport:
        """Generate comprehensive performance analytics report"""

        logger.info("Generating performance analytics report...")

        try:
            # Get prediction performance data
            df = await self.get_prediction_performance_data()

            if df.empty:
                logger.warning("No prediction performance data available")
                return self._create_empty_report(
                    "Performance Analytics", "No data available"
                )

            # Calculate overall performance metrics
            total_predictions = len(df)
            correct_predictions = df["prediction_correct"].sum()
            accuracy = (
                correct_predictions / total_predictions if total_predictions > 0 else 0
            )

            total_profit = df["profit_loss"].sum()
            total_stake = df["stake"].sum()
            overall_roi = (total_profit / total_stake * 100) if total_stake > 0 else 0

            # Calculate statistical summaries
            roi_summary = await self.calculate_statistical_summary(df, "roi")
            profit_summary = await self.calculate_statistical_summary(df, "profit_loss")
            confidence_summary = await self.calculate_statistical_summary(
                df, "prediction_confidence"
            )

            # Performance by track
            track_performance = (
                df.groupby("track_code")
                .agg(
                    {
                        "prediction_correct": "mean",
                        "profit_loss": "sum",
                        "roi": "mean",
                        "stake": "sum",
                    }
                )
                .round(4)
            )

            # Performance by race type
            race_type_performance = (
                df.groupby("race_type")
                .agg(
                    {
                        "prediction_correct": "mean",
                        "profit_loss": "sum",
                        "roi": "mean",
                        "stake": "sum",
                    }
                )
                .round(4)
            )

            # Performance over time (monthly)
            df["month"] = df["race_date"].dt.to_period("M")
            monthly_performance = (
                df.groupby("month")
                .agg(
                    {
                        "prediction_correct": "mean",
                        "profit_loss": "sum",
                        "roi": "mean",
                        "stake": "sum",
                    }
                )
                .round(4)
            )

            # Create charts
            charts = []

            # Chart 1: Accuracy over time
            chart_path = await self._create_accuracy_chart(df)
            if chart_path:
                charts.append(
                    {
                        "title": "Prediction Accuracy Over Time",
                        "type": "line_chart",
                        "path": str(chart_path),
                        "description": "Monthly prediction accuracy trends",
                    }
                )

            # Chart 2: ROI distribution
            chart_path = await self._create_roi_distribution_chart(df)
            if chart_path:
                charts.append(
                    {
                        "title": "ROI Distribution",
                        "type": "histogram",
                        "path": str(chart_path),
                        "description": "Distribution of Return on Investment",
                    }
                )

            # Chart 3: Performance by track
            chart_path = await self._create_track_performance_chart(track_performance)
            if chart_path:
                charts.append(
                    {
                        "title": "Performance by Track",
                        "type": "bar_chart",
                        "path": str(chart_path),
                        "description": "Accuracy and ROI by racing track",
                    }
                )

            # Chart 4: Cumulative profit
            chart_path = await self._create_cumulative_profit_chart(df)
            if chart_path:
                charts.append(
                    {
                        "title": "Cumulative Profit Over Time",
                        "type": "line_chart",
                        "path": str(chart_path),
                        "description": "Cumulative profit/loss progression",
                    }
                )

            # Compile report data
            report_data = {
                "summary_metrics": {
                    "total_predictions": total_predictions,
                    "correct_predictions": correct_predictions,
                    "accuracy_percentage": round(accuracy * 100, 2),
                    "total_profit": round(total_profit, 2),
                    "total_stake": round(total_stake, 2),
                    "overall_roi_percentage": round(overall_roi, 2),
                },
                "statistical_summaries": {
                    "roi": [asdict(s) for s in roi_summary],
                    "profit_loss": [asdict(s) for s in profit_summary],
                    "prediction_confidence": [asdict(s) for s in confidence_summary],
                },
                "performance_by_track": track_performance.to_dict("index"),
                "performance_by_race_type": race_type_performance.to_dict("index"),
                "monthly_performance": monthly_performance.to_dict("index"),
                "data_period": {
                    "start_date": (
                        df["race_date"].min().isoformat() if not df.empty else None
                    ),
                    "end_date": (
                        df["race_date"].max().isoformat() if not df.empty else None
                    ),
                },
            }

            # Create analytics report
            report = AnalyticsReport(
                report_id=f"performance_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="Performance Analytics Report",
                description="Comprehensive analysis of prediction performance and profitability",
                data=report_data,
                charts=charts,
                created_at=datetime.now(),
                report_type="performance_analytics",
                metadata={
                    "total_records": len(df),
                    "analysis_period_days": (
                        (df["race_date"].max() - df["race_date"].min()).days
                        if not df.empty
                        else 0
                    ),
                    "confidence_level": self.config.get("confidence_level", 0.95),
                },
            )

            logger.info(
                f"Performance analytics report generated successfully: {report.report_id}"
            )
            return report

        except Exception as e:
            logger.error(f"Error generating performance analytics report: {e}")
            return self._create_empty_report(
                "Performance Analytics", f"Error: {str(e)}"
            )

    async def _create_accuracy_chart(self, df: pd.DataFrame) -> Optional[Path]:
        """Create accuracy over time chart"""

        try:
            # Calculate monthly accuracy
            df["month"] = df["race_date"].dt.to_period("M")
            monthly_accuracy = df.groupby("month")["prediction_correct"].mean() * 100

            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            monthly_accuracy.plot(
                kind="line", ax=ax, marker="o", linewidth=2, markersize=6
            )

            ax.set_title(
                "Prediction Accuracy Over Time", fontsize=16, fontweight="bold"
            )
            ax.set_xlabel("Month", fontsize=12)
            ax.set_ylabel("Accuracy (%)", fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 100)

            # Add trend line
            x_numeric = range(len(monthly_accuracy))
            z = np.polyfit(x_numeric, monthly_accuracy.values, 1)
            p = np.poly1d(z)
            ax.plot(
                monthly_accuracy.index,
                p(x_numeric),
                "--",
                alpha=0.8,
                color="red",
                linewidth=2,
                label="Trend",
            )
            ax.legend()

            plt.tight_layout()

            # Save chart
            chart_path = (
                self.charts_dir
                / f"accuracy_over_time_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(
                chart_path, dpi=self.config.get("chart_dpi", 300), bbox_inches="tight"
            )
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating accuracy chart: {e}")
            return None

    async def _create_roi_distribution_chart(self, df: pd.DataFrame) -> Optional[Path]:
        """Create ROI distribution chart"""

        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

            # Histogram
            df["roi"].hist(bins=50, ax=ax1, alpha=0.7, edgecolor="black")
            ax1.axvline(
                df["roi"].mean(),
                color="red",
                linestyle="--",
                linewidth=2,
                label=f'Mean: {df["roi"].mean():.2f}%',
            )
            ax1.axvline(
                df["roi"].median(),
                color="green",
                linestyle="--",
                linewidth=2,
                label=f'Median: {df["roi"].median():.2f}%',
            )
            ax1.set_title("ROI Distribution", fontsize=14, fontweight="bold")
            ax1.set_xlabel("ROI (%)")
            ax1.set_ylabel("Frequency")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Box plot
            df.boxplot(column="roi", ax=ax2)
            ax2.set_title("ROI Box Plot", fontsize=14, fontweight="bold")
            ax2.set_ylabel("ROI (%)")
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save chart
            chart_path = (
                self.charts_dir
                / f"roi_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(
                chart_path, dpi=self.config.get("chart_dpi", 300), bbox_inches="tight"
            )
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating ROI distribution chart: {e}")
            return None

    async def _create_track_performance_chart(
        self, track_performance: pd.DataFrame
    ) -> Optional[Path]:
        """Create track performance chart"""

        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

            # Sort by accuracy
            track_performance_sorted = track_performance.sort_values(
                "prediction_correct", ascending=True
            )

            # Accuracy by track
            track_performance_sorted["prediction_correct"].plot(
                kind="barh", ax=ax1, color="skyblue"
            )
            ax1.set_title(
                "Prediction Accuracy by Track", fontsize=14, fontweight="bold"
            )
            ax1.set_xlabel("Accuracy")
            ax1.set_ylabel("Track Code")
            ax1.grid(True, alpha=0.3, axis="x")

            # Add percentage labels
            for i, v in enumerate(track_performance_sorted["prediction_correct"]):
                ax1.text(v + 0.01, i, f"{v:.1%}", va="center")

            # ROI by track
            track_performance_roi_sorted = track_performance.sort_values(
                "roi", ascending=True
            )
            colors = [
                "red" if x < 0 else "green" for x in track_performance_roi_sorted["roi"]
            ]
            track_performance_roi_sorted["roi"].plot(kind="barh", ax=ax2, color=colors)
            ax2.set_title("Average ROI by Track", fontsize=14, fontweight="bold")
            ax2.set_xlabel("ROI (%)")
            ax2.set_ylabel("Track Code")
            ax2.axvline(0, color="black", linestyle="-", alpha=0.5)
            ax2.grid(True, alpha=0.3, axis="x")

            # Add percentage labels
            for i, v in enumerate(track_performance_roi_sorted["roi"]):
                ax2.text(v + (1 if v >= 0 else -1), i, f"{v:.1f}%", va="center")

            plt.tight_layout()

            # Save chart
            chart_path = (
                self.charts_dir
                / f"track_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(
                chart_path, dpi=self.config.get("chart_dpi", 300), bbox_inches="tight"
            )
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating track performance chart: {e}")
            return None

    async def _create_cumulative_profit_chart(self, df: pd.DataFrame) -> Optional[Path]:
        """Create cumulative profit chart"""

        try:
            # Sort by date
            df_sorted = df.sort_values("race_date")

            fig, ax = plt.subplots(figsize=(14, 8))

            # Plot cumulative profit
            ax.plot(
                df_sorted["race_date"],
                df_sorted["cumulative_profit"],
                linewidth=2,
                color="blue",
                label="Cumulative Profit",
            )
            ax.axhline(0, color="black", linestyle="-", alpha=0.5)

            # Color the area above/below zero
            ax.fill_between(
                df_sorted["race_date"],
                df_sorted["cumulative_profit"],
                0,
                where=(df_sorted["cumulative_profit"] >= 0),
                alpha=0.3,
                color="green",
                label="Profit Zone",
            )
            ax.fill_between(
                df_sorted["race_date"],
                df_sorted["cumulative_profit"],
                0,
                where=(df_sorted["cumulative_profit"] < 0),
                alpha=0.3,
                color="red",
                label="Loss Zone",
            )

            ax.set_title("Cumulative Profit Over Time", fontsize=16, fontweight="bold")
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Cumulative Profit", fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Format x-axis dates
            fig.autofmt_xdate()

            # Add final profit annotation
            final_profit = df_sorted["cumulative_profit"].iloc[-1]
            ax.annotate(
                f"Final Profit: {final_profit:.2f}",
                xy=(df_sorted["race_date"].iloc[-1], final_profit),
                xytext=(10, 10),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

            plt.tight_layout()

            # Save chart
            chart_path = (
                self.charts_dir
                / f"cumulative_profit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(
                chart_path, dpi=self.config.get("chart_dpi", 300), bbox_inches="tight"
            )
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error creating cumulative profit chart: {e}")
            return None

    def _create_empty_report(self, title: str, description: str) -> AnalyticsReport:
        """Create an empty report for error cases"""
        return AnalyticsReport(
            report_id=f"empty_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            data={},
            charts=[],
            created_at=datetime.now(),
            report_type="empty",
            metadata={},
        )

    async def export_report_to_json(
        self, report: AnalyticsReport, filepath: Optional[str] = None
    ) -> str:
        """Export analytics report to JSON format"""

        if not filepath:
            filepath = self.output_dir / f"{report.report_id}.json"

        try:
            # Convert report to dictionary with serializable types
            report_dict = asdict(report)
            report_dict["created_at"] = report.created_at.isoformat()

            # Handle datetime objects in data
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(v) for v in obj]
                return obj

            report_dict = convert_datetime(report_dict)

            with open(filepath, "w") as f:
                json.dump(report_dict, f, indent=2, default=str)

            logger.info(f"Report exported to JSON: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting report to JSON: {e}")
            raise

    async def generate_custom_report(
        self, report_config: Dict[str, Any]
    ) -> AnalyticsReport:
        """Generate custom analytics report based on configuration"""

        logger.info(
            f"Generating custom report: {report_config.get('title', 'Untitled')}"
        )

        try:
            # Extract configuration
            title = report_config.get("title", "Custom Analytics Report")
            description = report_config.get("description", "Custom analytics analysis")
            metrics = report_config.get("metrics", [])
            filters = report_config.get("filters", {})
            chart_types = report_config.get("charts", [])

            # Get filtered data
            df = await self.get_race_data(
                start_date=filters.get("start_date"),
                end_date=filters.get("end_date"),
                track_code=filters.get("track_code"),
            )

            if df.empty:
                return self._create_empty_report(
                    title, "No data available for specified filters"
                )

            # Calculate custom metrics
            report_data = {}
            charts = []

            for metric in metrics:
                metric_name = metric.get("name")
                metric_column = metric.get("column")
                group_by = metric.get("group_by")

                if metric_column in df.columns:
                    summary = await self.calculate_statistical_summary(
                        df, metric_column, group_by
                    )
                    report_data[metric_name] = [asdict(s) for s in summary]

            # Generate custom charts based on configuration
            for chart_config in chart_types:
                chart_path = await self._generate_custom_chart(df, chart_config)
                if chart_path:
                    charts.append(
                        {
                            "title": chart_config.get("title", "Custom Chart"),
                            "type": chart_config.get("type", "unknown"),
                            "path": str(chart_path),
                            "description": chart_config.get(
                                "description", "Custom generated chart"
                            ),
                        }
                    )

            # Create custom report
            report = AnalyticsReport(
                report_id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=title,
                description=description,
                data=report_data,
                charts=charts,
                created_at=datetime.now(),
                report_type="custom",
                metadata={
                    "filters_applied": filters,
                    "metrics_analyzed": len(metrics),
                    "charts_generated": len(charts),
                    "total_records": len(df),
                },
            )

            logger.info(f"Custom report generated successfully: {report.report_id}")
            return report

        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            return self._create_empty_report(title, f"Error: {str(e)}")

    async def _generate_custom_chart(
        self, df: pd.DataFrame, chart_config: Dict[str, Any]
    ) -> Optional[Path]:
        """Generate custom chart based on configuration"""

        try:
            chart_type = chart_config.get("type", "line")
            x_column = chart_config.get("x_column")
            y_column = chart_config.get("y_column")
            title = chart_config.get("title", "Custom Chart")

            if not x_column or not y_column:
                logger.warning("Missing x_column or y_column for custom chart")
                return None

            if x_column not in df.columns or y_column not in df.columns:
                logger.warning(f"Columns {x_column} or {y_column} not found in data")
                return None

            fig, ax = plt.subplots(figsize=(12, 8))

            if chart_type == "scatter":
                ax.scatter(df[x_column], df[y_column], alpha=0.6)
            elif chart_type == "line":
                df_sorted = df.sort_values(x_column)
                ax.plot(df_sorted[x_column], df_sorted[y_column], marker="o")
            elif chart_type == "bar":
                grouped = df.groupby(x_column)[y_column].mean()
                grouped.plot(kind="bar", ax=ax)
            else:
                # Default to scatter
                ax.scatter(df[x_column], df[y_column], alpha=0.6)

            ax.set_title(title, fontsize=16, fontweight="bold")
            ax.set_xlabel(x_column, fontsize=12)
            ax.set_ylabel(y_column, fontsize=12)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save chart
            chart_path = (
                self.charts_dir
                / f"custom_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(
                chart_path, dpi=self.config.get("chart_dpi", 300), bbox_inches="tight"
            )
            plt.close()

            return chart_path

        except Exception as e:
            logger.error(f"Error generating custom chart: {e}")
            return None

    async def cleanup_old_reports(self, days_to_keep: int = 30):
        """Clean up old reports and charts"""

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Clean up reports
            for report_file in self.output_dir.glob("*.json"):
                if report_file.stat().st_mtime < cutoff_date.timestamp():
                    report_file.unlink()
                    logger.info(f"Deleted old report: {report_file}")

            # Clean up charts
            for chart_file in self.charts_dir.glob("*.png"):
                if chart_file.stat().st_mtime < cutoff_date.timestamp():
                    chart_file.unlink()
                    logger.info(f"Deleted old chart: {chart_file}")

            logger.info(
                f"Cleanup completed - removed files older than {days_to_keep} days"
            )

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main function for testing the Advanced Analytics Engine"""

    print("🚀 Advanced Analytics Engine V2.03")
    print("=" * 50)

    try:
        # Initialize analytics engine
        engine = AdvancedAnalyticsEngine()

        # Generate performance analytics report
        print("📊 Generating Performance Analytics Report...")
        performance_report = await engine.generate_performance_analytics_report()

        if performance_report.data:
            print(f"✅ Performance report generated: {performance_report.report_id}")
            print(
                f"   - Total Predictions: {performance_report.data.get('summary_metrics', {}).get('total_predictions', 'N/A')}"
            )
            print(
                f"   - Accuracy: {performance_report.data.get('summary_metrics', {}).get('accuracy_percentage', 'N/A')}%"
            )
            print(
                f"   - Overall ROI: {performance_report.data.get('summary_metrics', {}).get('overall_roi_percentage', 'N/A')}%"
            )
            print(f"   - Charts Generated: {len(performance_report.charts)}")

            # Export to JSON
            json_path = await engine.export_report_to_json(performance_report)
            print(f"   - Report exported to: {json_path}")
        else:
            print("⚠️ No performance data available")

        # Example custom report
        print("\n📈 Generating Custom Report Example...")
        custom_config = {
            "title": "Track Performance Analysis",
            "description": "Analysis of performance by track and race type",
            "metrics": [
                {"name": "roi_by_track", "column": "roi", "group_by": "track_code"}
            ],
            "charts": [
                {
                    "type": "scatter",
                    "x_column": "prediction_confidence",
                    "y_column": "roi",
                    "title": "Confidence vs ROI Analysis",
                }
            ],
            "filters": {"start_date": datetime.now() - timedelta(days=90)},
        }

        custom_report = await engine.generate_custom_report(custom_config)
        print(f"✅ Custom report generated: {custom_report.report_id}")

        # Cleanup old reports
        print("\n🧹 Cleaning up old reports...")
        await engine.cleanup_old_reports(days_to_keep=30)

        print("\n✅ Advanced Analytics Engine testing completed successfully!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
