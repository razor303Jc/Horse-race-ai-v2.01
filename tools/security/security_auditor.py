#!/usr/bin/env python3
"""
🔒 Horse Racing AI v2.0 - Security Audit Tool
===========================================

Comprehensive security auditing and vulnerability assessment.
Checks for common security issues and provides recommendations.

Features:
- Environment variable security audit
- File permission analysis
- Docker container security assessment
- Database security configuration
- Network security checks
- Code vulnerability scanning
- NTFY notification for security alerts

Author: AI Assistant
Date: August 11, 2025
"""

import json
import logging
import os
import stat
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityFinding:
    """Represents a security finding or vulnerability."""

    severity: str  # critical, high, medium, low, info
    category: str  # permissions, credentials, network, etc.
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None


class SecurityAuditor:
    """Comprehensive security auditing tool."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.reports_dir = self.project_root / "reports" / "security"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # NTFY configuration
        self.ntfy_enabled = os.getenv("NTFY_ENABLED", "true").lower() == "true"
        self.ntfy_url = os.getenv("NTFY_URL", "http://localhost:8081")
        self.ntfy_topic = os.getenv("NTFY_TOPIC", "horse-racing-alerts")

        # Security patterns to check
        self.dangerous_patterns = [
            # Hardcoded secrets
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            # SQL injection patterns
            r"execute\s*\(\s*f['\"].*\{.*\}.*['\"]",
            r"\.format\s*\(.*\)",
            # Command injection
            r"subprocess\.(call|run|Popen).*shell\s*=\s*True",
            r"os\.system\s*\(",
            # Insecure functions
            r"eval\s*\(",
            r"exec\s*\(",
        ]

        self.sensitive_files = [
            ".env",
            ".env.local",
            ".env.production",
            "config.json",
            "credentials.json",
            "docker-compose.yml",
            "*.key",
            "*.pem",
            "*.p12",
        ]

    def audit_environment_variables(self) -> List[SecurityFinding]:
        """Audit environment variables for security issues."""
        findings = []

        try:
            env_file = self.project_root / ".env"
            if env_file.exists():
                # Check file permissions
                file_stat = env_file.stat()
                file_mode = stat.filemode(file_stat.st_mode)

                if file_stat.st_mode & stat.S_IROTH or file_stat.st_mode & stat.S_IWOTH:
                    findings.append(
                        SecurityFinding(
                            severity="high",
                            category="permissions",
                            title=".env file has world-readable permissions",
                            description=f".env file permissions: {file_mode}",
                            file_path=str(env_file),
                            recommendation="Run: chmod 600 .env",
                        )
                    )

                # Check for weak passwords
                with open(env_file, "r") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            if "password" in key.lower() or "secret" in key.lower():
                                if len(value) < 12:
                                    findings.append(
                                        SecurityFinding(
                                            severity="medium",
                                            category="credentials",
                                            title="Weak password detected",
                                            description=f"Password for {key} is less than 12 characters",
                                            file_path=str(env_file),
                                            line_number=line_num,
                                            recommendation="Use passwords with at least 12 characters",
                                        )
                                    )

                                if value in ["password", "123456", "admin", "root"]:
                                    findings.append(
                                        SecurityFinding(
                                            severity="critical",
                                            category="credentials",
                                            title="Default/weak password detected",
                                            description=f"Default password found for {key}",
                                            file_path=str(env_file),
                                            line_number=line_num,
                                            recommendation="Change to a strong, unique password",
                                        )
                                    )

        except Exception as e:
            logger.error(f"Environment audit failed: {e}")
            findings.append(
                SecurityFinding(
                    severity="info",
                    category="audit",
                    title="Environment audit failed",
                    description=str(e),
                    recommendation="Check .env file accessibility",
                )
            )

        return findings

    def audit_file_permissions(self) -> List[SecurityFinding]:
        """Audit critical file permissions."""
        findings = []

        critical_files = [
            "docker-compose.yml",
            "requirements.txt",
            "pyproject.toml",
        ]

        try:
            for file_pattern in self.sensitive_files:
                for file_path in self.project_root.glob(file_pattern):
                    if file_path.is_file():
                        file_stat = file_path.stat()

                        # Check if world-writable
                        if file_stat.st_mode & stat.S_IWOTH:
                            findings.append(
                                SecurityFinding(
                                    severity="high",
                                    category="permissions",
                                    title="Sensitive file is world-writable",
                                    description=f"File {file_path.name} has world-write permissions",
                                    file_path=str(file_path),
                                    recommendation=f"Run: chmod o-w {file_path}",
                                )
                            )

            # Check script permissions
            for script in self.project_root.rglob("*.py"):
                if script.is_file():
                    file_stat = script.stat()
                    if (
                        file_stat.st_mode & stat.S_ISUID
                        or file_stat.st_mode & stat.S_ISGID
                    ):
                        findings.append(
                            SecurityFinding(
                                severity="high",
                                category="permissions",
                                title="Python script has setuid/setgid permissions",
                                description=f"Script {script} has dangerous permissions",
                                file_path=str(script),
                                recommendation="Remove setuid/setgid: chmod -s",
                            )
                        )

        except Exception as e:
            logger.error(f"File permissions audit failed: {e}")

        return findings

    def audit_docker_security(self) -> List[SecurityFinding]:
        """Audit Docker configuration for security issues."""
        findings = []

        try:
            # Check docker-compose files
            for compose_file in self.project_root.glob("docker-compose*.yml"):
                with open(compose_file, "r") as f:
                    content = f.read()

                    # Check for privileged mode
                    if "privileged: true" in content:
                        findings.append(
                            SecurityFinding(
                                severity="high",
                                category="docker",
                                title="Container running in privileged mode",
                                description="Privileged containers have access to host system",
                                file_path=str(compose_file),
                                recommendation="Remove privileged: true unless absolutely necessary",
                            )
                        )

                    # Check for host network mode
                    if "network_mode: host" in content:
                        findings.append(
                            SecurityFinding(
                                severity="medium",
                                category="docker",
                                title="Container using host network",
                                description="Host network mode bypasses Docker network isolation",
                                file_path=str(compose_file),
                                recommendation="Use bridge networks instead of host mode",
                            )
                        )

                    # Check for volume mounts to sensitive paths
                    sensitive_mounts = ["/", "/etc", "/usr", "/var"]
                    for mount in sensitive_mounts:
                        if f"- {mount}:" in content or f"- {mount}/" in content:
                            findings.append(
                                SecurityFinding(
                                    severity="high",
                                    category="docker",
                                    title="Sensitive host path mounted",
                                    description=f"Container mounts sensitive path: {mount}",
                                    file_path=str(compose_file),
                                    recommendation="Limit volume mounts to specific directories",
                                )
                            )

            # Check running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        name, image = line.split("\t")
                        # Check for latest tag usage
                        if ":latest" in image or ":" not in image:
                            findings.append(
                                SecurityFinding(
                                    severity="low",
                                    category="docker",
                                    title="Container using 'latest' tag",
                                    description=f"Container {name} uses unspecific image version",
                                    recommendation="Pin to specific image versions",
                                )
                            )

        except Exception as e:
            logger.error(f"Docker security audit failed: {e}")

        return findings

    def audit_database_security(self) -> List[SecurityFinding]:
        """Audit database security configuration."""
        findings = []

        try:
            # Check database connection security
            import psycopg2

            config = {
                "host": "localhost",
                "port": 5432,
                "database": "horse_racing_db",
                "user": "horse_racing",
                "password": os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
            }

            conn = psycopg2.connect(**config, connect_timeout=10)
            cursor = conn.cursor()

            # Check for default passwords
            if config["password"] in ["password", "postgres", "admin"]:
                findings.append(
                    SecurityFinding(
                        severity="critical",
                        category="database",
                        title="Database using default password",
                        description="Database has weak/default password",
                        recommendation="Change to a strong password",
                    )
                )

            # Check user privileges
            cursor.execute(
                """
                SELECT rolname, rolsuper, rolcreaterole, rolcreatedb 
                FROM pg_roles 
                WHERE rolname = %s
            """,
                (config["user"],),
            )

            user_info = cursor.fetchone()
            if user_info and user_info[1]:  # rolsuper
                findings.append(
                    SecurityFinding(
                        severity="medium",
                        category="database",
                        title="Database user has superuser privileges",
                        description="Application user should not have superuser privileges",
                        recommendation="Create restricted user for application",
                    )
                )

            # Check for unencrypted connections
            cursor.execute("SHOW ssl")
            ssl_status = cursor.fetchone()[0]
            if ssl_status == "off":
                findings.append(
                    SecurityFinding(
                        severity="medium",
                        category="database",
                        title="Database SSL disabled",
                        description="Database connections are not encrypted",
                        recommendation="Enable SSL for database connections",
                    )
                )

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Database security audit failed: {e}")

        return findings

    def audit_network_security(self) -> List[SecurityFinding]:
        """Audit network security configuration."""
        findings = []

        try:
            # Check open ports
            result = subprocess.run(
                ["netstat", "-tuln"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "LISTEN" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            if address.startswith("0.0.0.0:"):
                                port = address.split(":")[1]
                                if port not in [
                                    "22",
                                    "80",
                                    "443",
                                    "8000",
                                    "8081",
                                    "5433",
                                    "6380",
                                ]:
                                    findings.append(
                                        SecurityFinding(
                                            severity="low",
                                            category="network",
                                            title="Unexpected port listening on all interfaces",
                                            description=f"Port {port} is listening on 0.0.0.0",
                                            recommendation="Restrict to localhost if not needed externally",
                                        )
                                    )

            # Check firewall status
            try:
                result = subprocess.run(
                    ["ufw", "status"], capture_output=True, text=True, timeout=5
                )
                if "Status: inactive" in result.stdout:
                    findings.append(
                        SecurityFinding(
                            severity="medium",
                            category="network",
                            title="Firewall is disabled",
                            description="UFW firewall is not active",
                            recommendation="Enable firewall: sudo ufw enable",
                        )
                    )
            except:
                pass  # UFW might not be installed

        except Exception as e:
            logger.error(f"Network security audit failed: {e}")

        return findings

    def audit_code_security(self) -> List[SecurityFinding]:
        """Audit code for security vulnerabilities."""
        findings = []

        try:
            import re

            # Check Python files for security patterns
            for py_file in self.project_root.rglob("*.py"):
                if py_file.is_file() and not str(py_file).startswith(
                    str(self.project_root / ".venv")
                ):
                    try:
                        with open(py_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                            for pattern in self.dangerous_patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    line_num = content[: match.start()].count("\n") + 1
                                    findings.append(
                                        SecurityFinding(
                                            severity="medium",
                                            category="code",
                                            title="Potentially dangerous code pattern",
                                            description=f"Pattern '{pattern}' found",
                                            file_path=str(py_file),
                                            line_number=line_num,
                                            recommendation="Review and secure this code",
                                        )
                                    )

                            # Check for hardcoded IPs
                            ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
                            for line_num, line in enumerate(lines, 1):
                                if (
                                    re.search(ip_pattern, line)
                                    and "localhost" not in line
                                    and "127.0.0.1" not in line
                                ):
                                    findings.append(
                                        SecurityFinding(
                                            severity="low",
                                            category="code",
                                            title="Hardcoded IP address",
                                            description="IP address found in code",
                                            file_path=str(py_file),
                                            line_number=line_num,
                                            recommendation="Use configuration variables",
                                        )
                                    )

                    except Exception as e:
                        logger.warning(f"Could not scan {py_file}: {e}")

        except Exception as e:
            logger.error(f"Code security audit failed: {e}")

        return findings

    def send_security_alert(self, finding: SecurityFinding):
        """Send NTFY alert for security findings."""
        if not self.ntfy_enabled or finding.severity == "info":
            return

        try:
            severity_emoji = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "⚡",
                "low": "💡",
            }

            title = f"{severity_emoji.get(finding.severity, '🔍')} Security: {finding.title}"
            message = f"Severity: {finding.severity.upper()}\nCategory: {finding.category}\n\n{finding.description}"

            if finding.file_path:
                message += f"\nFile: {finding.file_path}"
            if finding.line_number:
                message += f"\nLine: {finding.line_number}"
            if finding.recommendation:
                message += f"\nRecommendation: {finding.recommendation}"

            priority = "high" if finding.severity in ["critical", "high"] else "default"

            headers = {
                "Title": title,
                "Priority": priority,
                "Tags": f"security,{finding.category},{finding.severity}",
            }

            url = f"{self.ntfy_url}/{self.ntfy_topic}"
            response = requests.post(url, data=message, headers=headers, timeout=5)

            if response.status_code == 200:
                logger.info(f"Security alert sent: {finding.title}")

        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security audit report."""
        logger.info("🔒 Starting security audit...")

        all_findings = []

        # Run all audits
        all_findings.extend(self.audit_environment_variables())
        all_findings.extend(self.audit_file_permissions())
        all_findings.extend(self.audit_docker_security())
        all_findings.extend(self.audit_database_security())
        all_findings.extend(self.audit_network_security())
        all_findings.extend(self.audit_code_security())

        # Categorize findings by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in all_findings:
            severity_counts[finding.severity] += 1

        # Send alerts for critical/high findings
        for finding in all_findings:
            if finding.severity in ["critical", "high"]:
                self.send_security_alert(finding)

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "audit_summary": {
                "total_findings": len(all_findings),
                "critical_findings": severity_counts["critical"],
                "high_findings": severity_counts["high"],
                "medium_findings": severity_counts["medium"],
                "low_findings": severity_counts["low"],
                "info_findings": severity_counts["info"],
            },
            "security_score": self._calculate_security_score(severity_counts),
            "findings": [
                {
                    "severity": finding.severity,
                    "category": finding.category,
                    "title": finding.title,
                    "description": finding.description,
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "recommendation": finding.recommendation,
                }
                for finding in all_findings
            ],
        }

        # Save report
        report_file = (
            self.reports_dir
            / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Security audit completed. Report saved: {report_file}")
        logger.info(f"Security score: {report['security_score']}/100")
        logger.info(
            f"Findings: {len(all_findings)} total, {severity_counts['critical']} critical, {severity_counts['high']} high"
        )

        return report

    def _calculate_security_score(self, severity_counts: Dict[str, int]) -> int:
        """Calculate security score based on findings."""
        base_score = 100

        # Deduct points based on severity
        deductions = {"critical": 25, "high": 15, "medium": 5, "low": 2, "info": 0}

        for severity, count in severity_counts.items():
            base_score -= deductions[severity] * count

        return max(0, base_score)

    def generate_html_report(self, report: Dict) -> Path:
        """Generate HTML security report."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Audit Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .score-card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .score { font-size: 3em; font-weight: bold; color: {score_color}; }
        .severity-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .severity-card { background: white; padding: 15px; border-radius: 8px; text-align: center; }
        .severity-critical { border-left: 5px solid #e74c3c; }
        .severity-high { border-left: 5px solid #f39c12; }
        .severity-medium { border-left: 5px solid #f1c40f; }
        .severity-low { border-left: 5px solid #3498db; }
        .severity-info { border-left: 5px solid #95a5a6; }
        .finding { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 5px solid #bdc3c7; }
        .finding-critical { border-left-color: #e74c3c; }
        .finding-high { border-left-color: #f39c12; }
        .finding-medium { border-left-color: #f1c40f; }
        .finding-low { border-left-color: #3498db; }
        .finding-title { font-weight: bold; margin-bottom: 5px; }
        .finding-category { color: #7f8c8d; font-size: 0.9em; }
        .finding-description { margin: 10px 0; }
        .finding-recommendation { background: #ecf0f1; padding: 10px; border-radius: 4px; margin-top: 10px; }
        .finding-location { color: #7f8c8d; font-size: 0.9em; font-family: monospace; }
        .timestamp { color: #bdc3c7; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Audit Report</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>
        
        <div class="score-card">
            <div class="score">{security_score}/100</div>
            <h3>Security Score</h3>
        </div>
        
        <div class="severity-grid">
            <div class="severity-card severity-critical">
                <h3>{critical_findings}</h3>
                <p>Critical</p>
            </div>
            <div class="severity-card severity-high">
                <h3>{high_findings}</h3>
                <p>High</p>
            </div>
            <div class="severity-card severity-medium">
                <h3>{medium_findings}</h3>
                <p>Medium</p>
            </div>
            <div class="severity-card severity-low">
                <h3>{low_findings}</h3>
                <p>Low</p>
            </div>
        </div>
        
        <div class="findings-section">
            <h2>Findings</h2>
            {findings_html}
        </div>
    </div>
</body>
</html>
        """

        # Generate findings HTML
        findings_html = ""
        for finding in report["findings"]:
            location_info = ""
            if finding["file_path"]:
                location_info = (
                    f"<div class='finding-location'>File: {finding['file_path']}"
                )
                if finding["line_number"]:
                    location_info += f" (Line {finding['line_number']})"
                location_info += "</div>"

            recommendation_html = ""
            if finding["recommendation"]:
                recommendation_html = f"<div class='finding-recommendation'><strong>Recommendation:</strong> {finding['recommendation']}</div>"

            findings_html += f"""
            <div class="finding finding-{finding['severity']}">
                <div class="finding-title">{finding['title']}</div>
                <div class="finding-category">Category: {finding['category']} | Severity: {finding['severity'].upper()}</div>
                <div class="finding-description">{finding['description']}</div>
                {location_info}
                {recommendation_html}
            </div>
            """

        # Score color
        score = report["security_score"]
        if score >= 80:
            score_color = "#27ae60"
        elif score >= 60:
            score_color = "#f39c12"
        else:
            score_color = "#e74c3c"

        # Fill template
        html_content = html_template.format(
            timestamp=report["timestamp"],
            security_score=report["security_score"],
            score_color=score_color,
            critical_findings=report["audit_summary"]["critical_findings"],
            high_findings=report["audit_summary"]["high_findings"],
            medium_findings=report["audit_summary"]["medium_findings"],
            low_findings=report["audit_summary"]["low_findings"],
            findings_html=findings_html,
        )

        # Save HTML report
        html_file = (
            self.reports_dir
            / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        with open(html_file, "w") as f:
            f.write(html_content)

        # Also save as latest
        latest_file = self.reports_dir / "latest_security_report.html"
        with open(latest_file, "w") as f:
            f.write(html_content)

        logger.info(f"HTML security report saved: {html_file}")
        return html_file


def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Security Audit Tool")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument(
        "--alerts", action="store_true", help="Send NTFY alerts for findings"
    )

    args = parser.parse_args()

    auditor = SecurityAuditor()
    report = auditor.generate_security_report()

    if args.html:
        html_file = auditor.generate_html_report(report)
        print(f"📊 HTML report generated: {html_file}")
        print(f"🌐 View at: file://{html_file.absolute()}")

    print(f"\n🔒 Security Audit Summary:")
    print(f"Score: {report['security_score']}/100")
    print(f"Total Findings: {report['audit_summary']['total_findings']}")
    print(f"Critical: {report['audit_summary']['critical_findings']}")
    print(f"High: {report['audit_summary']['high_findings']}")
    print(f"Medium: {report['audit_summary']['medium_findings']}")
    print(f"Low: {report['audit_summary']['low_findings']}")


if __name__ == "__main__":
    main()
