#!/usr/bin/env python3
"""
Comprehensive Secret Management System for Horse Racing AI V2.03
Provides secure handling of API keys, database credentials, and sensitive data
"""

import os
import json
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
import hvac  # HashiCorp Vault client


@dataclass
class SecretMetadata:
    """Metadata for secret management"""

    name: str
    created_at: datetime
    updated_at: datetime
    rotation_period: int  # days
    access_count: int
    last_accessed: Optional[datetime]
    tags: List[str]
    secret_type: str  # 'api_key', 'database', 'certificate', etc.


@dataclass
class SecretRotationPolicy:
    """Secret rotation policy configuration"""

    enabled: bool
    rotation_days: int
    warning_days: int
    auto_rotate: bool
    notification_channels: List[str]


class SecretEncryption:
    """Handles encryption and decryption of secrets"""

    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or self._get_or_create_master_key()
        self.fernet = self._create_fernet()
        self.logger = logging.getLogger(__name__)

    def _get_or_create_master_key(self) -> str:
        """Get or create master encryption key"""
        try:
            # Try to get from environment first
            master_key = os.getenv("HORSE_RACING_AI_MASTER_KEY")
            if master_key:
                return master_key

            # Try to get from keyring
            master_key = keyring.get_password("horse_racing_ai", "master_key")
            if master_key:
                return master_key

            # Generate new master key
            master_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

            # Store in keyring
            keyring.set_password("horse_racing_ai", "master_key", master_key)

            return master_key

        except Exception as e:
            self.logger.error(f"Error handling master key: {e}")
            # Fallback to generated key (less secure)
            return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

    def _create_fernet(self) -> Fernet:
        """Create Fernet encryption instance"""
        # Derive key from master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"horse_racing_ai_salt",  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data)
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise


class SecretStorage:
    """Abstract base for secret storage backends"""

    def store_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        raise NotImplementedError

    def retrieve_secret(self, name: str) -> Optional[str]:
        raise NotImplementedError

    def delete_secret(self, name: str) -> bool:
        raise NotImplementedError

    def list_secrets(self) -> List[str]:
        raise NotImplementedError


class FileSecretStorage(SecretStorage):
    """File-based secret storage with encryption"""

    def __init__(self, storage_path: str, encryption: SecretEncryption):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.encryption = encryption
        self.logger = logging.getLogger(__name__)

        # Secure directory permissions
        os.chmod(self.storage_path, 0o700)

    def store_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        """Store encrypted secret to file"""
        try:
            secret_file = self.storage_path / f"{name}.secret"
            metadata_file = self.storage_path / f"{name}.meta"

            # Encrypt and store secret
            encrypted_value = self.encryption.encrypt(value)
            with open(secret_file, "w") as f:
                f.write(encrypted_value)

            # Store metadata
            with open(metadata_file, "w") as f:
                json.dump(asdict(metadata), f, default=str, indent=2)

            # Secure file permissions
            os.chmod(secret_file, 0o600)
            os.chmod(metadata_file, 0o600)

            return True

        except Exception as e:
            self.logger.error(f"Error storing secret {name}: {e}")
            return False

    def retrieve_secret(self, name: str) -> Optional[str]:
        """Retrieve and decrypt secret from file"""
        try:
            secret_file = self.storage_path / f"{name}.secret"
            if not secret_file.exists():
                return None

            with open(secret_file, "r") as f:
                encrypted_value = f.read().strip()

            return self.encryption.decrypt(encrypted_value)

        except Exception as e:
            self.logger.error(f"Error retrieving secret {name}: {e}")
            return None

    def delete_secret(self, name: str) -> bool:
        """Delete secret and metadata files"""
        try:
            secret_file = self.storage_path / f"{name}.secret"
            metadata_file = self.storage_path / f"{name}.meta"

            if secret_file.exists():
                secret_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()

            return True

        except Exception as e:
            self.logger.error(f"Error deleting secret {name}: {e}")
            return False

    def list_secrets(self) -> List[str]:
        """List all stored secret names"""
        try:
            secrets = []
            for file_path in self.storage_path.glob("*.secret"):
                secrets.append(file_path.stem)
            return secrets
        except Exception as e:
            self.logger.error(f"Error listing secrets: {e}")
            return []


