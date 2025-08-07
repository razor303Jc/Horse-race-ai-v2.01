"""Command-line interface for Horse Racing AI."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .automation.playwright_scraper import PlaywrightScraper
from .core.config import config
from .ml.predictor import RacePredictor
from .notifications.ntfy_client import ntfy_client

console = Console()


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(debug: bool) -> None:
    """Horse Racing AI - Comprehensive handicapping system."""
    if debug:
        config.debug = True
        console.print("[yellow]Debug mode enabled[/yellow]")


@main.command()
@click.option("--topic", help="NTFY topic name")
def test_notifications(topic: Optional[str]) -> None:
    """Test NTFY notifications."""
    console.print("[blue]Testing NTFY notifications...[/blue]")

    if topic:
        ntfy_client.topic = topic

    success = ntfy_client.test_connection()

    if success:
        console.print("[green]✅ Notifications working correctly[/green]")
    else:
        console.print("[red]❌ Notification test failed[/red]")
        sys.exit(1)


@main.command()
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
def test_scraper(headless: bool) -> None:
    """Test Playwright web scraper."""
    console.print("[blue]Testing Playwright scraper...[/blue]")

    async def run_test():
        try:
            async with PlaywrightScraper() as scraper:
                # Override headless setting
                scraper.config.headless = headless

                page = await scraper.create_page()
                await page.goto("https://httpbin.org/get")

                title = await page.title()
                console.print(
                    f"[green]✅ Browser test successful - Page title: {title}[/green]"
                )

                return True
        except Exception as e:
            console.print(f"[red]❌ Browser test failed: {e}[/red]")
            return False

    success = asyncio.run(run_test())
    if not success:
        sys.exit(1)


@main.command()
@click.option(
    "--model-type",
    default="random_forest",
    type=click.Choice(["random_forest", "gradient_boost", "logistic"]),
    help="Type of ML model to use",
)
def train_model(model_type: str) -> None:
    """Train a machine learning model."""
    console.print(f"[blue]Training {model_type} model...[/blue]")

    # This would need actual training data
    console.print("[yellow]Note: This is a demo - no training data provided[/yellow]")

    predictor = RacePredictor(model_type=model_type)
    console.print(f"[green]✅ Model initialized: {model_type}[/green]")


@main.command()
@click.argument("url")
@click.option("--username", prompt=True, help="Login username")
@click.option("--password", prompt=True, hide_input=True, help="Login password")
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
def scrape_race(url: str, username: str, password: str, headless: bool) -> None:
    """Scrape race data from a URL."""
    console.print(f"[blue]Scraping race data from {url}...[/blue]")

    async def run_scrape():
        try:
            async with PlaywrightScraper() as scraper:
                scraper.config.headless = headless

                page = await scraper.create_page()

                # Attempt login if credentials provided
                login_success = await scraper.login_to_site(
                    page, url, username, password
                )
                if login_success:
                    console.print("[green]✅ Login successful[/green]")
                else:
                    console.print("[yellow]⚠️ Login may have failed[/yellow]")

                # Scrape race data
                race_data = await scraper.scrape_race_data(page, url)

                if race_data:
                    console.print("[green]✅ Race data scraped successfully[/green]")

                    # Display race info
                    table = Table(title="Race Information")
                    table.add_column("Field", style="cyan")
                    table.add_column("Value", style="green")

                    table.add_row("Track", race_data.track)
                    table.add_row("Race Number", str(race_data.race_number))
                    table.add_row("Distance", race_data.distance)
                    table.add_row("Surface", race_data.surface)
                    table.add_row("Horses", str(len(race_data.horses)))

                    console.print(table)

                    return True
                else:
                    console.print("[red]❌ Failed to scrape race data[/red]")
                    return False

        except Exception as e:
            console.print(f"[red]❌ Scraping failed: {e}[/red]")
            return False

    success = asyncio.run(run_scrape())
    if not success:
        sys.exit(1)


@main.command()
def status() -> None:
    """Show system status."""
    console.print("[blue]Horse Racing AI System Status[/blue]")

    # Configuration status
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Debug Mode", str(config.debug))
    table.add_row("Log Level", config.log_level)
    table.add_row("Data Directory", str(config.data_dir))
    table.add_row("Models Directory", str(config.models_dir))
    table.add_row("NTFY Topic", config.notifications.topic or "Not configured")
    table.add_row("Database URL", config.database.url)

    console.print(table)

    # Directory status
    dirs_table = Table(title="Directories")
    dirs_table.add_column("Directory", style="cyan")
    dirs_table.add_column("Exists", style="green")
    dirs_table.add_column("Path", style="yellow")

    for name, path in [
        ("Data", config.data_dir),
        ("Models", config.models_dir),
        ("Logs", config.logs_dir),
        ("Cache", config.cache_dir),
    ]:
        exists = "✅" if path.exists() else "❌"
        dirs_table.add_row(name, exists, str(path))

    console.print(dirs_table)


@main.command()
def version() -> None:
    """Show version information."""
    from . import __author__, __version__

    console.print(f"[bold blue]Horse Racing AI v{__version__}[/bold blue]")
    console.print(f"[dim]By {__author__}[/dim]")


if __name__ == "__main__":
    main()
