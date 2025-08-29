#!/usr/bin/env python3
"""
🏇 Horse Racing AI Pipeline Visual Chart Generator
Creates comprehensive visual representations of the 17-stage pipeline

This tool generates:
📊 ASCII Flow Chart of all 17 stages
🔄 Process Flow Diagrams by Phase
⏱️ Timing and Duration Charts
🔗 Dependencies and Data Flow Visualization
📋 Expandable Process Details

Author: AI Assistant
Date: August 15, 2025
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch


class PipelineVisualizer:
    """Generate visual charts for the horse racing AI pipeline"""

    def __init__(self, config_path="config/complete_17_stage_config.json"):
        self.config_path = Path(config_path)
        self.load_pipeline_config()
        self.setup_colors()

    def load_pipeline_config(self):
        """Load the pipeline configuration"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                self.stages = self.config.get("stages", [])
                self.phases = self.organize_by_phase()
                print(
                    f"✅ Loaded {len(self.stages)} stages across {len(self.phases)} phases"
                )
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            self.config = {}
            self.stages = []
            self.phases = {}

    def organize_by_phase(self):
        """Organize stages by their phases"""
        phases = {}
        for stage in self.stages:
            phase = stage.get("phase", "unknown")
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(stage)
        return phases

    def setup_colors(self):
        """Setup color scheme for different phases"""
        self.phase_colors = {
            "data_acquisition": "#3498db",  # Blue
            "feature_engineering": "#2ecc71",  # Green
            "advanced_analytics": "#e74c3c",  # Red
            "simulation": "#f39c12",  # Orange
            "strategy": "#9b59b6",  # Purple
            "pre_race": "#1abc9c",  # Teal
        }

        self.critical_color = "#e74c3c"  # Red for critical
        self.optional_color = "#95a5a6"  # Gray for optional

    def print_ascii_pipeline_chart(self):
        """Generate ASCII flow chart of the entire pipeline"""
        print("\n🏇 HORSE RACING AI PIPELINE - COMPLETE 17-STAGE FLOW CHART")
        print("=" * 80)
        print()

        # Header with timing info
        total_duration = sum(s["duration_minutes"] for s in self.stages)
        print(
            f"📊 Total Duration: {total_duration} minutes ({total_duration/60:.1f} hours)"
        )
        print(
            f"🔴 Critical Stages: {sum(1 for s in self.stages if s.get('critical', True))}"
        )
        print(
            f"🟡 Optional Stages: {sum(1 for s in self.stages if not s.get('critical', True))}"
        )
        print()

        # Pipeline flow by phase
        for phase_name, phase_stages in self.phases.items():
            phase_duration = sum(s["duration_minutes"] for s in phase_stages)

            print(
                f"┌─ 📋 {phase_name.upper().replace('_', ' ')} PHASE ({phase_duration}min)"
            )
            print(f"│")

            for i, stage in enumerate(phase_stages):
                critical_icon = "🔴" if stage.get("critical", True) else "🟡"
                connector = "├─" if i < len(phase_stages) - 1 else "└─"

                print(
                    f"│ {connector} {critical_icon} {stage['name']} ({stage['duration_minutes']}min)"
                )
                print(
                    f"│ {'│  ' if i < len(phase_stages) - 1 else '   '} └─ {stage['description']}"
                )
                if i < len(phase_stages) - 1:
                    print(f"│ │")
            print(f"│")
            print(f"└─ ⏬ Flows to next phase")
            print()

    def print_detailed_process_flow(self):
        """Print detailed process flow with expanded processes"""
        print("\n🔄 DETAILED PROCESS FLOW WITH EXPANSION OPPORTUNITIES")
        print("=" * 80)
        print()

        for phase_name, phase_stages in self.phases.items():
            print(f"📋 {phase_name.upper().replace('_', ' ')} PHASE")
            print("─" * 50)

            for stage in phase_stages:
                print(f"\n🔹 {stage['name'].upper()} ({stage['duration_minutes']}min)")
                print(f"   Description: {stage['description']}")
                print(f"   Critical: {'Yes' if stage.get('critical', True) else 'No'}")

                # Add process expansion details based on stage type
                processes = self.get_stage_processes(stage["name"])
                if processes:
                    print(f"   Current Processes:")
                    for process in processes:
                        print(f"     • {process}")

                expansions = self.get_expansion_opportunities(stage["name"])
                if expansions:
                    print(f"   🚀 Expansion Opportunities:")
                    for expansion in expansions:
                        print(f"     ➕ {expansion}")

                print()

    def get_stage_processes(self, stage_name):
        """Get current processes for a stage"""
        process_map = {
            "data_download": [
                "API connection management",
                "Rate limiting and throttling",
                "Data format validation",
                "Error handling and retries",
            ],
            "data_validation": [
                "Schema validation",
                "Data completeness checks",
                "Integrity verification",
                "Quality scoring",
            ],
            "data_preprocessing": [
                "Data cleaning and normalization",
                "Missing value handling",
                "Format standardization",
                "Outlier detection",
            ],
            "data_relationships": [
                "Entity relationship mapping",
                "Foreign key validation",
                "Data lineage tracking",
                "Reference integrity",
            ],
            "feature_engineering": [
                "Statistical feature extraction",
                "Derived variable creation",
                "Feature scaling and encoding",
                "Dimensionality optimization",
            ],
            "contextual_analysis": [
                "Environmental factor analysis",
                "Historical context matching",
                "Situational adjustments",
                "External data integration",
            ],
            "form_scoring": [
                "Performance history analysis",
                "Weighted scoring algorithms",
                "Form trend calculation",
                "Comparative ranking",
            ],
            "power_ratings": [
                "Speed figure calculations",
                "Class rating adjustments",
                "Track variant analysis",
                "Performance normalization",
            ],
            "speed_analysis": [
                "Sectional time analysis",
                "Pace scenario modeling",
                "Speed map generation",
                "Finishing kick analysis",
            ],
            "ml_model_training": [
                "Feature selection",
                "Model hyperparameter tuning",
                "Cross-validation",
                "Ensemble model creation",
            ],
            "monte_carlo_simulations": [
                "Random scenario generation",
                "Probability distribution modeling",
                "Outcome simulation",
                "Confidence interval calculation",
            ],
            "race_trends": [
                "Historical pattern analysis",
                "Track bias detection",
                "Seasonal trend identification",
                "Predictive pattern matching",
            ],
            "composite_scoring": [
                "Multi-factor score combination",
                "Weighted ranking algorithms",
                "Final rating calculation",
                "Confidence scoring",
            ],
            "betting_strategies": [
                "Value bet identification",
                "Kelly criterion application",
                "Risk management rules",
                "Portfolio optimization",
            ],
            "ai_selections": [
                "Final candidate filtering",
                "Confidence threshold application",
                "Selection ranking",
                "Risk assessment",
            ],
            "report_generation": [
                "Analysis report creation",
                "Visualization generation",
                "Summary statistics",
                "Recommendation formatting",
            ],
            "pre_race_updates": [
                "Live data monitoring",
                "Last-minute adjustments",
                "Scratchings handling",
                "Real-time recalculation",
            ],
        }
        return process_map.get(stage_name, [])

    def get_expansion_opportunities(self, stage_name):
        """Get expansion opportunities for each stage"""
        expansion_map = {
            "data_download": [
                "Multi-source data aggregation",
                "Real-time streaming capabilities",
                "Advanced caching strategies",
                "Parallel download optimization",
            ],
            "data_validation": [
                "AI-powered anomaly detection",
                "Advanced statistical validation",
                "Cross-source verification",
                "Automated quality scoring",
            ],
            "data_preprocessing": [
                "Advanced outlier detection algorithms",
                "Intelligent missing value imputation",
                "Feature transformation pipelines",
                "Data augmentation techniques",
            ],
            "data_relationships": [
                "Graph database integration",
                "Advanced entity resolution",
                "Relationship strength scoring",
                "Dynamic schema adaptation",
            ],
            "feature_engineering": [
                "Automated feature discovery",
                "Deep learning feature extraction",
                "Time-series feature engineering",
                "Domain-specific feature libraries",
            ],
            "contextual_analysis": [
                "Weather impact modeling",
                "Social media sentiment analysis",
                "Track condition algorithms",
                "Real-time context updates",
            ],
            "form_scoring": [
                "Advanced decay functions",
                "Opposition strength adjustments",
                "Multi-dimensional form analysis",
                "Predictive form modeling",
            ],
            "power_ratings": [
                "Advanced speed figure calculations",
                "Multi-track comparison algorithms",
                "Distance-specific adjustments",
                "Going condition normalization",
            ],
            "speed_analysis": [
                "Advanced pace modeling",
                "Energy expenditure analysis",
                "Tactical speed analysis",
                "Comparative pace profiling",
            ],
            "ml_model_training": [
                "AutoML integration",
                "Neural architecture search",
                "Advanced ensemble methods",
                "Online learning capabilities",
            ],
            "monte_carlo_simulations": [
                "Advanced probability distributions",
                "Correlated variable modeling",
                "Scenario-based simulations",
                "Risk factor integration",
            ],
            "race_trends": [
                "Machine learning pattern detection",
                "Seasonal adjustment algorithms",
                "Track-specific trend analysis",
                "Predictive trend modeling",
            ],
            "composite_scoring": [
                "Dynamic weighting algorithms",
                "Multi-objective optimization",
                "Uncertainty quantification",
                "Adaptive scoring methods",
            ],
            "betting_strategies": [
                "Advanced portfolio theory",
                "Dynamic bankroll management",
                "Multi-market strategies",
                "Risk-adjusted returns optimization",
            ],
            "ai_selections": [
                "Explainable AI integration",
                "Multi-criteria decision analysis",
                "Confidence calibration",
                "Selection diversity optimization",
            ],
            "report_generation": [
                "Interactive visualizations",
                "Natural language generation",
                "Personalized reporting",
                "Real-time dashboard updates",
            ],
            "pre_race_updates": [
                "Streaming data integration",
                "Predictive adjustment algorithms",
                "Real-time confidence updates",
                "Live risk recalculation",
            ],
        }
        return expansion_map.get(stage_name, [])

    def create_timing_chart(self, save_path="docs/pipeline_timing_chart.png"):
        """Create a visual timing chart"""
        plt.style.use("default")
        fig, ax = plt.subplots(figsize=(16, 10))

        # Calculate positions
        y_positions = []
        stage_names = []
        durations = []
        colors = []

        y_pos = 0
        for phase_name, phase_stages in self.phases.items():
            phase_color = self.phase_colors.get(phase_name, "#34495e")

            for stage in phase_stages:
                y_positions.append(y_pos)
                stage_names.append(f"{stage['name']} ({stage['duration_minutes']}min)")
                durations.append(stage["duration_minutes"])
                colors.append(phase_color)
                y_pos += 1

        # Create horizontal bar chart
        bars = ax.barh(
            y_positions,
            durations,
            color=colors,
            alpha=0.7,
            edgecolor="black",
            linewidth=0.5,
        )

        # Customize chart
        ax.set_yticks(y_positions)
        ax.set_yticklabels(stage_names, fontsize=9)
        ax.set_xlabel("Duration (minutes)", fontsize=12, fontweight="bold")
        ax.set_title(
            "🏇 Horse Racing AI Pipeline - Stage Duration Chart",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )

        # Add duration labels on bars
        for i, (bar, duration) in enumerate(zip(bars, durations)):
            width = bar.get_width()
            ax.text(
                width + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{duration}m",
                ha="left",
                va="center",
                fontweight="bold",
            )

        # Add phase separators and labels
        y_pos = 0
        for phase_name, phase_stages in self.phases.items():
            phase_y_start = y_pos
            phase_y_end = y_pos + len(phase_stages) - 1
            phase_y_center = (phase_y_start + phase_y_end) / 2

            # Add phase label on the right
            phase_color = self.phase_colors.get(phase_name, "#34495e")
            ax.text(
                max(durations) + 15,
                phase_y_center,
                phase_name.replace("_", " ").title(),
                rotation=90,
                ha="center",
                va="center",
                fontweight="bold",
                fontsize=10,
                color=phase_color,
            )

            # Add separator line
            if y_pos > 0:
                ax.axhline(y=y_pos - 0.5, color="gray", linestyle="--", alpha=0.5)

            y_pos += len(phase_stages)

        # Add grid and styling
        ax.grid(axis="x", alpha=0.3)
        ax.set_xlim(0, max(durations) + 30)

        # Add total duration text
        total_duration = sum(durations)
        ax.text(
            0.02,
            0.98,
            f"Total Pipeline Duration: {total_duration} minutes ({total_duration/60:.1f} hours)",
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
            verticalalignment="top",
        )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"✅ Timing chart saved to: {save_path}")
        plt.close()

    def create_flow_diagram(self, save_path="docs/pipeline_flow_diagram.png"):
        """Create a visual flow diagram"""
        plt.style.use("default")
        fig, ax = plt.subplots(figsize=(20, 14))

        # Layout parameters
        phase_width = 3.0
        stage_height = 0.8
        phase_spacing = 0.5

        x_pos = 0
        max_y = 0

        # Draw each phase
        for phase_name, phase_stages in self.phases.items():
            phase_color = self.phase_colors.get(phase_name, "#34495e")

            # Calculate phase height
            phase_height = len(phase_stages) * (stage_height + 0.1) + 0.5
            max_y = max(max_y, phase_height)

            # Draw phase background
            phase_rect = FancyBboxPatch(
                (x_pos, 0),
                phase_width,
                phase_height,
                boxstyle="round,pad=0.1",
                facecolor=phase_color,
                alpha=0.2,
                edgecolor=phase_color,
                linewidth=2,
            )
            ax.add_patch(phase_rect)

            # Phase title
            ax.text(
                x_pos + phase_width / 2,
                phase_height + 0.2,
                phase_name.replace("_", " ").title(),
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=12,
                color=phase_color,
            )

            # Draw stages within phase
            y_pos = phase_height - 0.3 - stage_height
            for stage in phase_stages:
                critical_color = (
                    self.critical_color
                    if stage.get("critical", True)
                    else self.optional_color
                )

                # Stage box
                stage_rect = FancyBboxPatch(
                    (x_pos + 0.1, y_pos),
                    phase_width - 0.2,
                    stage_height,
                    boxstyle="round,pad=0.05",
                    facecolor="white",
                    edgecolor=critical_color,
                    linewidth=2,
                )
                ax.add_patch(stage_rect)

                # Stage text
                stage_text = f"{stage['name']}\n({stage['duration_minutes']}min)"
                ax.text(
                    x_pos + phase_width / 2,
                    y_pos + stage_height / 2,
                    stage_text,
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                )

                y_pos -= stage_height + 0.1

            # Arrow to next phase
            if x_pos < (len(self.phases) - 1) * (phase_width + phase_spacing):
                arrow = patches.FancyArrowPatch(
                    (x_pos + phase_width, phase_height / 2),
                    (x_pos + phase_width + phase_spacing, phase_height / 2),
                    arrowstyle="->",
                    mutation_scale=20,
                    color="darkblue",
                    linewidth=3,
                )
                ax.add_patch(arrow)

            x_pos += phase_width + phase_spacing

        # Set axis limits and remove axes
        ax.set_xlim(-0.5, x_pos)
        ax.set_ylim(-0.5, max_y + 1)
        ax.set_aspect("equal")
        ax.axis("off")

        # Add title
        ax.text(
            x_pos / 2,
            max_y + 0.8,
            "🏇 Horse Racing AI Pipeline - 17-Stage Flow Diagram",
            ha="center",
            va="center",
            fontsize=18,
            fontweight="bold",
        )

        # Add legend
        legend_elements = [
            plt.Rectangle(
                (0, 0),
                1,
                1,
                facecolor="white",
                edgecolor=self.critical_color,
                linewidth=2,
                label="Critical Stage",
            ),
            plt.Rectangle(
                (0, 0),
                1,
                1,
                facecolor="white",
                edgecolor=self.optional_color,
                linewidth=2,
                label="Optional Stage",
            ),
        ]
        ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1, 0.1))

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"✅ Flow diagram saved to: {save_path}")
        plt.close()

    def generate_all_charts(self):
        """Generate all visual charts"""
        print("🎨 GENERATING COMPLETE PIPELINE VISUALIZATION SUITE")
        print("=" * 60)

        # Create docs directory if it doesn't exist
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)

        # Generate ASCII charts
        self.print_ascii_pipeline_chart()
        self.print_detailed_process_flow()

        # Generate visual charts
        try:
            self.create_timing_chart()
            self.create_flow_diagram()
        except ImportError:
            print("⚠️ Matplotlib not available - skipping visual charts")
            print("📝 Install with: pip install matplotlib")

        print("\n🎊 All pipeline visualizations complete!")


def main():
    """Main function to generate pipeline charts"""
    visualizer = PipelineVisualizer()
    visualizer.generate_all_charts()


if __name__ == "__main__":
    main()
