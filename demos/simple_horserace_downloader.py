#!/usr/bin/env python3
"""
Simple Horse Race Database Downloader
=====================================

Based on the mother project's approach but with human-like behavior
"""

import asyncio
import os
import zipfile
from datetime import datetime
from pathlib import Path

import aiofiles
import aiohttp
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
load_dotenv()

console = Console()


class SimpleHorseRaceDownloader:
    """Simple downloader using direct HTTP requests like the mother project."""

    def __init__(self):
        self.username = os.getenv("HORSERACE_DB_USERNAME")
        self.password = os.getenv("HORSERACE_DB_PASSWORD")
        self.results_url = os.getenv("HORSERACE_DB_RESULTS_URL")
        self.cards_url = os.getenv("HORSERACE_DB_CARDS_URL")

        # Data directories
        self.download_dir = Path("data/horseracedatabase")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        if not all([self.username, self.password, self.results_url, self.cards_url]):
            raise ValueError("Missing required environment variables in .env file")

    async def download_file(
        self, session: aiohttp.ClientSession, url: str, file_type: str
    ) -> bool:
        """Download a single file using direct HTTP request."""
        try:
            console.print(f"📥 Downloading {file_type} data...")

            async with session.get(url) as response:
                console.print(f"📡 Status: {response.status}")
                console.print(
                    f"📊 Content-Type: {response.headers.get('content-type', 'unknown')}"
                )

                if response.status == 200:
                    content_type = response.headers.get("content-type", "").lower()

                    if "zip" in content_type or "octet-stream" in content_type:
                        # Generate filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{file_type}_{timestamp}.zip"
                        file_path = self.download_dir / filename

                        # Save the file
                        async with aiofiles.open(file_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)

                        file_size = file_path.stat().st_size
                        console.print(
                            f"✅ Downloaded {file_type} ZIP ({file_size:,} bytes) to {file_path}"
                        )

                        # Extract the ZIP file
                        return await self.extract_zip_file(file_path, file_type)

                    else:
                        console.print(f"❌ Not a ZIP file, got: {content_type}")
                        # Save first part for debugging
                        debug_file = (
                            self.download_dir / f"debug_{file_type}_response.html"
                        )
                        content = await response.text()
                        async with aiofiles.open(debug_file, "w") as f:
                            await f.write(content[:2000])  # First 2000 chars
                        console.print(f"💾 Saved debug response to {debug_file}")
                        return False
                else:
                    console.print(f"❌ Download failed with status: {response.status}")
                    return False

        except Exception as e:
            console.print(f"❌ Error downloading {file_type}: {e}")
            return False

    async def extract_zip_file(self, zip_path: Path, file_type: str) -> bool:
        """Extract ZIP file contents."""
        try:
            extract_dir = self.download_dir / f"extracted_{file_type}"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                files = zip_ref.namelist()
                console.print(
                    f"📦 Extracting {len(files)} files from {file_type} ZIP..."
                )
                zip_ref.extractall(extract_dir)

                # Show some files
                console.print(f"📄 Extracted files in {extract_dir}:")
                for filename in files[:5]:
                    console.print(f"   - {filename}")
                if len(files) > 5:
                    console.print(f"   ... and {len(files) - 5} more files")

            # Clean up ZIP file
            zip_path.unlink()
            console.print(f"🗑️ Removed ZIP file: {zip_path.name}")
            console.print(f"✅ {file_type.title()} extraction complete!")
            return True

        except Exception as e:
            console.print(f"❌ Extraction failed for {file_type}: {e}")
            return False

    async def run_download(self) -> dict:
        """Run the complete download process."""
        results = {"results": False, "cards": False}

        # Create session with proper headers
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            # Download results file
            console.print("\n🔄 Starting results download...")
            results["results"] = await self.download_file(
                session, self.results_url, "results"
            )

            # Small delay between downloads
            await asyncio.sleep(2)

            # Download cards file
            console.print("\n🔄 Starting cards download...")
            results["cards"] = await self.download_file(
                session, self.cards_url, "cards"
            )

        return results


async def main():
    """Main function."""
    console.print(
        Panel.fit(
            "🏇 [bold cyan]Simple Horse Race Database Downloader[/bold cyan]\n"
            "[yellow]Direct download using HTTP requests[/yellow]",
            border_style="blue",
        )
    )

    try:
        downloader = SimpleHorseRaceDownloader()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            task = progress.add_task("Starting download process...", total=None)
            results = await downloader.run_download()
            progress.update(task, description="Download process complete")

        # Show results
        console.print("\n📊 [bold]Download Results:[/bold]")
        for file_type, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            console.print(f"  • {file_type.title()}: {status}")

        if any(results.values()):
            console.print(
                "\n🎉 [bold green]Data successfully downloaded and processed![/bold green]"
            )
        else:
            console.print("\n⚠️ [yellow]No data was successfully processed[/yellow]")

    except Exception as e:
        console.print(f"\n❌ [red]Error: {e}[/red]")


if __name__ == "__main__":
    asyncio.run(main())
