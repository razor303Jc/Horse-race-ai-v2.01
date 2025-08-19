#!/usr/bin/env python3
"""
Advanced Code Modularity and Refactoring Tool for Horse Racing AI V2.03
Provides automated refactoring suggestions and modularity improvements
"""

import os
import sys
import ast
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass
import logging
from collections import defaultdict, Counter
import importlib.util


@dataclass
class RefactoringRecommendation:
    """Refactoring recommendation details"""
    file_path: str
    line_number: int
    refactoring_type: str
    description: str
    before_code: str
    after_code: str
    benefit: str
    complexity_reduction: float
    risk_level: str


@dataclass
class ModularityMetrics:
    """Modularity analysis metrics"""
    cohesion_score: float
    coupling_score: float
    interface_segregation: float
    dependency_inversion: float
    single_responsibility: float
    overall_modularity: float


@dataclass
class DependencyInfo:
    """Dependency analysis information"""
    from_module: str
    to_module: str
    dependency_type: str
    usage_count: int
    is_circular: bool
    strength: str


class CohesionAnalyzer:
    """Analyze module cohesion"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze cohesion of a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Analyze classes
            class_cohesion = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    cohesion = self._analyze_class_cohesion(node)
                    class_cohesion[node.name] = cohesion
            
            # Analyze module cohesion
            module_cohesion = self._analyze_module_cohesion(tree)
            
            return {
                'file_path': file_path,
                'module_cohesion': module_cohesion,
                'class_cohesion': class_cohesion,
                'average_cohesion': self._calculate_average_cohesion(class_cohesion, module_cohesion)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing cohesion for {file_path}: {e}")
            return {}
    
    def _analyze_class_cohesion(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze cohesion within a class"""
        methods = []
        attributes = set()
        method_attribute_usage = defaultdict(set)
        
        # Extract methods and attributes
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append(node.name)
                
                # Find attribute usage in method
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute):
                        if isinstance(child.value, ast.Name) and child.value.id == 'self':
                            attributes.add(child.attr)
                            method_attribute_usage[node.name].add(child.attr)
            
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            attributes.add(target.attr)
        
        # Calculate LCOM (Lack of Cohesion of Methods)
        lcom = self._calculate_lcom(methods, attributes, method_attribute_usage)
        
        # Calculate cohesion score (0-100, higher is better)
        cohesion_score = max(0, 100 - (lcom * 10))
        
        return {
            'methods_count': len(methods),
            'attributes_count': len(attributes),
            'lcom': lcom,
            'cohesion_score': cohesion_score,
            'method_attribute_usage': dict(method_attribute_usage)
        }
    
    def _calculate_lcom(self, methods: List[str], attributes: Set[str], usage: Dict[str, Set[str]]) -> float:
        """Calculate Lack of Cohesion of Methods metric"""
        if len(methods) <= 1 or len(attributes) == 0:
            return 0
        
        # Count method pairs that don't share attributes
        non_sharing_pairs = 0
        sharing_pairs = 0
        
        for i, method1 in enumerate(methods):
            for method2 in methods[i+1:]:
                attrs1 = usage.get(method1, set())
                attrs2 = usage.get(method2, set())
                
                if attrs1.intersection(attrs2):
                    sharing_pairs += 1
                else:
                    non_sharing_pairs += 1
        
        total_pairs = len(methods) * (len(methods) - 1) // 2
        
        if total_pairs == 0:
            return 0
        
        return max(0, (non_sharing_pairs - sharing_pairs) / total_pairs)
    
    def _analyze_module_cohesion(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze module-level cohesion"""
        functions = []
        classes = []
        global_vars = set()
        
        # Extract module elements
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        global_vars.add(target.id)
        
        # Analyze relationships between functions
        function_calls = self._analyze_function_calls(tree)
        
        # Calculate module cohesion based on internal vs external dependencies
        internal_calls = sum(1 for call in function_calls if call in functions)
        total_calls = len(function_calls)
        
        module_cohesion = (internal_calls / total_calls * 100) if total_calls > 0 else 100
        
        return {
            'functions_count': len(functions),
            'classes_count': len(classes),
            'global_variables_count': len(global_vars),
            'internal_function_calls': internal_calls,
            'total_function_calls': total_calls,
            'cohesion_score': module_cohesion
        }
    
    def _analyze_function_calls(self, tree: ast.AST) -> List[str]:
        """Extract function calls from AST"""
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        
        return calls
    
    def _calculate_average_cohesion(self, class_cohesion: Dict[str, Any], module_cohesion: Dict[str, Any]) -> float:
        """Calculate average cohesion score for the file"""
        class_scores = [data['cohesion_score'] for data in class_cohesion.values()]
        module_score = module_cohesion.get('cohesion_score', 0)
        
        all_scores = class_scores + [module_score]
        return sum(all_scores) / len(all_scores) if all_scores else 0


class CouplingAnalyzer:
    """Analyze coupling between modules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze coupling across the entire project"""
        try:
            python_files = self._discover_python_files(project_path)
            
            # Build dependency graph
            dependencies = []
            import_graph = defaultdict(list)
            
            for file_path in python_files:
                file_dependencies = self._analyze_file_dependencies(file_path)
                dependencies.extend(file_dependencies)
                
                for dep in file_dependencies:
                    import_graph[dep.from_module].append(dep.to_module)
            
            # Detect circular dependencies
            circular_deps = self._detect_circular_dependencies(import_graph)
            
            # Calculate coupling metrics
            coupling_metrics = self._calculate_coupling_metrics(dependencies)
            
            return {
                'total_files': len(python_files),
                'total_dependencies': len(dependencies),
                'circular_dependencies': circular_deps,
                'coupling_metrics': coupling_metrics,
                'dependency_graph': dict(import_graph),
                'high_coupling_modules': self._identify_high_coupling_modules(dependencies)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing coupling: {e}")
            return {}
    
    def _discover_python_files(self, project_path: str) -> List[str]:
        """Discover Python files in project"""
        python_files = []
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv']]
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _analyze_file_dependencies(self, file_path: str) -> List[DependencyInfo]:
        """Analyze dependencies for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            dependencies = []
            
            # Get module name from file path
            module_name = self._get_module_name(file_path)
            
            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep = DependencyInfo(
                            from_module=module_name,
                            to_module=alias.name,
                            dependency_type='import',
                            usage_count=1,
                            is_circular=False,
                            strength='weak'
                        )
                        dependencies.append(dep)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep = DependencyInfo(
                            from_module=module_name,
                            to_module=node.module,
                            dependency_type='from_import',
                            usage_count=1,
                            is_circular=False,
                            strength='medium'
                        )
                        dependencies.append(dep)
            
            return dependencies
            
        except Exception as e:
            self.logger.warning(f"Error analyzing dependencies for {file_path}: {e}")
            return []
    
    def _get_module_name(self, file_path: str) -> str:
        """Convert file path to module name"""
        # Remove .py extension and convert slashes to dots
        module_name = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        # Remove leading dots
        while module_name.startswith('.'):
            module_name = module_name[1:]
        return module_name
    
    def _detect_circular_dependencies(self, import_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in import_graph.get(node, []):
                if dfs(neighbor, path + [node]):
                    pass  # Continue to find all cycles
            
            rec_stack.remove(node)
            return False
        
        for node in import_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _calculate_coupling_metrics(self, dependencies: List[DependencyInfo]) -> Dict[str, Any]:
        """Calculate various coupling metrics"""
        if not dependencies:
            return {}
        
        # Count dependencies per module
        afferent_coupling = defaultdict(int)  # Ca: modules that depend on this module
        efferent_coupling = defaultdict(int)  # Ce: modules this module depends on
        
        for dep in dependencies:
            efferent_coupling[dep.from_module] += 1
            afferent_coupling[dep.to_module] += 1
        
        # Calculate instability (I = Ce / (Ca + Ce))
        instability = {}
        for module in set(afferent_coupling.keys()) | set(efferent_coupling.keys()):
            ca = afferent_coupling[module]
            ce = efferent_coupling[module]
            if ca + ce > 0:
                instability[module] = ce / (ca + ce)
            else:
                instability[module] = 0
        
        # Calculate average coupling
        avg_afferent = sum(afferent_coupling.values()) / len(afferent_coupling) if afferent_coupling else 0
        avg_efferent = sum(efferent_coupling.values()) / len(efferent_coupling) if efferent_coupling else 0
        
        return {
            'afferent_coupling': dict(afferent_coupling),
            'efferent_coupling': dict(efferent_coupling),
            'instability': instability,
            'average_afferent_coupling': avg_afferent,
            'average_efferent_coupling': avg_efferent,
            'highly_coupled_threshold': 5
        }
    
    def _identify_high_coupling_modules(self, dependencies: List[DependencyInfo]) -> List[Dict[str, Any]]:
        """Identify modules with high coupling"""
        coupling_counts = defaultdict(int)
        
        for dep in dependencies:
            coupling_counts[dep.from_module] += 1
            coupling_counts[dep.to_module] += 1
        
        # Sort by coupling count
        sorted_modules = sorted(coupling_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 10 highly coupled modules
        return [
            {'module': module, 'coupling_count': count}
            for module, count in sorted_modules[:10]
            if count > 3  # Threshold for high coupling
        ]


class RefactoringEngine:
    """Advanced refactoring recommendation engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_file(self, file_path: str) -> List[RefactoringRecommendation]:
        """Generate refactoring recommendations for a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.splitlines()
            
            recommendations = []
            
            # Analyze different refactoring opportunities
            recommendations.extend(self._detect_long_methods(tree, lines, file_path))
            recommendations.extend(self._detect_large_classes(tree, lines, file_path))
            recommendations.extend(self._detect_parameter_list_issues(tree, lines, file_path))
            recommendations.extend(self._detect_duplicate_code(tree, lines, file_path))
            recommendations.extend(self._detect_god_objects(tree, lines, file_path))
            recommendations.extend(self._detect_feature_envy(tree, lines, file_path))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating refactoring recommendations for {file_path}: {e}")
            return []
    
    def _detect_long_methods(self, tree: ast.AST, lines: List[str], file_path: str) -> List[RefactoringRecommendation]:
        """Detect methods that are too long"""
        recommendations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_lines = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                
                if method_lines > 30:  # Threshold for long method
                    before_code = '\n'.join(lines[node.lineno-1:getattr(node, 'end_lineno', node.lineno)])
                    
                    recommendation = RefactoringRecommendation(
                        file_path=file_path,
                        line_number=node.lineno,
                        refactoring_type="extract_method",
                        description=f"Method '{node.name}' is {method_lines} lines long",
                        before_code=before_code[:200] + "...",  # Truncate for display
                        after_code=self._generate_extract_method_suggestion(node.name),
                        benefit="Improves readability and testability",
                        complexity_reduction=method_lines * 0.1,
                        risk_level="low"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _detect_large_classes(self, tree: ast.AST, lines: List[str], file_path: str) -> List[RefactoringRecommendation]:
        """Detect classes that are too large"""
        recommendations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_lines = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                
                if class_lines > 200 or method_count > 15:
                    before_code = '\n'.join(lines[node.lineno-1:min(node.lineno+9, len(lines))])
                    
                    recommendation = RefactoringRecommendation(
                        file_path=file_path,
                        line_number=node.lineno,
                        refactoring_type="extract_class",
                        description=f"Class '{node.name}' has {method_count} methods and {class_lines} lines",
                        before_code=before_code,
                        after_code=self._generate_extract_class_suggestion(node.name),
                        benefit="Improves single responsibility and maintainability",
                        complexity_reduction=class_lines * 0.05,
                        risk_level="medium"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _detect_parameter_list_issues(self, tree: ast.AST, lines: List[str], file_path: str) -> List[RefactoringRecommendation]:
        """Detect methods with too many parameters"""
        recommendations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                
                if param_count > 5:  # Threshold for too many parameters
                    before_code = lines[node.lineno-1] if node.lineno <= len(lines) else ""
                    
                    recommendation = RefactoringRecommendation(
                        file_path=file_path,
                        line_number=node.lineno,
                        refactoring_type="introduce_parameter_object",
                        description=f"Method '{node.name}' has {param_count} parameters",
                        before_code=before_code,
                        after_code=self._generate_parameter_object_suggestion(node.name, node.args.args),
                        benefit="Reduces parameter coupling and improves readability",
                        complexity_reduction=param_count * 0.2,
                        risk_level="low"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _detect_duplicate_code(self, tree: ast.AST, lines: List[str], file_path: str) -> List[RefactoringRecommendation]:
        """Detect duplicate code blocks"""
        recommendations = []
        
        # Simple duplicate detection based on similar line patterns
        line_groups = defaultdict(list)
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and len(stripped) > 10:
                line_groups[stripped].append(i + 1)
        
        for line_content, line_numbers in line_groups.items():
            if len(line_numbers) > 1:
                recommendation = RefactoringRecommendation(
                    file_path=file_path,
                    line_number=line_numbers[0],
                    refactoring_type="extract_method",
                    description=f"Duplicate code found at lines {line_numbers}",
                    before_code=line_content,
                    after_code=self._generate_extract_common_method_suggestion(),
                    benefit="Reduces duplication and improves maintainability",
                    complexity_reduction=len(line_numbers) * 0.3,
                    risk_level="low"
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _detect_god_objects(self, tree: ast.AST, lines: List[str], file_path: str) -> List[RefactoringRecommendation]:
        """Detect god objects (classes with too many responsibilities)"""
        recommendations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count different types of responsibilities
                method_categories = defaultdict(int)
                
                for method_node in node.body:
                    if isinstance(method_node, ast.FunctionDef):
                        method_name = method_node.name.lower()
                        
                        # Categorize methods by naming patterns
                        if any(word in method_name for word in ['get', 'fetch', 'retrieve', 'load']):
                            method_categories['data_access'] += 1
                        elif any(word in method_name for word in ['save', 'store', 'write', 'update']):
                            method_categories['data_persistence'] += 1
                        elif any(word in method_name for word in ['validate', 'check', 'verify']):
                            method_categories['validation'] += 1
                        elif any(word in method_name for word in ['format', 'convert', 'transform']):
                            method_categories['formatting'] += 1
                        else:
                            method_categories['business_logic'] += 1
                
                # If class has more than 3 categories with significant methods
                significant_categories = [cat for cat, count in method_categories.items() if count >= 3]
                
                if len(significant_categories) > 3:
                    recommendation = RefactoringRecommendation(
                        file_path=file_path,
                        line_number=node.lineno,
                        refactoring_type="extract_class",
                        description=f"Class '{node.name}' has multiple responsibilities: {', '.join(significant_categories)}",
                        before_code=f"class {node.name}:",
                        after_code=self._generate_responsibility_separation_suggestion(node.name, significant_categories),
                        benefit="Improves single responsibility principle",
                        complexity_reduction=len(significant_categories) * 2.0,
                        risk_level="high"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _detect_feature_envy(self, tree: ast.AST, lines: List[str], file_path: str) -> List[RefactoringRecommendation]:
        """Detect feature envy (methods using other classes more than their own)"""
        recommendations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count attribute accesses
                self_accesses = 0
                other_accesses = 0
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute):
                        if isinstance(child.value, ast.Name):
                            if child.value.id == 'self':
                                self_accesses += 1
                            else:
                                other_accesses += 1
                
                # If method uses other objects more than self
                if other_accesses > self_accesses and other_accesses > 3:
                    recommendation = RefactoringRecommendation(
                        file_path=file_path,
                        line_number=node.lineno,
                        refactoring_type="move_method",
                        description=f"Method '{node.name}' uses other objects more than self ({other_accesses} vs {self_accesses})",
                        before_code=f"def {node.name}(self, ...):",
                        after_code="# Consider moving this method to the class it uses most",
                        benefit="Improves cohesion by placing methods where they belong",
                        complexity_reduction=1.0,
                        risk_level="medium"
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_extract_method_suggestion(self, method_name: str) -> str:
        """Generate suggestion for extract method refactoring"""
        return f"""# Split {method_name} into smaller methods:
def {method_name}(self):
    self._prepare_data()
    self._process_data()
    self._finalize_result()

def _prepare_data(self):
    # Extract preparation logic here
    pass

def _process_data(self):
    # Extract main processing logic here
    pass

def _finalize_result(self):
    # Extract finalization logic here
    pass"""
    
    def _generate_extract_class_suggestion(self, class_name: str) -> str:
        """Generate suggestion for extract class refactoring"""
        return f"""# Split {class_name} into focused classes:
class {class_name}Core:
    # Core responsibilities only
    pass

class {class_name}Helper:
    # Supporting functionality
    pass

class {class_name}Manager:
    # Coordination logic
    def __init__(self):
        self.core = {class_name}Core()
        self.helper = {class_name}Helper()"""
    
    def _generate_parameter_object_suggestion(self, method_name: str, params: List[ast.arg]) -> str:
        """Generate suggestion for parameter object refactoring"""
        param_names = [param.arg for param in params if param.arg != 'self']
        
        return f"""# Create parameter object for {method_name}:
@dataclass
class {method_name.title()}Parameters:
    {': Any' + chr(10) + '    '.join(param_names)}: Any

def {method_name}(self, params: {method_name.title()}Parameters):
    # Use params.{param_names[0] if param_names else 'attribute'} instead of individual parameters
    pass"""
    
    def _generate_extract_common_method_suggestion(self) -> str:
        """Generate suggestion for extracting common method"""
        return """# Extract duplicate code into common method:
def _common_operation(self, data):
    # Move duplicate logic here
    return processed_data

# Replace duplicate code with:
result = self._common_operation(input_data)"""
    
    def _generate_responsibility_separation_suggestion(self, class_name: str, categories: List[str]) -> str:
        """Generate suggestion for separating responsibilities"""
        suggestions = []
        for category in categories:
            class_suffix = ''.join(word.capitalize() for word in category.split('_'))
            suggestions.append(f"class {class_name}{class_suffix}:")
            suggestions.append(f"    # Handle {category.replace('_', ' ')} responsibilities")
            suggestions.append("")
        
        return '\n'.join(suggestions)


class ModularityAnalyzer:
    """Comprehensive modularity analysis"""
    
    def __init__(self, project_root: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "modularity"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzers
        self.cohesion_analyzer = CohesionAnalyzer()
        self.coupling_analyzer = CouplingAnalyzer()
        self.refactoring_engine = RefactoringEngine()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.project_root / "logs" / "modularity.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive modularity analysis"""
        self.logger.info("Starting comprehensive modularity analysis...")
        
        # Discover Python files
        python_files = self._discover_python_files()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'total_files': len(python_files),
            'cohesion_analysis': {},
            'coupling_analysis': {},
            'refactoring_recommendations': [],
            'modularity_metrics': {},
            'improvement_roadmap': []
        }
        
        # Cohesion analysis
        self.logger.info("Analyzing cohesion...")
        cohesion_results = []
        for file_path in python_files:
            cohesion = self.cohesion_analyzer.analyze_file(file_path)
            if cohesion:
                cohesion_results.append(cohesion)
        results['cohesion_analysis'] = cohesion_results
        
        # Coupling analysis
        self.logger.info("Analyzing coupling...")
        coupling_results = self.coupling_analyzer.analyze_project(str(self.project_root))
        results['coupling_analysis'] = coupling_results
        
        # Refactoring recommendations
        self.logger.info("Generating refactoring recommendations...")
        all_recommendations = []
        for file_path in python_files:
            recommendations = self.refactoring_engine.analyze_file(file_path)
            all_recommendations.extend(recommendations)
        
        # Sort by complexity reduction potential
        all_recommendations.sort(key=lambda x: x.complexity_reduction, reverse=True)
        results['refactoring_recommendations'] = [rec.__dict__ for rec in all_recommendations]
        
        # Calculate overall modularity metrics
        results['modularity_metrics'] = self._calculate_modularity_metrics(results)
        
        # Generate improvement roadmap
        results['improvement_roadmap'] = self._generate_improvement_roadmap(results)
        
        # Save results
        self._save_analysis_results(results)
        
        self.logger.info("Modularity analysis completed")
        return results
    
    def _discover_python_files(self) -> List[str]:
        """Discover Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv']]
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _calculate_modularity_metrics(self, results: Dict[str, Any]) -> ModularityMetrics:
        """Calculate overall modularity metrics"""
        cohesion_scores = []
        for analysis in results['cohesion_analysis']:
            cohesion_scores.append(analysis.get('average_cohesion', 0))
        
        avg_cohesion = sum(cohesion_scores) / len(cohesion_scores) if cohesion_scores else 0
        
        # Coupling metrics
        coupling_data = results['coupling_analysis']
        avg_coupling = coupling_data.get('coupling_metrics', {}).get('average_efferent_coupling', 0)
        
        # Normalize coupling score (lower coupling is better)
        coupling_score = max(0, 100 - (avg_coupling * 10))
        
        # Calculate other metrics
        interface_segregation = self._calculate_interface_segregation(results)
        dependency_inversion = self._calculate_dependency_inversion(results)
        single_responsibility = self._calculate_single_responsibility(results)
        
        # Overall modularity score
        overall_modularity = (
            avg_cohesion * 0.3 +
            coupling_score * 0.3 +
            interface_segregation * 0.15 +
            dependency_inversion * 0.15 +
            single_responsibility * 0.1
        )
        
        return ModularityMetrics(
            cohesion_score=avg_cohesion,
            coupling_score=coupling_score,
            interface_segregation=interface_segregation,
            dependency_inversion=dependency_inversion,
            single_responsibility=single_responsibility,
            overall_modularity=overall_modularity
        )
    
    def _calculate_interface_segregation(self, results: Dict[str, Any]) -> float:
        """Calculate interface segregation score"""
        # Simplified metric based on class size and method count
        class_sizes = []
        
        for analysis in results['cohesion_analysis']:
            for class_name, class_data in analysis.get('class_cohesion', {}).items():
                method_count = class_data.get('methods_count', 0)
                # Smaller interfaces are better
                interface_score = max(0, 100 - (method_count * 5))
                class_sizes.append(interface_score)
        
        return sum(class_sizes) / len(class_sizes) if class_sizes else 100
    
    def _calculate_dependency_inversion(self, results: Dict[str, Any]) -> float:
        """Calculate dependency inversion score"""
        # Simplified metric based on import patterns
        # Higher score for fewer concrete dependencies
        total_deps = results['coupling_analysis'].get('total_dependencies', 0)
        total_files = results['total_files']
        
        if total_files == 0:
            return 100
        
        deps_per_file = total_deps / total_files
        return max(0, 100 - (deps_per_file * 5))
    
    def _calculate_single_responsibility(self, results: Dict[str, Any]) -> float:
        """Calculate single responsibility score"""
        # Based on refactoring recommendations related to responsibility
        responsibility_issues = [
            rec for rec in results['refactoring_recommendations']
            if rec['refactoring_type'] in ['extract_class', 'move_method']
        ]
        
        total_recommendations = len(results['refactoring_recommendations'])
        if total_recommendations == 0:
            return 100
        
        responsibility_ratio = len(responsibility_issues) / total_recommendations
        return max(0, 100 - (responsibility_ratio * 100))
    
    def _generate_improvement_roadmap(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement roadmap based on analysis"""
        roadmap = []
        
        # Priority 1: Critical refactoring
        critical_recommendations = [
            rec for rec in results['refactoring_recommendations']
            if rec['risk_level'] == 'low' and rec['complexity_reduction'] > 5.0
        ]
        
        if critical_recommendations:
            roadmap.append({
                'phase': 1,
                'title': 'Critical Refactoring',
                'description': 'Address high-impact, low-risk refactoring opportunities',
                'tasks': [
                    f"Refactor {rec['refactoring_type']} in {rec['file_path'].split('/')[-1]}"
                    for rec in critical_recommendations[:5]
                ],
                'estimated_effort': 'Medium',
                'impact': 'High'
            })
        
        # Priority 2: Coupling reduction
        coupling_issues = results['coupling_analysis'].get('circular_dependencies', [])
        if coupling_issues:
            roadmap.append({
                'phase': 2,
                'title': 'Coupling Reduction',
                'description': 'Break circular dependencies and reduce coupling',
                'tasks': [
                    f"Break circular dependency: {' -> '.join(cycle)}"
                    for cycle in coupling_issues[:3]
                ],
                'estimated_effort': 'High',
                'impact': 'High'
            })
        
        # Priority 3: Cohesion improvement
        low_cohesion_files = [
            analysis for analysis in results['cohesion_analysis']
            if analysis.get('average_cohesion', 0) < 50
        ]
        
        if low_cohesion_files:
            roadmap.append({
                'phase': 3,
                'title': 'Cohesion Improvement',
                'description': 'Improve internal cohesion of classes and modules',
                'tasks': [
                    f"Improve cohesion in {analysis['file_path'].split('/')[-1]}"
                    for analysis in low_cohesion_files[:5]
                ],
                'estimated_effort': 'Medium',
                'impact': 'Medium'
            })
        
        return roadmap
    
    def _save_analysis_results(self, results: Dict[str, Any]):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.reports_dir / f"modularity_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save summary report
        summary_file = self.reports_dir / "modularity_summary.md"
        summary_content = self._generate_summary_report(results)
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        self.logger.info(f"Modularity analysis results saved to {self.reports_dir}")
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown summary report"""
        metrics = results['modularity_metrics']
        
        summary = f"""# Modularity Analysis Summary

**Generated:** {results['timestamp']}  
**Project:** {results['project_root']}  
**Files Analyzed:** {results['total_files']}

## Overall Modularity Score: {metrics['overall_modularity']:.1f}/100

## Key Metrics

| Metric | Score | Grade |
|--------|-------|-------|
| Cohesion | {metrics['cohesion_score']:.1f}/100 | {self._get_grade(metrics['cohesion_score'])} |
| Coupling | {metrics['coupling_score']:.1f}/100 | {self._get_grade(metrics['coupling_score'])} |
| Interface Segregation | {metrics['interface_segregation']:.1f}/100 | {self._get_grade(metrics['interface_segregation'])} |
| Dependency Inversion | {metrics['dependency_inversion']:.1f}/100 | {self._get_grade(metrics['dependency_inversion'])} |
| Single Responsibility | {metrics['single_responsibility']:.1f}/100 | {self._get_grade(metrics['single_responsibility'])} |

## Top Refactoring Recommendations

"""
        
        for i, rec in enumerate(results['refactoring_recommendations'][:5], 1):
            summary += f"""### {i}. {rec['refactoring_type'].replace('_', ' ').title()}
**File:** {rec['file_path'].split('/')[-1]}  
**Line:** {rec['line_number']}  
**Description:** {rec['description']}  
**Benefit:** {rec['benefit']}  
**Complexity Reduction:** {rec['complexity_reduction']:.1f}  
**Risk:** {rec['risk_level'].upper()}

"""
        
        # Add improvement roadmap
        summary += "\n## Improvement Roadmap\n\n"
        for phase in results['improvement_roadmap']:
            summary += f"""### Phase {phase['phase']}: {phase['title']}
**Description:** {phase['description']}  
**Effort:** {phase['estimated_effort']}  
**Impact:** {phase['impact']}

**Tasks:**
"""
            for task in phase['tasks']:
                summary += f"- {task}\n"
            summary += "\n"
        
        return summary
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


def main():
    """Main modularity analysis execution"""
    analyzer = ModularityAnalyzer()
    
    print("🏗️ Comprehensive Modularity and Refactoring Analysis")
    print("=" * 60)
    
    # Run analysis
    results = analyzer.analyze_project()
    
    # Display summary
    metrics = results['modularity_metrics']
    print(f"\n📊 Modularity Metrics:")
    print(f"  Overall Score: {metrics['overall_modularity']:.1f}/100")
    print(f"  Cohesion: {metrics['cohesion_score']:.1f}/100")
    print(f"  Coupling: {metrics['coupling_score']:.1f}/100")
    print(f"  Single Responsibility: {metrics['single_responsibility']:.1f}/100")
    
    print(f"\n🔧 Refactoring Opportunities:")
    print(f"  Total Recommendations: {len(results['refactoring_recommendations'])}")
    
    # Show top recommendations
    top_recs = results['refactoring_recommendations'][:3]
    for i, rec in enumerate(top_recs, 1):
        print(f"  {i}. {rec['refactoring_type'].replace('_', ' ').title()} - {rec['description'][:50]}...")
    
    print(f"\n📝 Reports saved to: {analyzer.reports_dir}")
    print("✅ Modularity analysis completed")


if __name__ == "__main__":
    main()
