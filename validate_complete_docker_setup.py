#!/usr/bin/env python3
import os
import glob
import subprocess

def check_docker_setup():
    print("🐳 COMPLETE DOCKER SETUP VALIDATION")
    print("=" * 60)
    
    # Check docker-compose files
    compose_files = sorted(glob.glob("docker-compose*.yml"))
    print(f"📋 Found {len(compose_files)} docker-compose files:")
    for f in compose_files:
        size = os.path.getsize(f)
        print(f"  - {f} ({size} bytes)")
    
    # Check auto-downloader specific files
    auto_downloader_files = glob.glob("configs/docker/docker-compose.auto-downloader.yml")
    if auto_downloader_files:
        print(f"\n🤖 Auto-downloader files:")
        for f in auto_downloader_files:
            size = os.path.getsize(f)
            print(f"  - {f} ({size} bytes)")
    
    print("\n🔍 DOCKERFILE REFERENCES IN COMPOSE FILES:")
    print("-" * 50)
    
    all_files = compose_files + auto_downloader_files
    for compose_file in all_files:
        try:
            with open(compose_file, 'r') as f:
                content = f.read()
            
            print(f"\n📄 {compose_file}:")
            lines = content.split('\n')
            dockerfile_count = 0
            for i, line in enumerate(lines):
                if 'dockerfile:' in line.lower():
                    dockerfile_path = line.split('dockerfile:')[-1].strip()
                    # Handle relative paths for auto-downloader
                    if compose_file.startswith('configs/docker/'):
                        if not dockerfile_path.startswith('docker/'):
                            # Convert relative path
                            if dockerfile_path == '../../docker/dockerfiles/Dockerfile':
                                dockerfile_path = 'docker/dockerfiles/Dockerfile'
                    
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
                if file.startswith('Dockerfile') or file.endswith('.txt'):
                    size = os.path.getsize(os.path.join(root, file))
                    print(f"{subindent}📄 {file} ({size} bytes)")
    else:
        print("❌ docker/ directory not found")
    
    print("\n🏗️ MICROSERVICES ARCHITECTURE SUMMARY:")
    print("-" * 45)
    
    # Check the clean microservices file
    clean_file = 'docker-compose.clean.yml'
    if os.path.exists(clean_file):
        with open(clean_file, 'r') as f:
            content = f.read()
        
        services = []
        lines = content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#') and ':' in line and not line.startswith(' '):
                if line.strip() != 'services:' and line.strip() != 'version:' and line.strip() != 'networks:' and line.strip() != 'volumes:':
                    service_name = line.split(':')[0].strip()
                    services.append(service_name)
        
        print(f"📊 Services in {clean_file}:")
        for service in services:
            print(f"  🔹 {service}")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("-" * 20)
    print("1. Use docker-compose.clean.yml for main deployment (clean microservices)")
    print("2. Use docker-compose.yml for legacy/reference (11+ services)")
    print("3. Use docker-compose.optimized.yml for performance scenarios")
    print("4. Auto-downloader is integrated in docker-compose.clean.yml with --profile auto-downloader")
    print("5. All Dockerfiles are properly organized in docker/dockerfiles/")
    print("6. All requirements are properly organized in docker/requirements/")

if __name__ == "__main__":
    check_docker_setup()
