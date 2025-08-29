#!/usr/bin/env python3
"""
Comprehensive Input Validation and Sanitization System for Horse Racing AI V2.03
Provides robust input validation, sanitization, and security controls
"""

import re
import html
import json
import uuid
import ipaddress
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass
import logging
from email_validator import validate_email, EmailNotValidError
import bleach
from urllib.parse import urlparse
import sqlparse
from sqlalchemy import text
import phonenumbers


@dataclass
class ValidationRule:
    """Validation rule configuration"""

    field_name: str
    data_type: str
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable] = None
    sanitizer: Optional[Callable] = None


@dataclass
class ValidationResult:
    """Result of validation process"""

    is_valid: bool
    sanitized_data: Dict[str, Any]
    errors: Dict[str, List[str]]
    warnings: Dict[str, List[str]]
    security_flags: List[str]


class SecurityValidator:
    """Security-focused input validation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Common attack patterns
        self.sql_injection_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(or|and)\s+\d+\s*=\s*\d+)",
            r"(\bor\s+\d+\s*>\s*\d+)",
            r"(\';|\";\s*--)",
        ]

        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
        ]

        self.command_injection_patterns = [
            r"[;&|`$\(\)]",
            r"\b(rm|del|format|mkdir|rmdir|mv|cp|cat|type|echo)\b",
            r"(\.\./|\.\.\\",
        ]

    def check_sql_injection(self, value: str) -> List[str]:
        """Check for SQL injection patterns"""
        security_flags = []

        for pattern in self.sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                security_flags.append(f"Potential SQL injection detected: {pattern}")

        return security_flags

    def check_xss(self, value: str) -> List[str]:
        """Check for XSS patterns"""
        security_flags = []

        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                security_flags.append(f"Potential XSS detected: {pattern}")

        return security_flags

    def check_command_injection(self, value: str) -> List[str]:
        """Check for command injection patterns"""
        security_flags = []

        for pattern in self.command_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                security_flags.append(
                    f"Potential command injection detected: {pattern}"
                )

        return security_flags

    def validate_content_length(
        self, content: str, max_length: int = 1000000
    ) -> List[str]:
        """Validate content length to prevent DoS"""
        security_flags = []

        if len(content) > max_length:
            security_flags.append(
                f"Content exceeds maximum length: {len(content)} > {max_length}"
            )

        return security_flags


class DataTypeSanitizer:
    """Data type-specific sanitization"""

    @staticmethod
    def sanitize_string(
        value: str, max_length: Optional[int] = None, allow_html: bool = False
    ) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)

        # Remove null bytes and control characters
        value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

        # Normalize whitespace
        value = " ".join(value.split())

        if not allow_html:
            # Remove HTML tags
            value = bleach.clean(value, tags=[], strip=True)
            # Escape HTML entities
            value = html.escape(value)
        else:
            # Allow safe HTML tags only
            allowed_tags = ["p", "br", "strong", "em", "u", "ol", "ul", "li"]
            value = bleach.clean(value, tags=allowed_tags, strip=True)

        # Truncate if necessary
        if max_length and len(value) > max_length:
            value = value[:max_length]

        return value.strip()

    @staticmethod
    def sanitize_integer(value: Union[str, int, float]) -> Optional[int]:
        """Sanitize integer input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except minus sign
                value = re.sub(r"[^\d\-]", "", value)
            return int(float(value))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_float(value: Union[str, int, float]) -> Optional[float]:
        """Sanitize float input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except minus and decimal point
                value = re.sub(r"[^\d\-\.]", "", value)
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_decimal(value: Union[str, int, float, Decimal]) -> Optional[Decimal]:
        """Sanitize decimal input"""
        try:
            if isinstance(value, str):
                value = re.sub(r"[^\d\-\.]", "", value)
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_boolean(value: Union[str, bool, int]) -> Optional[bool]:
        """Sanitize boolean input"""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.lower().strip()
            if value in ["true", "1", "yes", "on", "enabled"]:
                return True
            elif value in ["false", "0", "no", "off", "disabled"]:
                return False

        if isinstance(value, int):
            return bool(value)

        return None

    @staticmethod
    def sanitize_email(value: str) -> Optional[str]:
        """Sanitize and validate email"""
        try:
            if not isinstance(value, str):
                return None

            value = value.strip().lower()
            # Basic email format validation
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
                return None

            # Use email-validator for thorough validation
            validated_email = validate_email(value)
            return validated_email.email
        except EmailNotValidError:
            return None

    @staticmethod
    def sanitize_url(value: str) -> Optional[str]:
        """Sanitize and validate URL"""
        try:
            if not isinstance(value, str):
                return None

            value = value.strip()

            # Add protocol if missing
            if not value.startswith(("http://", "https://")):
                value = "https://" + value

            parsed = urlparse(value)

            # Validate URL structure
            if not parsed.netloc or not parsed.scheme:
                return None

            # Only allow http/https
            if parsed.scheme not in ["http", "https"]:
                return None

            return value
        except Exception:
            return None

    @staticmethod
    def sanitize_phone(value: str, region: str = "US") -> Optional[str]:
        """Sanitize and validate phone number"""
        try:
            if not isinstance(value, str):
                return None

            # Parse phone number
            phone_number = phonenumbers.parse(value, region)

            # Validate phone number
            if phonenumbers.is_valid_number(phone_number):
                return phonenumbers.format_number(
                    phone_number, phonenumbers.PhoneNumberFormat.E164
                )

            return None
        except phonenumbers.NumberParseException:
            return None

    @staticmethod
    def sanitize_ip_address(value: str) -> Optional[str]:
        """Sanitize and validate IP address"""
        try:
            if not isinstance(value, str):
                return None

            value = value.strip()

            # Validate IP address
            ip = ipaddress.ip_address(value)
            return str(ip)
        except ValueError:
            return None


class BusinessLogicValidator:
    """Business logic validation for Horse Racing AI"""

    @staticmethod
    def validate_race_id(value: str) -> List[str]:
        """Validate race ID format"""
        errors = []

        if not isinstance(value, str):
            errors.append("Race ID must be a string")
            return errors

        # Race ID format: YYYYMMDD_VENUE_RACE_NUMBER
        pattern = r"^\d{8}_[A-Z]{2,10}_\d{1,2}$"
        if not re.match(pattern, value):
            errors.append("Race ID must follow format: YYYYMMDD_VENUE_RACE_NUMBER")

        return errors

    @staticmethod
    def validate_horse_name(value: str) -> List[str]:
        """Validate horse name"""
        errors = []

        if not isinstance(value, str):
            errors.append("Horse name must be a string")
            return errors

        if len(value.strip()) < 2:
            errors.append("Horse name must be at least 2 characters")

        if len(value.strip()) > 50:
            errors.append("Horse name cannot exceed 50 characters")

        # Only allow letters, numbers, spaces, and common punctuation
        if not re.match(r"^[A-Za-z0-9\s\'\-\.]+$", value):
            errors.append("Horse name contains invalid characters")

        return errors

    @staticmethod
    def validate_odds(value: Union[str, float, int]) -> List[str]:
        """Validate betting odds"""
        errors = []

        try:
            odds = float(value)

            if odds <= 0:
                errors.append("Odds must be positive")

            if odds > 1000:
                errors.append("Odds cannot exceed 1000")

        except (ValueError, TypeError):
            errors.append("Odds must be a valid number")

        return errors

    @staticmethod
    def validate_stake(value: Union[str, float, int]) -> List[str]:
        """Validate betting stake"""
        errors = []

        try:
            stake = float(value)

            if stake < 0:
                errors.append("Stake cannot be negative")

            if stake > 10000:
                errors.append("Stake cannot exceed £10,000")

            # Check for reasonable decimal places (pence)
            if round(stake, 2) != stake:
                errors.append("Stake can have maximum 2 decimal places")

        except (ValueError, TypeError):
            errors.append("Stake must be a valid number")

        return errors

    @staticmethod
    def validate_prediction_confidence(value: Union[str, float, int]) -> List[str]:
        """Validate ML prediction confidence"""
        errors = []

        try:
            confidence = float(value)

            if confidence < 0 or confidence > 1:
                errors.append("Prediction confidence must be between 0 and 1")

        except (ValueError, TypeError):
            errors.append("Prediction confidence must be a valid number")

        return errors


class ComprehensiveInputValidator:
    """Main input validation and sanitization system"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_validator = SecurityValidator()
        self.sanitizer = DataTypeSanitizer()
        self.business_validator = BusinessLogicValidator()

        # Common validation rules
        self.common_rules = {
            "string": ValidationRule("string", "string"),
            "integer": ValidationRule("integer", "integer"),
            "float": ValidationRule("float", "float"),
            "boolean": ValidationRule("boolean", "boolean"),
            "email": ValidationRule("email", "email"),
            "url": ValidationRule("url", "url"),
            "phone": ValidationRule("phone", "phone"),
            "ip": ValidationRule("ip", "ip_address"),
        }

    def validate_data(
        self, data: Dict[str, Any], rules: Dict[str, ValidationRule]
    ) -> ValidationResult:
        """Validate data against rules"""
        sanitized_data = {}
        errors = {}
        warnings = {}
        security_flags = []

        # Validate each field
        for field_name, rule in rules.items():
            field_errors = []
            field_warnings = []

            # Check if field is present
            if field_name not in data:
                if rule.required:
                    field_errors.append(f"Field '{field_name}' is required")
                continue

            value = data[field_name]

            # Security checks for string values
            if isinstance(value, str):
                security_flags.extend(
                    self.security_validator.check_sql_injection(value)
                )
                security_flags.extend(self.security_validator.check_xss(value))
                security_flags.extend(
                    self.security_validator.check_command_injection(value)
                )
                security_flags.extend(
                    self.security_validator.validate_content_length(value)
                )

            # Sanitize value
            sanitized_value = self._sanitize_value(value, rule)

            if sanitized_value is None and rule.required:
                field_errors.append(
                    f"Invalid {rule.data_type} value for '{field_name}'"
                )
                continue

            # Validate sanitized value
            field_errors.extend(self._validate_value(sanitized_value, rule))

            # Store sanitized value
            if sanitized_value is not None:
                sanitized_data[field_name] = sanitized_value

            # Store errors and warnings
            if field_errors:
                errors[field_name] = field_errors
            if field_warnings:
                warnings[field_name] = field_warnings

        # Overall validation result
        is_valid = len(errors) == 0 and len(security_flags) == 0

        return ValidationResult(
            is_valid=is_valid,
            sanitized_data=sanitized_data,
            errors=errors,
            warnings=warnings,
            security_flags=security_flags,
        )

    def _sanitize_value(self, value: Any, rule: ValidationRule) -> Any:
        """Sanitize value based on data type"""
        if rule.sanitizer:
            return rule.sanitizer(value)

        if rule.data_type == "string":
            return self.sanitizer.sanitize_string(value, rule.max_length)
        elif rule.data_type == "integer":
            return self.sanitizer.sanitize_integer(value)
        elif rule.data_type == "float":
            return self.sanitizer.sanitize_float(value)
        elif rule.data_type == "decimal":
            return self.sanitizer.sanitize_decimal(value)
        elif rule.data_type == "boolean":
            return self.sanitizer.sanitize_boolean(value)
        elif rule.data_type == "email":
            return self.sanitizer.sanitize_email(value)
        elif rule.data_type == "url":
            return self.sanitizer.sanitize_url(value)
        elif rule.data_type == "phone":
            return self.sanitizer.sanitize_phone(value)
        elif rule.data_type == "ip_address":
            return self.sanitizer.sanitize_ip_address(value)
        else:
            return value

    def _validate_value(self, value: Any, rule: ValidationRule) -> List[str]:
        """Validate value against rule constraints"""
        errors = []

        if value is None:
            return errors

        # Length validation for strings
        if rule.data_type == "string" and isinstance(value, str):
            if rule.min_length and len(value) < rule.min_length:
                errors.append(f"Minimum length is {rule.min_length}")
            if rule.max_length and len(value) > rule.max_length:
                errors.append(f"Maximum length is {rule.max_length}")

        # Range validation for numbers
        if rule.data_type in ["integer", "float", "decimal"] and isinstance(
            value, (int, float, Decimal)
        ):
            if rule.min_value is not None and value < rule.min_value:
                errors.append(f"Minimum value is {rule.min_value}")
            if rule.max_value is not None and value > rule.max_value:
                errors.append(f"Maximum value is {rule.max_value}")

        # Pattern validation
        if rule.pattern and isinstance(value, str):
            if not re.match(rule.pattern, value):
                errors.append(f"Value does not match required pattern: {rule.pattern}")

        # Allowed values validation
        if rule.allowed_values and value not in rule.allowed_values:
            errors.append(f"Value must be one of: {rule.allowed_values}")

        # Custom validation
        if rule.custom_validator:
            try:
                custom_errors = rule.custom_validator(value)
                if custom_errors:
                    errors.extend(custom_errors)
            except Exception as e:
                errors.append(f"Custom validation error: {e}")

        return errors

    def validate_race_data(self, race_data: Dict[str, Any]) -> ValidationResult:
        """Validate race data submission"""
        rules = {
            "race_id": ValidationRule(
                "race_id",
                "string",
                required=True,
                pattern=r"^\d{8}_[A-Z]{2,10}_\d{1,2}$",
                custom_validator=self.business_validator.validate_race_id,
            ),
            "venue": ValidationRule(
                "venue", "string", required=True, min_length=2, max_length=50
            ),
            "race_time": ValidationRule(
                "race_time",
                "string",
                required=True,
                pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            ),
            "distance": ValidationRule(
                "distance", "integer", required=True, min_value=800, max_value=10000
            ),
            "ground_conditions": ValidationRule(
                "ground_conditions",
                "string",
                required=False,
                allowed_values=["firm", "good", "soft", "heavy", "yielding"],
            ),
        }

        return self.validate_data(race_data, rules)

    def validate_horse_data(self, horse_data: Dict[str, Any]) -> ValidationResult:
        """Validate horse data submission"""
        rules = {
            "name": ValidationRule(
                "name",
                "string",
                required=True,
                min_length=2,
                max_length=50,
                custom_validator=self.business_validator.validate_horse_name,
            ),
            "age": ValidationRule(
                "age", "integer", required=True, min_value=2, max_value=15
            ),
            "weight": ValidationRule(
                "weight", "float", required=True, min_value=45.0, max_value=80.0
            ),
            "jockey": ValidationRule(
                "jockey", "string", required=True, min_length=2, max_length=50
            ),
            "trainer": ValidationRule(
                "trainer", "string", required=True, min_length=2, max_length=50
            ),
            "odds": ValidationRule(
                "odds",
                "float",
                required=False,
                custom_validator=self.business_validator.validate_odds,
            ),
        }

        return self.validate_data(horse_data, rules)

    def validate_betting_data(self, betting_data: Dict[str, Any]) -> ValidationResult:
        """Validate betting data submission"""
        rules = {
            "race_id": ValidationRule(
                "race_id",
                "string",
                required=True,
                custom_validator=self.business_validator.validate_race_id,
            ),
            "horse_name": ValidationRule(
                "horse_name",
                "string",
                required=True,
                custom_validator=self.business_validator.validate_horse_name,
            ),
            "bet_type": ValidationRule(
                "bet_type",
                "string",
                required=True,
                allowed_values=["win", "place", "each_way", "forecast", "tricast"],
            ),
            "stake": ValidationRule(
                "stake",
                "float",
                required=True,
                custom_validator=self.business_validator.validate_stake,
            ),
            "odds": ValidationRule(
                "odds",
                "float",
                required=True,
                custom_validator=self.business_validator.validate_odds,
            ),
        }

        return self.validate_data(betting_data, rules)

    def validate_api_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Validate API request data"""
        rules = {
            "endpoint": ValidationRule(
                "endpoint", "string", required=True, pattern=r"^[a-zA-Z0-9/_-]+$"
            ),
            "method": ValidationRule(
                "method",
                "string",
                required=True,
                allowed_values=["GET", "POST", "PUT", "DELETE"],
            ),
            "api_key": ValidationRule(
                "api_key",
                "string",
                required=True,
                min_length=32,
                max_length=64,
                pattern=r"^[a-zA-Z0-9]+$",
            ),
            "timestamp": ValidationRule(
                "timestamp",
                "string",
                required=True,
                pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$",
            ),
        }

        return self.validate_data(request_data, rules)


def main():
    """Main execution function"""
    print("🛡️ Horse Racing AI V2.03 - Comprehensive Input Validation System")
    print("=" * 70)

    validator = ComprehensiveInputValidator()

    # Test race data validation
    print("\n📊 Testing Race Data Validation:")
    race_data = {
        "race_id": "20241201_NEW_1",
        "venue": "Newcastle",
        "race_time": "2024-12-01 14:30:00",
        "distance": 1200,
        "ground_conditions": "good",
    }

    result = validator.validate_race_data(race_data)
    print(f"  {'✅' if result.is_valid else '❌'} Valid: {result.is_valid}")
    if result.errors:
        print(f"  ⚠️ Errors: {result.errors}")
    if result.security_flags:
        print(f"  🚨 Security Flags: {result.security_flags}")

    # Test horse data validation
    print("\n🐎 Testing Horse Data Validation:")
    horse_data = {
        "name": "Thunder Bolt",
        "age": 4,
        "weight": 58.5,
        "jockey": "J. Smith",
        "trainer": "M. Johnson",
        "odds": 3.5,
    }

    result = validator.validate_horse_data(horse_data)
    print(f"  {'✅' if result.is_valid else '❌'} Valid: {result.is_valid}")
    if result.errors:
        print(f"  ⚠️ Errors: {result.errors}")

    # Test security validation
    print("\n🔒 Testing Security Validation:")
    malicious_data = {
        "name": "'; DROP TABLE horses; --",
        "description": '<script>alert("xss")</script>',
        "command": "rm -rf /",
    }

    rules = {
        "name": ValidationRule("name", "string"),
        "description": ValidationRule("description", "string"),
        "command": ValidationRule("command", "string"),
    }

    result = validator.validate_data(malicious_data, rules)
    print(f"  {'✅' if result.is_valid else '❌'} Valid: {result.is_valid}")
    print(f"  🚨 Security Flags: {len(result.security_flags)} detected")
    for flag in result.security_flags[:3]:  # Show first 3
        print(f"    - {flag}")

    print("\n✅ Input validation system demonstration completed")


if __name__ == "__main__":
    main()
