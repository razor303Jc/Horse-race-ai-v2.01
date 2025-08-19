#!/usr/bin/env python3
"""
Comprehensive Audit Logging System for Horse Racing AI V2.03
Provides detailed audit trails, compliance tracking, and security monitoring
"""

import os
import json
import time
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import threading
from queue import Queue, Empty
import gzip
import socket
import getpass
from enum import Enum
import psutil


class AuditEventType(Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    API_REQUEST = "api_request"
    PREDICTION_GENERATED = "prediction_generated"
    BET_PLACED = "bet_placed"
    BET_RESULT = "bet_result"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    ERROR_OCCURRED = "error_occurred"
    SECURITY_ALERT = "security_alert"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    CONFIGURATION_CHANGE = "configuration_change"
    MODEL_TRAINING = "model_training"
    MODEL_DEPLOYMENT = "model_deployment"


class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    details: Dict[str, Any]
    result: str  # success, failure, error
    error_message: Optional[str]
    system_info: Dict[str, Any]
    compliance_tags: List[str]
    checksum: Optional[str] = None


@dataclass
class ComplianceRequirement:
    """Compliance requirement configuration"""
    name: str
    description: str
    retention_days: int
    event_types: List[AuditEventType]
    required_fields: List[str]
    encryption_required: bool
    real_time_monitoring: bool


class AuditEventHasher:
    """Generates tamper-proof hashes for audit events"""
    
    @staticmethod
    def generate_event_hash(event: AuditEvent) -> str:
        """Generate SHA-256 hash of audit event"""
        # Create a canonical representation of the event
        event_data = {
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type.value,
            'severity': event.severity.value,
            'user_id': event.user_id,
            'session_id': event.session_id,
            'source_ip': event.source_ip,
            'resource': event.resource,
            'action': event.action,
            'details': event.details,
            'result': event.result
        }
        
        # Sort keys for consistent hashing
        canonical_json = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA-256 hash
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


class AuditStorage:
    """Abstract base class for audit storage backends"""
    
    def store_event(self, event: AuditEvent) -> bool:
        raise NotImplementedError
    
    def query_events(self, filters: Dict[str, Any], limit: int = 1000) -> List[AuditEvent]:
        raise NotImplementedError
    
    def get_event_count(self, filters: Dict[str, Any]) -> int:
        raise NotImplementedError
    
    def cleanup_old_events(self, retention_days: int) -> int:
        raise NotImplementedError


class SQLiteAuditStorage(AuditStorage):
    """SQLite-based audit storage"""
    
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize audit database schema"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    source_ip TEXT,
                    user_agent TEXT,
                    resource TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    result TEXT NOT NULL,
                    error_message TEXT,
                    system_info TEXT,
                    compliance_tags TEXT,
                    checksum TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for common queries
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)')
            
            conn.commit()
    
    def store_event(self, event: AuditEvent) -> bool:
        """Store audit event in SQLite database"""
        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    conn.execute('''
                        INSERT INTO audit_events (
                            event_id, timestamp, event_type, severity, user_id,
                            session_id, source_ip, user_agent, resource, action,
                            details, result, error_message, system_info,
                            compliance_tags, checksum
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event.event_id,
                        event.timestamp.isoformat(),
                        event.event_type.value,
                        event.severity.value,
                        event.user_id,
                        event.session_id,
                        event.source_ip,
                        event.user_agent,
                        event.resource,
                        event.action,
                        json.dumps(event.details),
                        event.result,
                        event.error_message,
                        json.dumps(event.system_info),
                        json.dumps(event.compliance_tags),
                        event.checksum
                    ))
                    conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error storing audit event: {e}")
            return False
    
    def query_events(self, filters: Dict[str, Any], limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filters"""
        try:
            where_clauses = []
            params = []
            
            # Build WHERE clause from filters
            if 'start_date' in filters:
                where_clauses.append('timestamp >= ?')
                params.append(filters['start_date'])
            
            if 'end_date' in filters:
                where_clauses.append('timestamp <= ?')
                params.append(filters['end_date'])
            
            if 'event_type' in filters:
                where_clauses.append('event_type = ?')
                params.append(filters['event_type'])
            
            if 'user_id' in filters:
                where_clauses.append('user_id = ?')
                params.append(filters['user_id'])
            
            if 'severity' in filters:
                where_clauses.append('severity = ?')
                params.append(filters['severity'])
            
            # Construct query
            query = 'SELECT * FROM audit_events'
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    events.append(self._row_to_event(row))
                
                return events
                
        except Exception as e:
            logging.error(f"Error querying audit events: {e}")
            return []
    
    def get_event_count(self, filters: Dict[str, Any]) -> int:
        """Get count of audit events matching filters"""
        try:
            where_clauses = []
            params = []
            
            # Build WHERE clause (same logic as query_events)
            if 'start_date' in filters:
                where_clauses.append('timestamp >= ?')
                params.append(filters['start_date'])
            
            if 'end_date' in filters:
                where_clauses.append('timestamp <= ?')
                params.append(filters['end_date'])
            
            if 'event_type' in filters:
                where_clauses.append('event_type = ?')
                params.append(filters['event_type'])
            
            # Construct query
            query = 'SELECT COUNT(*) FROM audit_events'
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute(query, params)
                return cursor.fetchone()[0]
                
        except Exception as e:
            logging.error(f"Error counting audit events: {e}")
            return 0
    
    def cleanup_old_events(self, retention_days: int) -> int:
        """Clean up old audit events"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
            
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.execute('DELETE FROM audit_events WHERE timestamp < ?', (cutoff_date,))
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
            return deleted_count
            
        except Exception as e:
            logging.error(f"Error cleaning up old events: {e}")
            return 0
    
    def _row_to_event(self, row: sqlite3.Row) -> AuditEvent:
        """Convert database row to AuditEvent"""
        return AuditEvent(
            event_id=row['event_id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            event_type=AuditEventType(row['event_type']),
            severity=AuditSeverity(row['severity']),
            user_id=row['user_id'],
            session_id=row['session_id'],
            source_ip=row['source_ip'],
            user_agent=row['user_agent'],
            resource=row['resource'],
            action=row['action'],
            details=json.loads(row['details']) if row['details'] else {},
            result=row['result'],
            error_message=row['error_message'],
            system_info=json.loads(row['system_info']) if row['system_info'] else {},
            compliance_tags=json.loads(row['compliance_tags']) if row['compliance_tags'] else [],
            checksum=row['checksum']
        )


class AuditEventProcessor:
    """Processes and enriches audit events"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enrich_event(self, event: AuditEvent) -> AuditEvent:
        """Enrich audit event with system information"""
        # Add system information
        event.system_info.update({
            'hostname': socket.gethostname(),
            'platform': os.name,
            'python_version': os.sys.version,
            'process_id': os.getpid(),
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent
        })
        
        # Generate checksum for tamper detection
        event.checksum = AuditEventHasher.generate_event_hash(event)
        
        return event
    
    def validate_event(self, event: AuditEvent) -> bool:
        """Validate audit event integrity"""
        if not event.checksum:
            return False
        
        # Recalculate checksum
        expected_checksum = AuditEventHasher.generate_event_hash(event)
        return event.checksum == expected_checksum


class ComplianceManager:
    """Manages compliance requirements and reporting"""
    
    def __init__(self):
        self.requirements = self._load_compliance_requirements()
        self.logger = logging.getLogger(__name__)
    
    def _load_compliance_requirements(self) -> Dict[str, ComplianceRequirement]:
        """Load compliance requirements"""
        return {
            'gdpr': ComplianceRequirement(
                name='GDPR',
                description='General Data Protection Regulation',
                retention_days=2555,  # 7 years
                event_types=[
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.DATA_MODIFICATION,
                    AuditEventType.DATA_EXPORT,
                    AuditEventType.DATA_IMPORT
                ],
                required_fields=['user_id', 'resource', 'action', 'timestamp'],
                encryption_required=True,
                real_time_monitoring=True
            ),
            'financial_conduct': ComplianceRequirement(
                name='Financial Conduct',
                description='Financial services compliance',
                retention_days=2555,  # 7 years
                event_types=[
                    AuditEventType.BET_PLACED,
                    AuditEventType.BET_RESULT,
                    AuditEventType.PREDICTION_GENERATED
                ],
                required_fields=['user_id', 'action', 'details', 'timestamp'],
                encryption_required=True,
                real_time_monitoring=True
            ),
            'data_protection': ComplianceRequirement(
                name='Data Protection',
                description='Data protection and privacy',
                retention_days=1825,  # 5 years
                event_types=[
                    AuditEventType.USER_LOGIN,
                    AuditEventType.DATA_ACCESS,
                    AuditEventType.SECURITY_ALERT
                ],
                required_fields=['user_id', 'source_ip', 'timestamp'],
                encryption_required=False,
                real_time_monitoring=True
            )
        }
    
    def check_compliance(self, event: AuditEvent) -> List[str]:
        """Check if event meets compliance requirements"""
        compliance_issues = []
        
        for req_name, requirement in self.requirements.items():
            if event.event_type in requirement.event_types:
                # Check required fields
                for field in requirement.required_fields:
                    field_value = getattr(event, field, None)
                    if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
                        compliance_issues.append(f"{req_name}: Missing required field '{field}'")
                
                # Add compliance tag
                if req_name not in event.compliance_tags:
                    event.compliance_tags.append(req_name)
        
        return compliance_issues


class ComprehensiveAuditLogger:
    """Main audit logging system"""
    
    def __init__(self, storage_backend: AuditStorage, 
                 async_processing: bool = True):
        self.storage = storage_backend
        self.processor = AuditEventProcessor()
        self.compliance_manager = ComplianceManager()
        self.logger = logging.getLogger(__name__)
        
        # Async processing setup
        self.async_processing = async_processing
        if async_processing:
            self.event_queue = Queue(maxsize=10000)
            self.processing_thread = threading.Thread(target=self._process_events_async, daemon=True)
            self.processing_thread.start()
    
    def log_event(self, event_type: AuditEventType, action: str,
                  user_id: Optional[str] = None, session_id: Optional[str] = None,
                  source_ip: Optional[str] = None, user_agent: Optional[str] = None,
                  resource: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                  result: str = 'success', error_message: Optional[str] = None,
                  severity: AuditSeverity = AuditSeverity.MEDIUM) -> bool:
        """Log an audit event"""
        
        # Create audit event
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            user_id=user_id or self._get_current_user(),
            session_id=session_id,
            source_ip=source_ip or self._get_local_ip(),
            user_agent=user_agent,
            resource=resource,
            action=action,
            details=details or {},
            result=result,
            error_message=error_message,
            system_info={},
            compliance_tags=[]
        )
        
        # Enrich event
        event = self.processor.enrich_event(event)
        
        # Check compliance
        compliance_issues = self.compliance_manager.check_compliance(event)
        if compliance_issues:
            self.logger.warning(f"Compliance issues for event {event.event_id}: {compliance_issues}")
        
        # Store event
        if self.async_processing:
            try:
                self.event_queue.put_nowait(event)
                return True
            except:
                # Fallback to synchronous processing
                return self.storage.store_event(event)
        else:
            return self.storage.store_event(event)
    
    def log_user_login(self, user_id: str, source_ip: str, user_agent: str,
                      success: bool = True, error_message: Optional[str] = None):
        """Log user login event"""
        self.log_event(
            event_type=AuditEventType.USER_LOGIN,
            action='user_login',
            user_id=user_id,
            source_ip=source_ip,
            user_agent=user_agent,
            result='success' if success else 'failure',
            error_message=error_message,
            severity=AuditSeverity.MEDIUM
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str,
                       details: Optional[Dict[str, Any]] = None):
        """Log data access event"""
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action=action,
            user_id=user_id,
            resource=resource,
            details=details,
            severity=AuditSeverity.LOW
        )
    
    def log_prediction_generated(self, user_id: str, race_id: str, 
                               prediction_details: Dict[str, Any]):
        """Log ML prediction generation"""
        self.log_event(
            event_type=AuditEventType.PREDICTION_GENERATED,
            action='generate_prediction',
            user_id=user_id,
            resource=f'race:{race_id}',
            details=prediction_details,
            severity=AuditSeverity.MEDIUM
        )
    
    def log_bet_placed(self, user_id: str, bet_details: Dict[str, Any]):
        """Log betting event"""
        self.log_event(
            event_type=AuditEventType.BET_PLACED,
            action='place_bet',
            user_id=user_id,
            resource=f"race:{bet_details.get('race_id', 'unknown')}",
            details=bet_details,
            severity=AuditSeverity.HIGH
        )
    
    def log_security_alert(self, alert_type: str, details: Dict[str, Any],
                          user_id: Optional[str] = None, source_ip: Optional[str] = None):
        """Log security alert"""
        self.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            action=alert_type,
            user_id=user_id,
            source_ip=source_ip,
            details=details,
            severity=AuditSeverity.CRITICAL
        )
    
    def log_api_request(self, endpoint: str, method: str, user_id: str,
                       source_ip: str, response_code: int,
                       request_details: Optional[Dict[str, Any]] = None):
        """Log API request"""
        self.log_event(
            event_type=AuditEventType.API_REQUEST,
            action=f'{method} {endpoint}',
            user_id=user_id,
            source_ip=source_ip,
            resource=endpoint,
            details={
                'method': method,
                'response_code': response_code,
                'request_details': request_details
            },
            result='success' if 200 <= response_code < 400 else 'failure',
            severity=AuditSeverity.LOW
        )
    
    def query_events(self, filters: Dict[str, Any], limit: int = 1000) -> List[AuditEvent]:
        """Query audit events"""
        return self.storage.query_events(filters, limit)
    
    def generate_compliance_report(self, compliance_type: str, 
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report"""
        filters = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        # Get relevant events
        requirement = self.compliance_manager.requirements.get(compliance_type)
        if not requirement:
            return {'error': f'Unknown compliance type: {compliance_type}'}
        
        all_events = self.storage.query_events(filters, limit=10000)
        relevant_events = [e for e in all_events if e.event_type in requirement.event_types]
        
        # Generate report
        report = {
            'compliance_type': compliance_type,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': len(relevant_events),
            'event_breakdown': {},
            'compliance_issues': [],
            'top_users': {},
            'summary': {}
        }
        
        # Event breakdown by type
        for event in relevant_events:
            event_type = event.event_type.value
            report['event_breakdown'][event_type] = report['event_breakdown'].get(event_type, 0) + 1
        
        # Top users by activity
        user_counts = {}
        for event in relevant_events:
            if event.user_id:
                user_counts[event.user_id] = user_counts.get(event.user_id, 0) + 1
        
        report['top_users'] = dict(sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return report
    
    def _process_events_async(self):
        """Async event processing worker"""
        while True:
            try:
                event = self.event_queue.get(timeout=1)
                self.storage.store_event(event)
                self.event_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing async event: {e}")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_current_user(self) -> str:
        """Get current system user"""
        return getpass.getuser()
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"


def main():
    """Main execution function"""
    print("📋 Horse Racing AI V2.03 - Comprehensive Audit Logging System")
    print("=" * 70)
    
    # Initialize audit logger
    storage = SQLiteAuditStorage("logs/audit.db")
    audit_logger = ComprehensiveAuditLogger(storage)
    
    print("\n📊 Testing Audit Logging:")
    
    # Test various audit events
    test_events = [
        ("User Login", lambda: audit_logger.log_user_login(
            "test_user", "192.168.1.100", "Mozilla/5.0 Browser")),
        ("Data Access", lambda: audit_logger.log_data_access(
            "test_user", "horses_table", "SELECT * FROM horses")),
        ("Prediction Generated", lambda: audit_logger.log_prediction_generated(
            "test_user", "20241201_NEW_1", {"horse": "Thunder Bolt", "confidence": 0.85})),
        ("Bet Placed", lambda: audit_logger.log_bet_placed(
            "test_user", {"race_id": "20241201_NEW_1", "horse": "Thunder Bolt", "stake": 10.0})),
        ("Security Alert", lambda: audit_logger.log_security_alert(
            "failed_login_attempts", {"attempts": 5, "ip": "192.168.1.100"})),
        ("API Request", lambda: audit_logger.log_api_request(
            "/api/predictions", "POST", "test_user", "192.168.1.100", 200))
    ]
    
    for event_name, event_func in test_events:
        success = event_func()
        print(f"  {'✅' if success else '❌'} {event_name}: {'Logged' if success else 'Failed'}")
    
    # Query events
    print(f"\n📋 Querying Recent Events:")
    recent_events = audit_logger.query_events({}, limit=5)
    print(f"  📊 Found {len(recent_events)} recent events")
    
    for event in recent_events:
        print(f"    - {event.timestamp.strftime('%H:%M:%S')} | "
              f"{event.event_type.value} | {event.action} | {event.user_id}")
    
    # Generate compliance report
    print(f"\n📈 Generating Compliance Report:")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    report = audit_logger.generate_compliance_report('gdpr', start_date, end_date)
    print(f"  📊 GDPR Compliance Report (Last 7 days):")
    print(f"    - Total Events: {report.get('total_events', 0)}")
    print(f"    - Event Types: {len(report.get('event_breakdown', {}))}")
    print(f"    - Active Users: {len(report.get('top_users', {}))}")
    
    print("\n✅ Audit logging system demonstration completed")


if __name__ == "__main__":
    main()
