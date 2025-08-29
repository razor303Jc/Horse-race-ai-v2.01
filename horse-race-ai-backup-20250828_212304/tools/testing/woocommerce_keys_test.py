#!/usr/bin/env python3
"""
WooCommerce URL Test
===================

Test if different keys return different data from the same file ID.
"""

import asyncio
import hashlib
from pathlib import Path

import aiohttp


async def test_woocommerce_urls():
    """Test both URLs to see if they return different data"""

    # CORRECTED URLs based on user's identification
    results_url = "https://horseracedatabase.com/?download_file=17605&order=wc_order_CdJf7udYlJDk3&email=justin.d.crooke%40gmail.com&key=6e9e40dd-781e-45fa-8f14-dc54734dd36f"
    cards_url = "https://horseracedatabase.com/?download_file=17605&order=wc_order_CdJf7udYlJDk3&email=justin.d.crooke%40gmail.com&key=df4a1dc3-9b7b-4efb-9f32-1b69fffa534b"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        print("🔍 Testing RESULTS URL...")
        async with session.get(results_url) as response:
            results_status = response.status
            results_content_type = response.headers.get("content-type", "")
            results_content = await response.read()
            results_hash = hashlib.md5(results_content).hexdigest()

            print(f"  Status: {results_status}")
            print(f"  Content-Type: {results_content_type}")
            print(f"  Content Length: {len(results_content):,} bytes")
            print(f"  MD5 Hash: {results_hash}")
            print(f"  First 200 chars: {results_content[:200]}")

        print("\n" + "=" * 50 + "\n")

        # Add delay to avoid rate limiting
        await asyncio.sleep(2)

        print("🔍 Testing CARDS URL...")
        async with session.get(cards_url) as response:
            cards_status = response.status
            cards_content_type = response.headers.get("content-type", "")
            cards_content = await response.read()
            cards_hash = hashlib.md5(cards_content).hexdigest()

            print(f"  Status: {cards_status}")
            print(f"  Content-Type: {cards_content_type}")
            print(f"  Content Length: {len(cards_content):,} bytes")
            print(f"  MD5 Hash: {cards_hash}")
            print(f"  First 200 chars: {cards_content[:200]}")

        print("\n" + "=" * 50 + "\n")

        if results_hash == cards_hash:
            print("❌ IDENTICAL CONTENT - Both URLs return the same data!")
            print("   This confirms the issue: different keys returning same data")
        else:
            print("✅ DIFFERENT CONTENT - URLs return different data as expected")
            print("   The issue might be in the download timing or processing")

        print(f"\nResults Hash: {results_hash}")
        print(f"Cards Hash:   {cards_hash}")


if __name__ == "__main__":
    asyncio.run(test_woocommerce_urls())
