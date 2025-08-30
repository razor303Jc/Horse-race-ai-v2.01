#!/bin/bash
# PostgreSQL Entity Tables Setup via Docker Exec
# ==============================================
# Creates entity tables directly in PostgreSQL container

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

success() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

# Function to create databases
create_databases() {
    log "🗄️ Creating PostgreSQL databases..."
    
    local databases=("results" "cards" "advanced_metrics")
    
    for db in "${databases[@]}"; do
        log "Creating database: $db"
        docker exec horse_racing_postgres_clean psql -U horse_racing -d postgres -c "
            CREATE DATABASE $db;
        " 2>/dev/null || {
            # Database might already exist, check if it exists
            if docker exec horse_racing_postgres_clean psql -U horse_racing -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$db';" | grep -q 1; then
                info "Database $db already exists"
            else
                error "Failed to create database: $db"
                return 1
            fi
        }
        info "✅ Database $db ready"
    done
    
    success "✅ All databases created"
    return 0
}

# Function to create entity tables
create_entity_tables() {
    log "🗃️ Creating entity tables in results database..."
    
    # Copy schema files into container
    log "Copying schema files to container..."
    docker cp database/schemas horse_racing_postgres_clean:/tmp/schemas
    
    # Create horses entity table
    log "Creating horses_entity table..."
    docker exec horse_racing_postgres_clean psql -U horse_racing -d results -f /tmp/schemas/horses_entity.sql || {
        error "Failed to create horses_entity table"
        return 1
    }
    info "✅ horses_entity table created"
    
    # Create jockeys entity table
    log "Creating jockeys_entity table..."
    docker exec horse_racing_postgres_clean psql -U horse_racing -d results -f /tmp/schemas/jockeys_entity.sql || {
        error "Failed to create jockeys_entity table"
        return 1
    }
    info "✅ jockeys_entity table created"
    
    # Create trainers entity table
    log "Creating trainers_entity table..."
    docker exec horse_racing_postgres_clean psql -U horse_racing -d results -f /tmp/schemas/trainers_entity.sql || {
        error "Failed to create trainers_entity table"
        return 1
    }
    info "✅ trainers_entity table created"
    
    success "✅ All entity tables created successfully"
    return 0
}

# Function to verify tables
verify_tables() {
    log "🔍 Verifying entity tables..."
    
    local tables=("horses_entity" "jockeys_entity" "trainers_entity")
    
    for table in "${tables[@]}"; do
        local count
        count=$(docker exec horse_racing_postgres_clean psql -U horse_racing -d results -t -c "SELECT COUNT(*) FROM $table;" | tr -d ' ')
        info "✅ Table $table: exists ($count rows)"
    done
    
    success "✅ All tables verified"
    return 0
}

# Main execution
main() {
    log "🚀 Setting up PostgreSQL entity tables..."
    
    # Check if PostgreSQL container is running
    if ! docker ps | grep -q horse_racing_postgres_clean; then
        error "PostgreSQL container not running. Please start with: docker-compose up -d"
        exit 1
    fi
    
    # Test basic connection
    if ! docker exec horse_racing_postgres_clean psql -U horse_racing -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        error "Cannot connect to PostgreSQL container"
        exit 1
    fi
    
    info "✅ PostgreSQL container connection verified"
    
    # Execute setup steps
    if create_databases && create_entity_tables && verify_tables; then
        echo
        success "🎉 PostgreSQL entity tables setup completed successfully!"
        echo
        info "📊 Created tables:"
        info "  - horses_entity (auto-increment ID + original horse_id)"
        info "  - jockeys_entity (auto-increment ID + original jockey_id)"
        info "  - trainers_entity (auto-increment ID + original trainer_id)"
        echo
        info "🔗 Next steps:"
        info "  1. Load test data: ./load_test_data.sh --dataset 2025-08-26"
        info "  2. Run testing suite: ./run_comprehensive_tests.sh"
        echo
    else
        error "❌ Entity tables setup failed"
        exit 1
    fi
}

# Execute main function
main "$@"
