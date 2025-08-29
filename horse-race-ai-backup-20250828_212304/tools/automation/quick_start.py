#!/usr/bin/env python3
"""
🚀 Quick Start Pipeline Script
=============================

Simple launcher for the racing data pipeline automation system.
This script provides easy access to the most common pipeline operations.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.automation.pipeline_automation import PipelineAutomation
from rich.console import Console
from rich.panel import Panel

console = Console()


async def main():
    """Quick start menu for pipeline operations"""

    console.print(
        Panel.fit(
            "🏇 Horse Racing AI - Pipeline Quick Start\n\n"
            "Choose your action:\n"
            "1. 🔍 Start File Watcher (continuous monitoring)\n"
            "2. 📁 Process Existing Files (one-time)\n"
            "3. ⚙️ Run Complete Pipeline (manual)\n"
            "4. 📊 Check Pipeline Status\n"
            "5. ❌ Exit\n\n"
            "What would you like to do?",
            title="Pipeline Quick Start",
            border_style="bright_blue",
        )
    )

    automation = PipelineAutomation()

    while True:
        try:
            choice = console.input("\n[bold cyan]Enter your choice (1-5): [/bold cyan]")

            if choice == "1":
                console.print("\n[yellow]Starting file watcher service...[/yellow]")
                await automation.start_file_watcher()
                break

            elif choice == "2":
                console.print("\n[yellow]Processing existing files...[/yellow]")
                await automation.process_existing_files()
                break

            elif choice == "3":
                console.print("\n[yellow]Running complete pipeline...[/yellow]")
                await automation.run_complete_pipeline()
                break

            elif choice == "4":
                status = automation.get_pipeline_status()
                console.print(
                    Panel.fit(
                        f"📊 Pipeline Status\n\n"
                        f"• Base Path: {status['base_path']}\n"
                        f"• CSV Mapper: {'✅' if status['csv_mapper_available'] else '❌'}\n"
                        f"• Database Uploader: {'✅' if status['database_uploader_available'] else '❌'}\n"
                        f"• Pending ZIP Files: {status['pending_zip_files']}\n"
                        f"• Files: {', '.join(status['zip_files']) if status['zip_files'] else 'None'}\n\n"
                        f"Last Updated: {status['timestamp']}",
                        title="Current Status",
                        border_style="green",
                    )
                )

            elif choice == "5":
                console.print("\n[green]Goodbye! 👋[/green]")
                break

            else:
                console.print("\n[red]❌ Invalid choice. Please enter 1-5.[/red]")

        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️ Operation cancelled by user[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")
            continue


if __name__ == "__main__":
    asyncio.run(main())
