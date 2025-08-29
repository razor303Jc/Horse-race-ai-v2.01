// Test the real API integration
async function testAPI() {
  try {
    const response = await fetch("http://localhost:3000/api/daily_races");
    const data = await response.json();

    console.log("✅ PostgreSQL API Test Success!");
    console.log("📊 Total races available:", data.races.length);
    console.log(
      "🏇 Sample race venues:",
      data.races
        .slice(0, 3)
        .map((r) => r.venue)
        .join(", ")
    );

    // Test detailed race data
    if (data.races.length > 0) {
      const firstRaceId = data.races[0].race_id;
      const detailResponse = await fetch(
        `http://localhost:3000/api/race_details/${firstRaceId}`
      );
      const detailData = await detailResponse.json();

      console.log("🐎 Horses in first race:", detailData.horses.length);
      console.log(
        "🥇 Sample horses:",
        detailData.horses
          .slice(0, 2)
          .map((h) => h.horse_name)
          .join(", ")
      );
    }

    return true;
  } catch (error) {
    console.log("❌ API Test Failed:", error.message);
    return false;
  }
}

testAPI();
