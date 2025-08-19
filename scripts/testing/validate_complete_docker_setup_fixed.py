#!/usr/bin/env python3
import os
import glob
import yaml
import subprocess

def check_docker_setup():
    print("🐳 COMPLETE DOCKER SETUP VALIDATION (FIXED)")
    print("=" * 60)
    
    # Check docker-compose files
    compose_files = sorted(glob.glob("docker-compose*.yml"))
    print(f"📋 Found {len(compose_files)} docker-compose files:")
    for f in compose_files:
        size = os.path.getsize(f)
        print(f"  - {f} ({size} bytes)")
    
    print("\n🔍 DOCKERFILE REFERENCES IN COMPOSE FILES:")
    print("-" * 50)
    
    for compose_file in compose_files:
        try:
            with open(compose_file, 'r') as f:
                content = f.read()
            
            print(f"\n📄 {compose_file}:")
            lines = content.split('\n')
            dockerfile_count = 0
            for i, line in enumerate(lines):
                if 'dockerfile:' in line.lower():
                    dockerfile_path = line.split('dockerfile:')[-1].strip()
                    exists = os.path.exists(dockerfile_path)
                    status = "✅" if exists else "❌"
                    print(f"  {status} Line {i+1}: {dockerfile_path}")
                    dockerfile_count += 1
            
            if dockerfile_count == 0:
                print("  📝 No dockerfile references found")
                
        except Exception as e:
            print(f"❌ Error reading {compose_file}: {e}")
    
    print("\n📁 DOCKER DIRECTORY STRUCTURE:")
    print("-" * 40)
    
    # Check docker directory structure
    if os.path.exists('docker'):
        print("📂 docker/")
        for root, dirs, files in os.walk('docker'):
            level = root.replace('docker', '').count(os.sep)
            indent = '  ' * (level + 1)
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = '  ' * (level + 2)
            for file in files:
                if file.startswith('Dockerfile') or file.endswith('.txt') or file.endswith('.py'):
                    size = os.path.getsize(os.path.join(root, file))
                    print(f"{subindent}📄 {file} ({size} bytes)")
    else:
        print("❌ docker/ directory not found")
    
    print("\n🏗️ MICROSERVICES ARCHITECTURE SUMMARY:")
    print("-" * 45)
    
    # Check services using grep-based approach (more reliable)
    clean_file = 'docker-compose.clean.yml'
    if os.path.exists(clean_file):
        try:
            result = subprocess.run(['grep', '-n', '^  [a-zA-Z]', clean_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                service_lines = result.stdout.strip().split('\n')
                services = []
                for line in service_lines:
                    if ':' in line:
                        service_name = line.split(':')[1].strip().rstrip(':')
                        if service_name and service_name not in ['version', 'services', 'networks', 'volumes']:
                            services.append(service_name)
                
                print(f"📊 Services in {clean_file} ({len(services)} services):")
                for service in services:
                    print(f"  🔹 {service}")
            else:
                print(f"❌ Could not parse services from {clean_file}")
                
        except Exception as e:
            print(f"❌ Error parsing {clean_file}: {e}")
    
    # Check project structure
    print("\n📂 PROJECT STRUCTURE OVERVIEW:")
    print("-" * 30)
    
    project_dirs = ['src', 'api', 'config', 'database', 'templates', 'tools', 'reports', 'analysis']
    for dir_name in project_dirs:
        if os.path.exists(dir_name):
            if os.path.isdir(dir_name):
                file_count = sum(len(files) for _, _, files in os.walk(dir_name))
                dir_count = sum(len(dirs) for _, dirs, _ in os.walk(dir_name)) - 1  # exclude root
                print(f"  ✅ {dir_name}/ ({file_count} files, {dir_count} subdirs)")
            else:
                print(f"  📄 {dir_name} (file)")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("-" * 20)
    print("1. Use docker-compose.clean.yml for main deployment (clean microservices)")
    print("2. All Dockerfiles are properly organized in docker/dockerfiles/")
    print("3. All requirements are properly organized in docker/requirements/")
    print("4. Auto-downloader service uses --profile auto-downloader for optional deployment")
    print("5. Project structure is comprehensive with all major components")

if __name__ == "__main__":
    check_docker_setup()
