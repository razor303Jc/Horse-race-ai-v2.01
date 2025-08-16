#!/bin/bash
# Enable Optional Services Script
# ===============================

echo "🎛️ ENABLING OPTIONAL SERVICES"
echo "============================="

echo "📋 Available optional services:"
echo "1. auto-downloader - Automated data collection"
echo "2. pgadmin - Database administration"
echo "3. docs - Documentation service"
echo "4. reports - Report generation"
echo "5. news-analyzer - AI news analysis"
echo "6. ntfy - Notification service"
echo ""

echo "🚀 Starting essential optional services..."

echo "📁 Starting pgAdmin (Database Admin)..."
docker-compose -f docker-compose.clean.yml --profile admin up -d pgadmin

echo "📚 Starting Documentation service..."
docker-compose -f docker-compose.clean.yml --profile docs up -d docs

echo "🔄 Starting Auto-downloader service..."
docker-compose -f docker-compose.clean.yml --profile auto-downloader up -d auto-downloader

echo "⏳ Waiting 20 seconds for services to start..."
sleep 20

echo "📊 Checking optional services status..."
docker-compose -f docker-compose.clean.yml ps

echo ""
echo "🌐 OPTIONAL SERVICE ENDPOINTS:"
echo "==============================="
echo "📁 pgAdmin: http://localhost:8081"
echo "   Default login: admin@horseracing.local / admin_password_123"
echo ""
echo "📚 Documentation: http://localhost:8080"
echo ""
echo "🔄 Auto-downloader: Background service (check logs)"
echo ""

echo "🔍 Checking logs for any startup issues..."
echo "pgAdmin logs:"
docker-compose -f docker-compose.clean.yml logs --tail=5 pgadmin 2>/dev/null || echo "pgAdmin not running"

echo ""
echo "Documentation logs:"
docker-compose -f docker-compose.clean.yml logs --tail=5 docs 2>/dev/null || echo "Docs not running"

echo ""
echo "Auto-downloader logs:"
docker-compose -f docker-compose.clean.yml logs --tail=5 auto-downloader 2>/dev/null || echo "Auto-downloader not running"
