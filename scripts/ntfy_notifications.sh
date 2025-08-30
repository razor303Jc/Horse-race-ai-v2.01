#!/bin/bash
# NTFY Horse Racing AI Integration Script
# Sends various system notifications via NTFY

NTFY_URL="http://localhost:8082"
SYSTEM_TOPIC="horserace-system"
PROCESSING_TOPIC="horserace-processing"
ALERTS_TOPIC="horserace-alerts"
MONITORING_TOPIC="horserace-monitoring"

# Function to send NTFY notification
send_ntfy() {
    local topic=$1
    local title=$2
    local message=$3
    local priority=${4:-"default"}
    local tags=${5:-"system"}
    
    curl -X POST \
        -H "Title: $title" \
        -H "Tags: $tags" \
        -H "Priority: $priority" \
        -d "$message" \
        "$NTFY_URL/$topic"
}

# System status notification
send_system_status() {
    local status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(web_app|node_red|ntfy|postgres)" | wc -l)
    
    if [ $status -ge 4 ]; then
        send_ntfy "$SYSTEM_TOPIC" "✅ System Status: Healthy" \
            "All core services are running properly. Web App, Node-RED, NTFY, and PostgreSQL are online." \
            "default" "green_circle,system,healthy"
    else
        send_ntfy "$ALERTS_TOPIC" "⚠️ System Status: Degraded" \
            "Some core services may be offline. Please check system status." \
            "high" "warning,system,degraded"
    fi
}

# Data processing completion notification
send_processing_complete() {
    local files_processed=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    send_ntfy "$PROCESSING_TOPIC" "🔄 Data Processing Complete" \
        "Processed $files_processed files at $timestamp. Data pipeline execution successful." \
        "default" "arrow_forward,processing,complete"
}

# Error notification
send_error_alert() {
    local error_type=$1
    local error_message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    send_ntfy "$ALERTS_TOPIC" "❌ Error Alert: $error_type" \
        "Error occurred at $timestamp: $error_message" \
        "urgent" "rotating_light,error,alert"
}

# AI model training notification
send_training_complete() {
    local model_name=$1
    local accuracy=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    send_ntfy "$PROCESSING_TOPIC" "🤖 AI Training Complete" \
        "Model '$model_name' training finished at $timestamp with accuracy: $accuracy%" \
        "default" "robot,ai,training,complete"
}

# Database backup notification
send_backup_complete() {
    local backup_size=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    send_ntfy "$MONITORING_TOPIC" "💾 Database Backup Complete" \
        "Database backup completed at $timestamp. Backup size: $backup_size MB" \
        "default" "floppy_disk,backup,database"
}

# High-value prediction alert
send_prediction_alert() {
    local race_name=$1
    local horse_name=$2
    local confidence=$3
    local value_rating=$4
    
    send_ntfy "$ALERTS_TOPIC" "🏆 High-Value Prediction Alert" \
        "🐎 $horse_name in $race_name - Confidence: $confidence% - Value Rating: $value_rating/10" \
        "high" "horse,money_with_wings,prediction,value"
}

# System performance monitoring
send_performance_alert() {
    local metric_name=$1
    local current_value=$2
    local threshold=$3
    local status=$4
    
    if [ "$status" == "warning" ]; then
        send_ntfy "$MONITORING_TOPIC" "⚠️ Performance Warning" \
            "$metric_name is at $current_value (threshold: $threshold). System performance may be degraded." \
            "default" "warning,performance,monitoring"
    elif [ "$status" == "critical" ]; then
        send_ntfy "$ALERTS_TOPIC" "🚨 Performance Critical" \
            "$metric_name is at $current_value (threshold: $threshold). Immediate attention required!" \
            "urgent" "rotating_light,critical,performance"
    fi
}

# Daily summary notification
send_daily_summary() {
    local races_processed=$1
    local predictions_made=$2
    local accuracy_today=$3
    local date=$(date '+%Y-%m-%d')
    
    send_ntfy "$MONITORING_TOPIC" "📊 Daily Summary - $date" \
        "📈 Races: $races_processed | 🎯 Predictions: $predictions_made | 📊 Accuracy: $accuracy_today%" \
        "default" "chart_with_upwards_trend,daily,summary"
}

# Emergency stop notification
send_emergency_stop() {
    local triggered_by=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    send_ntfy "$ALERTS_TOPIC" "🛑 EMERGENCY STOP TRIGGERED" \
        "Emergency stop activated by $triggered_by at $timestamp. All automated processes halted." \
        "urgent" "octagonal_sign,emergency,stop,critical"
}

# Test notification
send_test_notification() {
    send_ntfy "$SYSTEM_TOPIC" "🧪 NTFY Test Notification" \
        "This is a test notification from the Horse Racing AI system. NTFY integration is working correctly!" \
        "default" "test_tube,test,system"
}

# Command line interface
case "$1" in
    "status")
        send_system_status
        ;;
    "processing")
        send_processing_complete "${2:-0}"
        ;;
    "error")
        send_error_alert "${2:-Unknown}" "${3:-No message provided}"
        ;;
    "training")
        send_training_complete "${2:-Unknown Model}" "${3:-0}"
        ;;
    "backup")
        send_backup_complete "${2:-0}"
        ;;
    "prediction")
        send_prediction_alert "${2:-Unknown Race}" "${3:-Unknown Horse}" "${4:-0}" "${5:-0}"
        ;;
    "performance")
        send_performance_alert "${2:-Unknown Metric}" "${3:-0}" "${4:-0}" "${5:-warning}"
        ;;
    "daily")
        send_daily_summary "${2:-0}" "${3:-0}" "${4:-0}"
        ;;
    "emergency")
        send_emergency_stop "${2:-System}"
        ;;
    "test")
        send_test_notification
        ;;
    *)
        echo "Usage: $0 {status|processing|error|training|backup|prediction|performance|daily|emergency|test}"
        echo ""
        echo "Examples:"
        echo "  $0 test                                    # Send test notification"
        echo "  $0 status                                 # Send system status"
        echo "  $0 processing 15                         # Send processing complete (15 files)"
        echo "  $0 error 'Database' 'Connection failed'  # Send error alert"
        echo "  $0 training 'Model_v2.1' 87             # Send training complete (87% accuracy)"
        echo "  $0 prediction 'Race 5' 'Thunder Bolt' 85 9  # High-value prediction alert"
        echo "  $0 emergency 'Manual Override'           # Send emergency stop"
        exit 1
        ;;
esac
