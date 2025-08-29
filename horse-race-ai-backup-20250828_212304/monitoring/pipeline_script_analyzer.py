#!/usr/bin/env python3
"""
Pipeline Script Analyzer - Identifies which scripts are being used in the pipeline
and analyzes the manual download files
"""

import os
import sys
import json
import time
from pathlib import Path
import subprocess

sys.path.insert(0, '/home/jc/Documents/Horse-race-ai-v2.03/monitoring')
from script_function_analyzer import ScriptFunctionAnalyzer

class PipelineScriptAnalyzer:
    """
    Analyzes pipeline scripts and identifies which ones are actually used
    """
    
    def __init__(self):
        self.base_dir = "/home/jc/Documents/Horse-race-ai-v2.03"
        self.manual_download_dir = os.path.join(self.base_dir, "data/daily_downloads/manual_download")
        self.analyzer = ScriptFunctionAnalyzer()
        
        # Key pipeline directories
        self.pipeline_dirs = [
            "tools",
            "src/stages", 
            "src/feeds",
            "src/database",
            "src/management",
            "src/horse_racing_ai"
        ]
        
        self.script_usage = {}
        self.file_analysis = {}
    
    @property
    def track_function(self):
        return self.analyzer.track_function
    
    def analyze_manual_downloads(self):
        """Analyze the manually downloaded files"""
        print("📁 Analyzing manually downloaded files...")
        
        if not os.path.exists(self.manual_download_dir):
            print(f"❌ Manual download directory not found: {self.manual_download_dir}")
            return {}
        
        analysis = {
            'directory': self.manual_download_dir,
            'files_found': [],
            'file_types': {},
            'total_size': 0,
            'analysis_timestamp': time.time()
        }
        
        try:
            for root, dirs, files in os.walk(self.manual_download_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.manual_download_dir)
                    
                    # Get file info
                    stat = os.stat(file_path)
                    file_ext = Path(file).suffix.lower()
                    
                    file_info = {
                        'name': file,
                        'path': relative_path,
                        'full_path': file_path,
                        'size': stat.st_size,
                        'extension': file_ext,
                        'modified': stat.st_mtime
                    }
                    
                    analysis['files_found'].append(file_info)
                    analysis['total_size'] += stat.st_size
                    
                    # Count file types
                    if file_ext in analysis['file_types']:
                        analysis['file_types'][file_ext] += 1
                    else:
                        analysis['file_types'][file_ext] = 1
                    
                    print(f"  📄 {relative_path} ({stat.st_size} bytes)")
            
            print(f"\n📊 Summary: {len(analysis['files_found'])} files, {analysis['total_size']} total bytes")
            print(f"File types: {analysis['file_types']}")
            
            self.file_analysis = analysis
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing files: {e}")
            return {}
    
    def discover_pipeline_scripts(self):
        """Discover all Python scripts in pipeline directories"""
        print("🔍 Discovering pipeline scripts...")
        
        scripts = []
        
        for pipeline_dir in self.pipeline_dirs:
            full_dir = os.path.join(self.base_dir, pipeline_dir)
            
            if not os.path.exists(full_dir):
                print(f"⚠️ Directory not found: {pipeline_dir}")
                continue
            
            for root, dirs, files in os.walk(full_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.base_dir)
                        
                        scripts.append({
                            'name': file,
                            'relative_path': relative_path,
                            'full_path': file_path,
                            'directory': pipeline_dir,
                            'size': os.path.getsize(file_path)
                        })
        
        print(f"📋 Found {len(scripts)} Python scripts in pipeline directories")
        
        return scripts
    
    
    def analyze_script_imports(self, script_path):
        """Analyze imports in a script to understand dependencies"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = {
                'standard_library': [],
                'third_party': [],
                'local_imports': [],
                'relative_imports': []
            }
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                if line.startswith('import ') or line.startswith('from '):
                    # Simple import analysis
                    if line.startswith('from .') or line.startswith('from ..'):
                        imports['relative_imports'].append(line)
                    elif any(lib in line for lib in ['pandas', 'numpy', 'sklearn', 'joblib', 'psycopg2']):
                        imports['third_party'].append(line)
                    elif any(lib in line for lib in ['os', 'sys', 'json', 'time', 'datetime']):
                        imports['standard_library'].append(line)
                    else:
                        imports['local_imports'].append(line)
            
            return imports
            
        except Exception as e:
            print(f"❌ Error analyzing imports in {script_path}: {e}")
            return {}
    
    
    def test_script_execution(self, script_path):
        """Test if a script can be executed without errors"""
        print(f"🧪 Testing script execution: {os.path.basename(script_path)}")
        
        try:
            # Just check syntax by compiling
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, script_path, 'exec')
            
            return {
                'syntax_valid': True,
                'can_compile': True,
                'error': None
            }
            
        except SyntaxError as e:
            return {
                'syntax_valid': False,
                'can_compile': False,
                'error': f"Syntax error: {e}"
            }
        except Exception as e:
            return {
                'syntax_valid': True,
                'can_compile': False,
                'error': f"Compilation error: {e}"
            }
    
    
    def check_script_references(self, script_path):
        """Check if other scripts reference this script"""
        script_name = os.path.basename(script_path)
        references = []
        
        # Search for references in other scripts
        for pipeline_dir in self.pipeline_dirs:
            full_dir = os.path.join(self.base_dir, pipeline_dir)
            
            if not os.path.exists(full_dir):
                continue
                
            for root, dirs, files in os.walk(full_dir):
                for file in files:
                    if file.endswith('.py') and file != script_name:
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if script_name.replace('.py', '') in content:
                                references.append({
                                    'referencing_script': file,
                                    'referencing_path': os.path.relpath(file_path, self.base_dir)
                                })
                        except:
                            continue
        
        return references
    
    def run_comprehensive_analysis(self):
        """Run comprehensive analysis of all pipeline components"""
        print("🎯 Running Comprehensive Pipeline Script Analysis")
        print("=" * 60)
        
        results = {
            'analysis_timestamp': time.time(),
            'manual_downloads': {},
            'pipeline_scripts': [],
            'script_analysis': {},
            'usage_summary': {},
            'recommendations': []
        }
        
        # 1. Analyze manual downloads
        print("\n1️⃣ Manual Downloads Analysis")
        print("-" * 30)
        results['manual_downloads'] = self.analyze_manual_downloads()
        
        # 2. Discover pipeline scripts
        print("\n2️⃣ Pipeline Scripts Discovery")
        print("-" * 30)
        scripts = self.discover_pipeline_scripts()
        results['pipeline_scripts'] = scripts
        
        # 3. Analyze each script
        print("\n3️⃣ Individual Script Analysis")
        print("-" * 30)
        
        for script in scripts:
            script_path = script['full_path']
            script_name = script['name']
            
            print(f"\n🔍 Analyzing: {script['relative_path']}")
            
            analysis = {
                'script_info': script,
                'imports': self.analyze_script_imports(script_path),
                'execution_test': self.test_script_execution(script_path),
                'references': self.check_script_references(script_path),
                'usage_score': 0
            }
            
            # Calculate usage score
            score = 0
            if analysis['execution_test']['syntax_valid']:
                score += 10
            if analysis['execution_test']['can_compile']:
                score += 10
            if len(analysis['references']) > 0:
                score += len(analysis['references']) * 5
            if len(analysis['imports']['local_imports']) > 0:
                score += 5
            
            analysis['usage_score'] = score
            
            results['script_analysis'][script_name] = analysis
            
            # Print quick summary
            status = "✅" if analysis['execution_test']['syntax_valid'] else "❌"
            refs = len(analysis['references'])
            print(f"  {status} Score: {score}, References: {refs}")
        
        # 4. Generate usage summary
        print("\n4️⃣ Usage Summary")
        print("-" * 30)
        
        # Sort scripts by usage score
        sorted_scripts = sorted(
            results['script_analysis'].items(), 
            key=lambda x: x[1]['usage_score'], 
            reverse=True
        )
        
        results['usage_summary'] = {
            'high_usage': [s for s in sorted_scripts if s[1]['usage_score'] >= 20],
            'medium_usage': [s for s in sorted_scripts if 10 <= s[1]['usage_score'] < 20],
            'low_usage': [s for s in sorted_scripts if s[1]['usage_score'] < 10],
            'total_scripts': len(scripts)
        }
        
        print(f"📊 High usage scripts: {len(results['usage_summary']['high_usage'])}")
        print(f"📊 Medium usage scripts: {len(results['usage_summary']['medium_usage'])}")
        print(f"📊 Low usage scripts: {len(results['usage_summary']['low_usage'])}")
        
        # 5. Generate recommendations
        print("\n5️⃣ Recommendations")
        print("-" * 30)
        
        recommendations = []
        
        # Files to process
        if results['manual_downloads'].get('files_found'):
            file_count = len(results['manual_downloads']['files_found'])
            recommendations.append(f"Process {file_count} files in manual_download directory")
        
        # High priority scripts
        high_usage = results['usage_summary']['high_usage']
        if high_usage:
            script_names = [s[0] for s in high_usage[:3]]
            recommendations.append(f"Focus on high-usage scripts: {', '.join(script_names)}")
        
        # Scripts with syntax errors
        broken_scripts = [
            name for name, analysis in results['script_analysis'].items()
            if not analysis['execution_test']['syntax_valid']
        ]
        if broken_scripts:
            recommendations.append(f"Fix syntax errors in: {', '.join(broken_scripts)}")
        
        results['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"💡 {rec}")
        
        # Save comprehensive report
        report_file = os.path.join(
            self.base_dir, 
            "monitoring/analysis_logs", 
            f"pipeline_analysis_{int(time.time())}.json"
        )
        
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Comprehensive report saved to: {report_file}")
        
        # Generate analyzer report
        analyzer_report = self.analyzer.generate_report()
        print(f"\n📊 Function Analysis: {analyzer_report['summary']['total_function_calls']} calls tracked")
        
        return results

def main():
    """Main function"""
    analyzer = PipelineScriptAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    print("\n" + "="*60)
    print("🎉 PIPELINE SCRIPT ANALYSIS COMPLETE")
    print("="*60)
    
    return results

if __name__ == "__main__":
    main()
