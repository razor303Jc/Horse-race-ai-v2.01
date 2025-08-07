#!/usr/bin/env python3
"""
Demo: Scheduled Auto-Download System
====================================

Demonstrates the hourly auto-download system for horse race database.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from src.horse_racing_ai.automation.scheduled_auto_download import (
    ScheduledAutoDownloadSystem,
)
from rich.console import Console
from rich.panel import Panel

console = Console()


async def demo_scheduled_download():
    """Demonstrate the scheduled auto-download system."""

    console.print(
        Panel(
            "[bold blue]🏇 Horse Race Database Auto-Download Demo[/bold blue]\n\n"
            "This demo shows the scheduled auto-download system that:\n"
            "• Attempts downloads from 00:01 to 10:00 daily\n"
            "• Retries every hour until successful\n"
            "• Stops when download succeeds\n"
            "• Includes comprehensive logging and notifications",
            title="📥 Auto-Download Demo",
            border_style="blue",
        )
    )

    # Create the system
    system = ScheduledAutoDownloadSystem()

    console.print("\n[bold]Available Demo Options:[/bold]")
    console.print("1. 🧪 Run test mode (simulates multiple attempts)")
    console.print("2. 🎯 Run single manual attempt")
    console.print("3. 📅 Start full scheduler (runs continuously)")
    console.print("4. ❌ Exit")

    try:
        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            console.print("\n[bold blue]🧪 Running Test Mode[/bold blue]")
            await system.run_manual_test()

        elif choice == "2":
            console.print("\n[bold blue]🎯 Running Single Manual Attempt[/bold blue]")
            if await system.initialize():
                success = await system.attempt_download()
                await system.cleanup()
                if success:
                    console.print("[green]✅ Manual attempt successful![/green]")
                else:
                    console.print("[red]❌ Manual attempt failed[/red]")

        elif choice == "3":
            console.print("\n[bold blue]📅 Starting Full Scheduler[/bold blue]")
            console.print(
                "[yellow]⚠️  This will run continuously. Press Ctrl+C to stop.[/yellow]"
            )
            input("Press Enter to continue or Ctrl+C to cancel...")
            await system.run_scheduler()

        elif choice == "4":
            console.print("[yellow]👋 Demo cancelled[/yellow]")
            return

        else:
            console.print("[red]❌ Invalid choice[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Demo stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Demo error: {e}[/red]")


def show_schedule_info():
    """Show information about the download schedule."""

    console.print(
        Panel(
            "[bold blue]📅 Download Schedule Information[/bold blue]\n\n"
            "[bold]Daily Schedule:[/bold]\n"
            "1.  00:01 - First attempt (right after midnight)\n"
            "2.  01:01 - Second attempt\n"
            "3.  02:01 - Third attempt\n"
            "4.  03:01 - Fourth attempt\n"
            "5.  04:01 - Fifth attempt\n"
            "6.  05:01 - Sixth attempt\n"
            "7.  06:01 - Seventh attempt\n"
            "8.  07:01 - Eighth attempt\n"
            "9.  08:01 - Ninth attempt\n"
            "10. 09:01 - Tenth attempt\n"
            "11. 10:00 - Final attempt\n\n"
            "[bold]Behavior:[/bold]\n"
            "• Stops immediately when download succeeds\n"
            "• Maximum 11 attempts per day\n"
            "• Resets tracking at midnight\n"
            "• Sends notifications on success/failure\n"
            "• Logs all attempts with timestamps",
            title="🕐 Schedule Details",
            border_style="green",
        )
    )


async def main():
    """Main demo entry point."""

    # Show welcome message
    console.print(
        Panel(
            "[bold green]🎉 Welcome to Horse Racing AI Auto-Download Demo[/bold green]\n\n"
            "This demo showcases the automated download system that attempts\n"
            "to download horse race data every hour from 00:01 to 10:00 until successful.",
            title="🏇 Horse Racing AI",
            border_style="green",
        )
    )

    while True:
        console.print("\n[bold]Demo Menu:[/bold]")
        console.print("1. 📥 Test Auto-Download System")
        console.print("2. 📅 View Schedule Information")
        console.print("3. 🔧 System Status Check")
        console.print("4. ❌ Exit Demo")

        try:
            choice = input("\nSelect option (1-4): ").strip()

            if choice == "1":
                await demo_scheduled_download()

            elif choice == "2":
                show_schedule_info()

            elif choice == "3":
                console.print("\n[bold blue]🔧 System Status Check[/bold blue]")
                system = ScheduledAutoDownloadSystem()
                if await system.initialize():
                    console.print("[green]✅ System initialized successfully[/green]")
                    await system.cleanup()
                else:
                    console.print("[red]❌ System initialization failed[/red]")

            elif choice == "4":
                console.print("[yellow]👋 Goodbye![/yellow]")
                break

            else:
                console.print("[red]❌ Invalid choice. Please select 1-4.[/red]")

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Demo stopped by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Demo error: {e}[/red]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Demo stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)