class VaultSecretStorage(SecretStorage):
    """HashiCorp Vault secret storage backend"""

    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "kv"):
        self.vault_url = vault_url
        self.mount_point = mount_point
        self.client = hvac.Client(url=vault_url, token=vault_token)
        self.logger = logging.getLogger(__name__)

        if not self.client.is_authenticated():
            raise Exception("Vault authentication failed")

    def store_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        """Store secret in Vault"""
        try:
            secret_data = {"value": value, "metadata": asdict(metadata)}

            self.client.secrets.kv.v2.create_or_update_secret(
                path=name, secret=secret_data, mount_point=self.mount_point
            )

            return True

        except Exception as e:
            self.logger.error(f"Error storing secret {name} in Vault: {e}")
            return False

    def retrieve_secret(self, name: str) -> Optional[str]:
        """Retrieve secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=name, mount_point=self.mount_point
            )

            return response["data"]["data"]["value"]

        except Exception as e:
            self.logger.error(f"Error retrieving secret {name} from Vault: {e}")
            return None

    def delete_secret(self, name: str) -> bool:
        """Delete secret from Vault"""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=name, mount_point=self.mount_point
            )

            return True

        except Exception as e:
            self.logger.error(f"Error deleting secret {name} from Vault: {e}")
            return False

    def list_secrets(self) -> List[str]:
        """List all secrets in Vault"""
        try:
            response = self.client.secrets.kv.v2.list_secrets(
                path="", mount_point=self.mount_point
            )

            return response["data"]["keys"]

        except Exception as e:
            self.logger.error(f"Error listing secrets from Vault: {e}")
            return []


class SecretRotationManager:
    """Manages automatic secret rotation"""

    def __init__(self, secret_manager: "ComprehensiveSecretManager"):
        self.secret_manager = secret_manager
        self.logger = logging.getLogger(__name__)

    def check_rotation_needed(self, secret_name: str) -> bool:
        """Check if secret needs rotation"""
        try:
            metadata = self.secret_manager.get_secret_metadata(secret_name)
            if not metadata:
                return False

            rotation_policy = self.secret_manager.get_rotation_policy(secret_name)
            if not rotation_policy or not rotation_policy.enabled:
                return False

            days_since_update = (datetime.now() - metadata.updated_at).days
            return days_since_update >= rotation_policy.rotation_days

        except Exception as e:
            self.logger.error(f"Error checking rotation for {secret_name}: {e}")
            return False

    def rotate_secret(self, secret_name: str, new_value: Optional[str] = None) -> bool:
        """Rotate a secret"""
        try:
            metadata = self.secret_manager.get_secret_metadata(secret_name)
            if not metadata:
                return False

            # Generate new value if not provided
            if new_value is None:
                new_value = self._generate_new_secret(metadata.secret_type)

            # Update secret
            success = self.secret_manager.store_secret(
                secret_name, new_value, metadata.secret_type, metadata.tags
            )

            if success:
                self.logger.info(f"Successfully rotated secret: {secret_name}")
                # TODO: Notify relevant systems of rotation
                self._notify_rotation(secret_name)

            return success

        except Exception as e:
            self.logger.error(f"Error rotating secret {secret_name}: {e}")
            return False

    def _generate_new_secret(self, secret_type: str) -> str:
        """Generate new secret based on type"""
        if secret_type == "api_key":
            return secrets.token_urlsafe(32)
        elif secret_type == "password":
            # Generate strong password
            return secrets.token_urlsafe(24)
        elif secret_type == "token":
            return secrets.token_hex(32)
        else:
            return secrets.token_urlsafe(32)

    def _notify_rotation(self, secret_name: str):
        """Notify systems of secret rotation"""
        # TODO: Implement notification logic
        self.logger.info(f"Secret {secret_name} rotated - notifications sent")


class ComprehensiveSecretManager:
    """Main secret management system"""

    def __init__(
        self,
        storage_backend: str = "file",
        storage_config: Optional[Dict[str, Any]] = None,
    ):
        self.storage_config = storage_config or {}
        self.encryption = SecretEncryption()
        self.logger = logging.getLogger(__name__)

        # Initialize storage backend
        if storage_backend == "file":
            storage_path = self.storage_config.get("path", "secrets")
            self.storage = FileSecretStorage(storage_path, self.encryption)
        elif storage_backend == "vault":
            self.storage = VaultSecretStorage(
                vault_url=self.storage_config["vault_url"],
                vault_token=self.storage_config["vault_token"],
                mount_point=self.storage_config.get("mount_point", "kv"),
            )
        else:
            raise ValueError(f"Unsupported storage backend: {storage_backend}")

        self.rotation_manager = SecretRotationManager(self)
        self.rotation_policies = self._load_rotation_policies()

    def store_secret(
        self, name: str, value: str, secret_type: str, tags: Optional[List[str]] = None
    ) -> bool:
        """Store a new secret"""
        try:
            # Validate inputs
            if not name or not value:
                raise ValueError("Secret name and value cannot be empty")

            # Create metadata
            metadata = SecretMetadata(
                name=name,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                rotation_period=self._get_default_rotation_period(secret_type),
                access_count=0,
                last_accessed=None,
                tags=tags or [],
                secret_type=secret_type,
            )

            success = self.storage.store_secret(name, value, metadata)

            if success:
                self.logger.info(f"Secret stored successfully: {name}")
                # Log audit event
                self._audit_log(
                    "SECRET_STORED", {"secret_name": name, "secret_type": secret_type}
                )

            return success

        except Exception as e:
            self.logger.error(f"Error storing secret {name}: {e}")
            return False

    def retrieve_secret(self, name: str) -> Optional[str]:
        """Retrieve a secret"""
        try:
            value = self.storage.retrieve_secret(name)

            if value:
                # Update access tracking
                self._update_access_tracking(name)
                # Log audit event
                self._audit_log("SECRET_ACCESSED", {"secret_name": name})

            return value

        except Exception as e:
            self.logger.error(f"Error retrieving secret {name}: {e}")
            return None

    def delete_secret(self, name: str) -> bool:
        """Delete a secret"""
        try:
            success = self.storage.delete_secret(name)

            if success:
                self.logger.info(f"Secret deleted: {name}")
                # Log audit event
                self._audit_log("SECRET_DELETED", {"secret_name": name})

            return success

        except Exception as e:
            self.logger.error(f"Error deleting secret {name}: {e}")
            return False

    def list_secrets(
        self, secret_type: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[str]:
        """List secrets with optional filtering"""
        try:
            all_secrets = self.storage.list_secrets()

            if not secret_type and not tags:
                return all_secrets

            # Filter by metadata
            filtered_secrets = []
            for secret_name in all_secrets:
                metadata = self.get_secret_metadata(secret_name)
                if metadata:
                    if secret_type and metadata.secret_type != secret_type:
                        continue
                    if tags and not any(tag in metadata.tags for tag in tags):
                        continue
                    filtered_secrets.append(secret_name)

            return filtered_secrets

        except Exception as e:
            self.logger.error(f"Error listing secrets: {e}")
            return []

    def get_secret_metadata(self, name: str) -> Optional[SecretMetadata]:
        """Get secret metadata"""
        try:
            metadata_file = Path(self.storage.storage_path) / f"{name}.meta"
            if not metadata_file.exists():
                return None

            with open(metadata_file, "r") as f:
                metadata_dict = json.load(f)

            # Convert datetime strings back to datetime objects
            metadata_dict["created_at"] = datetime.fromisoformat(
                metadata_dict["created_at"]
            )
            metadata_dict["updated_at"] = datetime.fromisoformat(
                metadata_dict["updated_at"]
            )
            if metadata_dict["last_accessed"]:
                metadata_dict["last_accessed"] = datetime.fromisoformat(
                    metadata_dict["last_accessed"]
                )

            return SecretMetadata(**metadata_dict)

        except Exception as e:
            self.logger.error(f"Error getting metadata for {name}: {e}")
            return None

    def check_rotations(self) -> Dict[str, Any]:
        """Check all secrets for needed rotations"""
        results = {
            "secrets_checked": 0,
            "rotations_needed": [],
            "rotations_completed": [],
            "errors": [],
        }

        try:
            all_secrets = self.list_secrets()
            results["secrets_checked"] = len(all_secrets)

            for secret_name in all_secrets:
                try:
                    if self.rotation_manager.check_rotation_needed(secret_name):
                        results["rotations_needed"].append(secret_name)

                        # Auto-rotate if enabled
                        rotation_policy = self.get_rotation_policy(secret_name)
                        if rotation_policy and rotation_policy.auto_rotate:
                            if self.rotation_manager.rotate_secret(secret_name):
                                results["rotations_completed"].append(secret_name)

                except Exception as e:
                    results["errors"].append(f"Error checking {secret_name}: {e}")

            return results

        except Exception as e:
            self.logger.error(f"Error checking rotations: {e}")
            results["errors"].append(str(e))
            return results

    def get_rotation_policy(self, secret_name: str) -> Optional[SecretRotationPolicy]:
        """Get rotation policy for a secret"""
        return self.rotation_policies.get(secret_name)

    def set_rotation_policy(self, secret_name: str, policy: SecretRotationPolicy):
        """Set rotation policy for a secret"""
        self.rotation_policies[secret_name] = policy
        self._save_rotation_policies()

    def _get_default_rotation_period(self, secret_type: str) -> int:
        """Get default rotation period for secret type"""
        defaults = {
            "api_key": 90,
            "database": 180,
            "certificate": 365,
            "password": 90,
            "token": 30,
        }
        return defaults.get(secret_type, 90)

    def _update_access_tracking(self, name: str):
        """Update access tracking for a secret"""
        try:
            metadata = self.get_secret_metadata(name)
            if metadata:
                metadata.access_count += 1
                metadata.last_accessed = datetime.now()

                # Save updated metadata
                metadata_file = Path(self.storage.storage_path) / f"{name}.meta"
                with open(metadata_file, "w") as f:
                    json.dump(asdict(metadata), f, default=str, indent=2)

        except Exception as e:
            self.logger.error(f"Error updating access tracking for {name}: {e}")

    def _audit_log(self, action: str, details: Dict[str, Any]):
        """Log audit event"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user": os.getenv("USER", "unknown"),
        }

        # TODO: Send to audit logging system
        self.logger.info(f"AUDIT: {json.dumps(audit_entry)}")

    def _load_rotation_policies(self) -> Dict[str, SecretRotationPolicy]:
        """Load rotation policies from configuration"""
        try:
            config_file = Path(self.storage.storage_path) / "rotation_policies.json"
            if config_file.exists():
                with open(config_file, "r") as f:
                    policies_dict = json.load(f)

                policies = {}
                for name, policy_dict in policies_dict.items():
                    policies[name] = SecretRotationPolicy(**policy_dict)

                return policies
        except Exception as e:
            self.logger.error(f"Error loading rotation policies: {e}")

        return {}

    def _save_rotation_policies(self):
        """Save rotation policies to configuration"""
        try:
            config_file = Path(self.storage.storage_path) / "rotation_policies.json"
            policies_dict = {}

            for name, policy in self.rotation_policies.items():
                policies_dict[name] = asdict(policy)

            with open(config_file, "w") as f:
                json.dump(policies_dict, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving rotation policies: {e}")


def main():
    """Main execution function"""
    print("🔐 Horse Racing AI V2.03 - Comprehensive Secret Management System")
    print("=" * 70)

    # Initialize secret manager
    secret_manager = ComprehensiveSecretManager(
        storage_backend="file", storage_config={"path": "config/secrets"}
    )

    # Demo operations
    print("\n📊 Secret Management Operations:")

    # Store sample secrets
    test_secrets = [
        (
            "betdaq_api_key",
            "sample_betdaq_key_12345",
            "api_key",
            ["betting", "production"],
        ),
        (
            "database_password",
            "secure_db_password_67890",
            "password",
            ["database", "production"],
        ),
        ("jwt_secret", "jwt_signing_secret_abcdef", "token", ["auth", "api"]),
    ]

    for name, value, secret_type, tags in test_secrets:
        success = secret_manager.store_secret(name, value, secret_type, tags)
        print(
            f"  {'✅' if success else '❌'} Store {name}: {'Success' if success else 'Failed'}"
        )

    # List secrets
    print(f"\n📋 Stored Secrets: {len(secret_manager.list_secrets())}")
    for secret_name in secret_manager.list_secrets():
        metadata = secret_manager.get_secret_metadata(secret_name)
        if metadata:
            print(
                f"  🔑 {secret_name} ({metadata.secret_type}) - {len(metadata.tags)} tags"
            )

    # Check rotations
    print("\n🔄 Rotation Check:")
    rotation_results = secret_manager.check_rotations()
    print(f"  📊 Checked: {rotation_results['secrets_checked']} secrets")
    print(f"  ⚠️ Need Rotation: {len(rotation_results['rotations_needed'])}")
    print(f"  ✅ Auto-Rotated: {len(rotation_results['rotations_completed'])}")

    print("\n✅ Secret management system demonstration completed")


if __name__ == "__main__":
    main()
