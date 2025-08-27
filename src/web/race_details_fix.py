# Updated race_details endpoint
entries_query = """
SELECT 
    rd.name as horse_name,
    rd.age as horse_age,
    rd.country as horse_country,
    rd.horse_number,
    rd.draw,
    rd.weight as weight_kg,
    rd.jockey,
    rd.trainer,
    rd.odds,
    rd.fav as favourite_position,
    rd.timeform_comments as form,
    rd.horse_rate as official_rating,
    rd.odds_decimal
FROM racecard_details rd
WHERE rd.race_id = %s
ORDER BY rd.horse_number;
"""
