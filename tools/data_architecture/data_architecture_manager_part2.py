    async def _save_monitoring_results(self, results: Dict) -> None:
        """Save monitoring results to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = self.monitoring_root / f'monitoring_results_{timestamp}.json'
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Also save as latest
            latest_file = self.monitoring_root / 'latest_monitoring_results.json'
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"Saved monitoring results to {results_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving monitoring results: {e}")
    
    async def _run_data_versioning(self) -> Dict[str, Any]:
        """Run data versioning and history tracking."""
        try:
            self.logger.info("Running data versioning")
            
            versioning_results = {
                'timestamp': datetime.now().isoformat(),
                'files_versioned': 0,
                'databases_versioned': 0,
                'versions_created': [],
                'old_versions_cleaned': 0,
                'storage_used_mb': 0
            }
            
            # Version key data files
            data_files = list(self.data_root.rglob('*.csv')) + list(self.data_root.rglob('*.json'))
            
            for file_path in data_files:
                if file_path.is_file() and not str(file_path).startswith(str(self.versioning_root)):
                    try:
                        version_info = await self._create_file_version(file_path)
                        if version_info:
                            versioning_results['files_versioned'] += 1
                            versioning_results['versions_created'].append(version_info)
                            versioning_results['storage_used_mb'] += version_info.get('size_mb', 0)
                    except Exception as e:
                        self.logger.warning(f"Error versioning file {file_path}: {e}")
            
            # Version database if configured
            if self.db_config:
                db_version_info = await self._create_database_version()
                if db_version_info:
                    versioning_results['databases_versioned'] += 1
                    versioning_results['versions_created'].append(db_version_info)
                    versioning_results['storage_used_mb'] += db_version_info.get('size_mb', 0)
            
            # Clean up old versions
            cleaned_count = await self._cleanup_old_versions()
            versioning_results['old_versions_cleaned'] = cleaned_count
            
            return versioning_results
            
        except Exception as e:
            self.logger.error(f"Error in data versioning: {e}")
            return {'error': str(e)}
    
    async def _create_file_version(self, file_path: Path) -> Optional[Dict]:
        """Create a version of a data file."""
        try:
            # Generate version info
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = self._calculate_file_checksum(file_path)
            
            # Create version directory
            relative_path = file_path.relative_to(self.data_root)
            version_dir = self.versioning_root / relative_path.parent
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Create versioned filename
            version_filename = f"{file_path.stem}_{timestamp}_{file_hash[:8]}{file_path.suffix}"
            version_path = version_dir / version_filename
            
            # Check if this version already exists (same hash)
            existing_versions = list(version_dir.glob(f"{file_path.stem}_*{file_path.suffix}"))
            for existing in existing_versions:
                if file_hash[:8] in existing.name:
                    # Same content, skip versioning
                    return None
            
            # Copy file to version directory
            shutil.copy2(file_path, version_path)
            
            # Create metadata
            metadata = {
                'original_path': str(file_path),
                'version_path': str(version_path),
                'timestamp': timestamp,
                'file_hash': file_hash,
                'file_size': file_path.stat().st_size,
                'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                'creation_time': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                'modification_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # Save metadata
            metadata_path = version_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error creating file version for {file_path}: {e}")
            return None
    
    async def _create_database_version(self) -> Optional[Dict]:
        """Create a version of the database."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create database backup directory
            db_version_dir = self.versioning_root / 'database'
            db_version_dir.mkdir(parents=True, exist_ok=True)
            
            # Create database dump
            dump_filename = f"db_version_{timestamp}.sql"
            dump_path = db_version_dir / dump_filename
            
            # Use pg_dump to create database version
            dump_command = [
                'pg_dump',
                '-h', self.db_config.get('host', 'localhost'),
                '-p', str(self.db_config.get('port', 5432)),
                '-U', self.db_config.get('user', 'postgres'),
                '-d', self.db_config.get('database', 'horse_racing'),
                '-f', str(dump_path),
                '--verbose'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.get('password', '')
            
            result = subprocess.run(dump_command, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                # Compress the dump
                compressed_path = dump_path.with_suffix('.sql.gz')
                with open(dump_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed version
                dump_path.unlink()
                
                # Create metadata
                metadata = {
                    'type': 'database_version',
                    'version_path': str(compressed_path),
                    'timestamp': timestamp,
                    'database': self.db_config.get('database'),
                    'host': self.db_config.get('host'),
                    'file_size': compressed_path.stat().st_size,
                    'size_mb': round(compressed_path.stat().st_size / (1024 * 1024), 2),
                    'dump_success': True
                }
                
                # Save metadata
                metadata_path = compressed_path.with_suffix('.metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return metadata
            else:
                self.logger.error(f"Database dump failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating database version: {e}")
            return None
    
    async def _cleanup_old_versions(self) -> int:
        """Clean up old versions beyond the retention limit."""
        try:
            cleaned_count = 0
            
            # Clean up file versions
            for version_dir in self.versioning_root.rglob('*'):
                if version_dir.is_dir() and version_dir != self.versioning_root:
                    # Get all version files in this directory
                    version_files = []
                    for file_path in version_dir.iterdir():
                        if file_path.is_file() and not file_path.name.endswith('.metadata.json'):
                            try:
                                # Extract timestamp from filename
                                parts = file_path.stem.split('_')
                                if len(parts) >= 2:
                                    timestamp_str = parts[-2]  # Assuming format: name_timestamp_hash
                                    file_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                    version_files.append((file_path, file_time))
                            except Exception:
                                pass  # Skip files with unexpected format
                    
                    # Sort by timestamp (newest first)
                    version_files.sort(key=lambda x: x[1], reverse=True)
                    
                    # Remove old versions beyond max_versions
                    if len(version_files) > self.max_versions:
                        for file_path, _ in version_files[self.max_versions:]:
                            try:
                                file_path.unlink()
                                # Also remove metadata file
                                metadata_path = file_path.with_suffix('.metadata.json')
                                if metadata_path.exists():
                                    metadata_path.unlink()
                                cleaned_count += 1
                            except Exception as e:
                                self.logger.warning(f"Error removing old version {file_path}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old versions: {e}")
            return 0
    
    async def _run_automated_backup(self) -> Dict[str, Any]:
        """Run automated backup system."""
        try:
            self.logger.info("Running automated backup")
            
            backup_results = {
                'timestamp': datetime.now().isoformat(),
                'backup_type': 'full',
                'files_backed_up': 0,
                'databases_backed_up': 0,
                'backup_size_mb': 0,
                'backup_path': '',
                'compression_ratio': 0.0,
                'backup_success': False
            }
            
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.backup_root / f'backup_{timestamp}'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_results['backup_path'] = str(backup_dir)
            
            # Backup data files
            if self.config.get('backup', {}).get('include_files', True):
                files_backup_result = await self._backup_data_files(backup_dir)
                backup_results['files_backed_up'] = files_backup_result.get('files_count', 0)
                backup_results['backup_size_mb'] += files_backup_result.get('size_mb', 0)
            
            # Backup database
            if self.config.get('backup', {}).get('include_database', True) and self.db_config:
                db_backup_result = await self._backup_database(backup_dir)
                if db_backup_result.get('success'):
                    backup_results['databases_backed_up'] = 1
                    backup_results['backup_size_mb'] += db_backup_result.get('size_mb', 0)
            
            # Create backup archive if compression enabled
            if self.config.get('backup', {}).get('compression', True):
                archive_result = await self._create_backup_archive(backup_dir)
                if archive_result.get('success'):
                    backup_results['compression_ratio'] = archive_result.get('compression_ratio', 0)
                    backup_results['backup_size_mb'] = archive_result.get('compressed_size_mb', 0)
            
            # Create backup manifest
            manifest = await self._create_backup_manifest(backup_dir, backup_results)
            
            # Clean up old backups
            cleaned_backups = await self._cleanup_old_backups()
            backup_results['old_backups_cleaned'] = cleaned_backups
            
            backup_results['backup_success'] = True
            
            return backup_results
            
        except Exception as e:
            self.logger.error(f"Error in automated backup: {e}")
            return {'error': str(e), 'backup_success': False}
    
    async def _backup_data_files(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup data files to backup directory."""
        try:
            files_backup_dir = backup_dir / 'data_files'
            files_backup_dir.mkdir(parents=True, exist_ok=True)
            
            files_count = 0
            total_size = 0
            
            # Copy important data files
            important_paths = [
                self.data_root / 'daily_downloads',
                self.data_root / 'preprocessed',
                self.data_root / 'monte_carlo_results',
                self.data_root / 'speed_analysis'
            ]
            
            for source_path in important_paths:
                if source_path.exists():
                    dest_path = files_backup_dir / source_path.name
                    
                    if source_path.is_dir():
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        # Count files and size
                        for file_path in dest_path.rglob('*'):
                            if file_path.is_file():
                                files_count += 1
                                total_size += file_path.stat().st_size
                    else:
                        shutil.copy2(source_path, dest_path)
                        files_count += 1
                        total_size += dest_path.stat().st_size
            
            return {
                'files_count': files_count,
                'size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error backing up data files: {e}")
            return {'files_count': 0, 'size_mb': 0}
    
    async def _backup_database(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup database to backup directory."""
        try:
            db_backup_dir = backup_dir / 'database'
            db_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create database dump
            dump_filename = 'database_backup.sql'
            dump_path = db_backup_dir / dump_filename
            
            # Use pg_dump
            dump_command = [
                'pg_dump',
                '-h', self.db_config.get('host', 'localhost'),
                '-p', str(self.db_config.get('port', 5432)),
                '-U', self.db_config.get('user', 'postgres'),
                '-d', self.db_config.get('database', 'horse_racing'),
                '-f', str(dump_path),
                '--verbose'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.get('password', '')
            
            result = subprocess.run(dump_command, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                # Compress the dump
                compressed_path = dump_path.with_suffix('.sql.gz')
                with open(dump_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                dump_path.unlink()  # Remove uncompressed version
                
                return {
                    'success': True,
                    'size_mb': round(compressed_path.stat().st_size / (1024 * 1024), 2)
                }
            else:
                self.logger.error(f"Database backup failed: {result.stderr}")
                return {'success': False, 'size_mb': 0}
                
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            return {'success': False, 'size_mb': 0}
    
    async def _create_backup_archive(self, backup_dir: Path) -> Dict[str, Any]:
        """Create compressed archive of backup directory."""
        try:
            archive_path = backup_dir.with_suffix('.tar.gz')
            
            # Calculate original size
            original_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
            
            # Create tar.gz archive
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(backup_dir, arcname=backup_dir.name)
            
            # Calculate compressed size
            compressed_size = archive_path.stat().st_size
            
            # Remove original backup directory
            shutil.rmtree(backup_dir)
            
            compression_ratio = (original_size - compressed_size) / original_size if original_size > 0 else 0
            
            return {
                'success': True,
                'compressed_size_mb': round(compressed_size / (1024 * 1024), 2),
                'compression_ratio': round(compression_ratio, 3)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating backup archive: {e}")
            return {'success': False}
    
    async def _create_backup_manifest(self, backup_dir: Path, backup_results: Dict) -> Dict:
        """Create backup manifest with metadata."""
        try:
            manifest = {
                'backup_timestamp': datetime.now().isoformat(),
                'backup_type': 'automated_full',
                'backup_results': backup_results,
                'system_info': {
                    'hostname': os.uname().nodename,
                    'python_version': os.sys.version,
                    'backup_tool_version': '1.0.0'
                },
                'verification': {
                    'checksum': '',
                    'file_count': 0
                }
            }
            
            # Calculate backup checksum and file count
            if backup_dir.exists():
                all_files = list(backup_dir.rglob('*'))
                manifest['verification']['file_count'] = len([f for f in all_files if f.is_file()])
                
                # Simple manifest checksum (sum of file sizes)
                total_size = sum(f.stat().st_size for f in all_files if f.is_file())
                manifest['verification']['checksum'] = str(total_size)
            
            # Save manifest
            manifest_path = backup_dir / 'backup_manifest.json'
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return manifest
            
        except Exception as e:
            self.logger.error(f"Error creating backup manifest: {e}")
            return {}
    
    async def _cleanup_old_backups(self) -> int:
        """Clean up old backups beyond retention period."""
        try:
            cleaned_count = 0
            cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
            
            # Find old backup files/directories
            for backup_item in self.backup_root.iterdir():
                try:
                    # Extract timestamp from backup name
                    if backup_item.name.startswith('backup_'):
                        timestamp_str = backup_item.name.replace('backup_', '').replace('.tar.gz', '')
                        backup_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        if backup_time < cutoff_date:
                            if backup_item.is_dir():
                                shutil.rmtree(backup_item)
                            else:
                                backup_item.unlink()
                            cleaned_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Error processing backup item {backup_item}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
            return 0
