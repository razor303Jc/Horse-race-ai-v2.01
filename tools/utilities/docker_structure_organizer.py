#!/usr/bin/env python3
"""
Docker Structure Organizer

This script organizes files from the root directory into proper Docker container structure
and updates all references to maintain functionality.
"""

import os
import shutil
from pathlib import Path
import json
import re


class DockerStructureOrganizer:
    """Organizes project files into proper Docker structure"""
    
    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.01")
        
        # Define file movements
        self.moves = {
            # Data processing files -> docker/data_pipeline/
            "data_cleaner.py": "docker/data_pipeline/data_cleaner.py",
            "clean_upload.py": "docker/data_pipeline/clean_upload.py",
            "simple_upload.py": "docker/data_pipeline/simple_upload.py",
            "upload_races.py": "docker/data_pipeline/upload_races.py",
            
            # Pipeline files -> docker/automation/
            "dynamic_pipeline_timing.py": "docker/automation/dynamic_pipeline_timing.py",
            "pipeline_integration_summary.py": "docker/automation/pipeline_integration_summary.py",
            
            # Main application files -> src/
            "main.py": "src/main.py",
            "app.py": "src/app.py",
        }
        
        # Files that need reference updates
        self.reference_updates = {
            "docker/automation/run_docker_auto_downloader.py": [
                ("from data_cleaner", "from docker.data_pipeline.data_cleaner"),
                ("from simple_upload", "from docker.data_pipeline.simple_upload"),
                ("from upload_races", "from docker.data_pipeline.upload_races"),
            ],
            "tools/data_processing/advanced_csv_mapper.py": [
                ("from data_cleaner", "from docker.data_pipeline.data_cleaner"),
                ("import upload_races", "from docker.data_pipeline import upload_races"),
            ],
        }
    
    def backup_files(self):
        """Create backup of files before moving"""
        print("📦 Creating backup of files...")
        backup_dir = self.project_root / "backups" / "pre_organization"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for src_file in self.moves.keys():
            src_path = self.project_root / src_file
            if src_path.exists():
                backup_path = backup_dir / src_file
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, backup_path)
                print(f"  ✅ Backed up {src_file}")
    
    def move_files(self):
        """Move files to their proper Docker locations"""
        print("\n🚚 Moving files to proper Docker structure...")
        
        for src_file, dest_file in self.moves.items():
            src_path = self.project_root / src_file
            dest_path = self.project_root / dest_file
            
            if src_path.exists():
                # Create destination directory
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file (or copy if destination exists)
                if dest_path.exists():
                    print(f"  ⚠️  {dest_file} already exists, comparing...")
                    if self._files_different(src_path, dest_path):
                        # Keep newer version or merge
                        backup_name = f"{dest_path.name}.backup"
                        shutil.move(dest_path, dest_path.parent / backup_name)
                        shutil.move(src_path, dest_path)
                        print(f"  ✅ Moved {src_file} -> {dest_file} (backed up existing)")
                    else:
                        os.remove(src_path)
                        print(f"  ✅ Removed duplicate {src_file}")
                else:
                    shutil.move(src_path, dest_path)
                    print(f"  ✅ Moved {src_file} -> {dest_file}")
            else:
                print(f"  ⚠️  {src_file} not found, skipping")
    
    def _files_different(self, file1: Path, file2: Path) -> bool:
        """Check if two files are different"""
        try:
            with open(file1, 'r') as f1, open(file2, 'r') as f2:
                return f1.read() != f2.read()
        except:
            return True
    
    def update_references(self):
        """Update import and reference paths in files"""
        print("\n🔧 Updating file references...")
        
        # Update Dockerfiles
        self._update_dockerfiles()
        
        # Update import statements
        for file_path, updates in self.reference_updates.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                self._update_file_references(full_path, updates)
        
        # Update all Python files for import references
        self._update_all_imports()
    
    def _update_dockerfiles(self):
        """Update Dockerfile COPY statements"""
        dockerfiles = [
            "Dockerfile",
            "configs/docker/Dockerfile.auto",
            "docker-compose.yml",
            "docker-compose.auto-downloader.yml"
        ]
        
        for dockerfile in dockerfiles:
            dockerfile_path = self.project_root / dockerfile
            if dockerfile_path.exists():
                print(f"  🐳 Updating {dockerfile}")
                
                with open(dockerfile_path, 'r') as f:
                    content = f.read()
                
                # Update COPY statements for moved files
                for src_file, dest_file in self.moves.items():
                    # Update COPY statements
                    content = re.sub(
                        f"COPY {re.escape(src_file)}",
                        f"COPY {dest_file}",
                        content
                    )
                
                with open(dockerfile_path, 'w') as f:
                    f.write(content)
    
    def _update_file_references(self, file_path: Path, updates: list):
        """Update specific file references"""
        print(f"  📝 Updating {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        for old_ref, new_ref in updates:
            content = content.replace(old_ref, new_ref)
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def _update_all_imports(self):
        """Update all import statements across the project"""
        print("  🔍 Scanning for import references...")
        
        # Find all Python files
        for py_file in self.project_root.rglob("*.py"):
            if py_file.is_file() and not any(part.startswith('.') for part in py_file.parts):
                self._update_imports_in_file(py_file)
    
    def _update_imports_in_file(self, file_path: Path):
        """Update imports in a specific file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Update imports for moved files
            import_updates = {
                "from data_cleaner": "from docker.data_pipeline.data_cleaner",
                "import data_cleaner": "from docker.data_pipeline import data_cleaner",
                "from clean_upload": "from docker.data_pipeline.clean_upload",
                "import clean_upload": "from docker.data_pipeline import clean_upload",
                "from simple_upload": "from docker.data_pipeline.simple_upload",
                "import simple_upload": "from docker.data_pipeline import simple_upload",
                "from upload_races": "from docker.data_pipeline.upload_races",
                "import upload_races": "from docker.data_pipeline import upload_races",
                "from dynamic_pipeline_timing": "from docker.automation.dynamic_pipeline_timing",
                "import dynamic_pipeline_timing": "from docker.automation import dynamic_pipeline_timing",
            }
            
            for old_import, new_import in import_updates.items():
                content = content.replace(old_import, new_import)
            
            # Only write if changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"    ✅ Updated imports in {file_path.relative_to(self.project_root)}")
                
        except Exception as e:
            print(f"    ⚠️  Error updating {file_path}: {e}")
    
    def create_init_files(self):
        """Create __init__.py files for Python packages"""
        print("\n📁 Creating __init__.py files...")
        
        package_dirs = [
            "docker",
            "docker/automation",
            "docker/data_pipeline",
            "docker/scripts",
            "src",
        ]
        
        for pkg_dir in package_dirs:
            init_path = self.project_root / pkg_dir / "__init__.py"
            if not init_path.exists():
                init_path.parent.mkdir(parents=True, exist_ok=True)
                with open(init_path, 'w') as f:
                    f.write(f'"""Docker {pkg_dir.split("/")[-1]} package"""\n')
                print(f"  ✅ Created {init_path.relative_to(self.project_root)}")
    
    def update_schedule_default_time(self):
        """Update the default schedule time to 00:01"""
        print("\n⏰ Updating default schedule time to 00:01...")
        
        schedule_manager_path = self.project_root / "tools/cli/schedule_manager.py"
        if schedule_manager_path.exists():
            with open(schedule_manager_path, 'r') as f:
                content = f.read()
            
            # Update any hardcoded default times
            content = re.sub(
                r'download_time.*?=.*?"11:31"',
                'download_time" = "00:01"',
                content
            )
            content = re.sub(
                r'default.*?=.*?"11:31"',
                'default="00:01"',
                content
            )
            
            with open(schedule_manager_path, 'w') as f:
                f.write(content)
            
            print("  ✅ Updated schedule manager default time")
            
            # Update configuration files
            config_files = list(self.project_root.glob("config/*pipeline*.json"))
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    if "schedule" in config and "download_time" in config["schedule"]:
                        old_time = config["schedule"]["download_time"]
                        config["schedule"]["download_time"] = "00:01"
                        
                        with open(config_file, 'w') as f:
                            json.dump(config, f, indent=2)
                        
                        print(f"  ✅ Updated {config_file.name}: {old_time} -> 00:01")
                except Exception as e:
                    print(f"  ⚠️  Error updating {config_file}: {e}")
    
    def validate_structure(self):
        """Validate the new structure"""
        print("\n✅ Validating new structure...")
        
        # Check that moved files exist in new locations
        for src_file, dest_file in self.moves.items():
            dest_path = self.project_root / dest_file
            if dest_path.exists():
                print(f"  ✅ {dest_file}")
            else:
                print(f"  ❌ {dest_file} - MISSING!")
        
        # Check for __init__.py files
        required_inits = [
            "docker/__init__.py",
            "docker/automation/__init__.py",
            "docker/data_pipeline/__init__.py",
        ]
        
        for init_file in required_inits:
            init_path = self.project_root / init_file
            if init_path.exists():
                print(f"  ✅ {init_file}")
            else:
                print(f"  ❌ {init_file} - MISSING!")
    
    def run_organization(self):
        """Run the complete organization process"""
        print("🏗️  Docker Structure Organization Starting...")
        print("=" * 60)
        
        try:
            self.backup_files()
            self.move_files()
            self.create_init_files()
            self.update_references()
            self.update_schedule_default_time()
            self.validate_structure()
            
            print("\n🎉 Docker structure organization completed successfully!")
            print("\n📋 Summary of changes:")
            print("  • Moved data processing files to docker/data_pipeline/")
            print("  • Moved automation files to docker/automation/")
            print("  • Moved main application files to src/")
            print("  • Updated all import references")
            print("  • Created Python package __init__.py files")
            print("  • Updated default schedule time to 00:01")
            print("  • Updated Dockerfile references")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during organization: {e}")
            return False


def main():
    """Main function"""
    organizer = DockerStructureOrganizer()
    success = organizer.run_organization()
    
    if success:
        print("\n🚀 Next steps:")
        print("  1. Review moved files and updated references")
        print("  2. Run tests to validate functionality")
        print("  3. Rebuild Docker containers")
        print("  4. Test the complete pipeline")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
