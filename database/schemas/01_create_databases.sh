#!/bin/bash
# 01_create_databases.sql
# Creates all required databases for the Horse Racing AI system

set -e

# Create the three main databases
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create the main results database
    CREATE DATABASE results_horse_racing_db OWNER horse_racing;
    
    -- Create the cards database  
    CREATE DATABASE cards_horse_racing_db OWNER horse_racing;
    
    -- Create the AI database
    CREATE DATABASE ai_horse_racing_db OWNER horse_racing;
    
    -- Grant all privileges to the horse_racing user
    GRANT ALL PRIVILEGES ON DATABASE results_horse_racing_db TO horse_racing;
    GRANT ALL PRIVILEGES ON DATABASE cards_horse_racing_db TO horse_racing;
    GRANT ALL PRIVILEGES ON DATABASE ai_horse_racing_db TO horse_racing;
    
    -- Show created databases
    \\l
EOSQL

echo "✅ All three databases created successfully!"
echo "  - results_horse_racing_db"
echo "  - cards_horse_racing_db" 
echo "  - ai_horse_racing_db"
