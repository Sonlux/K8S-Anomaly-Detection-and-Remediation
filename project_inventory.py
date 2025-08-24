#!/usr/bin/env python3
"""
Project Inventory and Analysis Script
Analyzes current project structure and generates cleanup recommendations
"""

import os
import json
import hashlib
import re
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import subprocess
import sys

class ProjectInventory:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.inventory = {
            "duplicate_files": [],
            "obsolete_files": [],
            "unused_dependencies": [],
            "build_artifacts": [],
            "virtual_environments": [],
            "requirements_files": [],
            "config_files": [],
            "documentation_files": [],
            "cleanup_plan": {}
        }
        
    def analyze_project(self):
        """Run complete project analysis"""
        print("🔍 Starting project inventory analysis...")
        
        self._find_duplicate_files()
        self._identify_build_artifacts()
        self._find_virtual_environments()
        self._analyze_requirements_files()
        self._find_config_files()
        self._identify_obsolete_files()
        self._analyze_documentation()
        self._generate_cleanup_plan()
        
        return self.inventory
    
    def _find_duplicate_files(self):
        """Find duplicate files by content hash"""
        print("📁 Analyzing duplicate files...")
        file_hashes = defaultdict(list)
        
        for file_path in self._get_all_files():
            if self._should_skip_file(file_path):
                continue
            
            # Skip large files to avoid memory issues
            try:
                if file_path.stat().st_size > 50 * 1024 * 1024:  # Skip files > 50MB
                    continue
            except OSError:
                continue
                
            try:
                with open(file_path, 'rb') as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()
                    file_hashes[content_hash].append(str(file_path.relative_to(self.root_path)))
            except (IOError, OSError, PermissionError):
                continue
        
        # Find duplicates
        for hash_val, files in file_hashes.items():
            if len(files) > 1:
                self.inventory["duplicate_files"].append({
                    "hash": hash_val,
                    "files": files,
                    "size": self._get_file_size(files[0])
                }) 
   
    def _identify_build_artifacts(self):
        """Identify build artifacts and temporary files"""
        print("🗑️  Identifying build artifacts...")
        
        artifact_patterns = [
            r'__pycache__',
            r'\.pyc$',
            r'\.pyo$',
            r'\.log$',
            r'\.tmp$',
            r'\.cache',
            r'node_modules',
            r'\.next',
            r'dist/',
            r'build/',
            r'coverage/',
            r'\.pytest_cache',
            r'\.coverage'
        ]
        
        for file_path in self._get_all_files_and_dirs():
            file_str = str(file_path.relative_to(self.root_path))
            
            for pattern in artifact_patterns:
                if re.search(pattern, file_str):
                    self.inventory["build_artifacts"].append({
                        "path": file_str,
                        "type": "directory" if file_path.is_dir() else "file",
                        "size": self._get_path_size(file_path)
                    })
                    break
    
    def _find_virtual_environments(self):
        """Find virtual environment directories"""
        print("🐍 Finding virtual environments...")
        
        venv_indicators = [
            'pyvenv.cfg',
            'Scripts/activate',
            'bin/activate',
            'lib/python'
        ]
        
        for dir_path in self.root_path.rglob('*'):
            if not dir_path.is_dir():
                continue
                
            # Check if directory contains venv indicators
            for indicator in venv_indicators:
                if (dir_path / indicator).exists():
                    self.inventory["virtual_environments"].append({
                        "path": str(dir_path.relative_to(self.root_path)),
                        "size": self._get_path_size(dir_path),
                        "indicator": indicator
                    })
                    break
    
    def _analyze_requirements_files(self):
        """Analyze Python requirements files"""
        print("📦 Analyzing requirements files...")
        
        req_patterns = [
            'requirements*.txt',
            'pyproject.toml',
            'setup.py',
            'Pipfile',
            'poetry.lock'
        ]
        
        all_requirements = {}
        
        for pattern in req_patterns:
            for req_file in self.root_path.rglob(pattern):
                rel_path = str(req_file.relative_to(self.root_path))
                self.inventory["requirements_files"].append(rel_path)
                
                if req_file.name.startswith('requirements') and req_file.suffix == '.txt':
                    try:
                        with open(req_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            packages = self._parse_requirements(content)
                            all_requirements[rel_path] = packages
                    except (IOError, OSError, UnicodeDecodeError):
                        continue
        
        # Find duplicate dependencies across files
        self._find_duplicate_dependencies(all_requirements)
        
        # Analyze for potentially unused dependencies
        self._analyze_unused_dependencies(all_requirements)  
  
    def _find_config_files(self):
        """Find configuration files"""
        print("⚙️  Finding configuration files...")
        
        config_patterns = [
            '*.json',
            '*.yaml',
            '*.yml',
            '*.toml',
            '*.ini',
            '*.cfg',
            '.env*',
            'Dockerfile*',
            'docker-compose*',
            '*.config.js',
            'tsconfig.json',
            'next.config.js',
            'tailwind.config.js'
        ]
        
        for pattern in config_patterns:
            for config_file in self.root_path.rglob(pattern):
                if self._should_skip_file(config_file):
                    continue
                    
                rel_path = str(config_file.relative_to(self.root_path))
                self.inventory["config_files"].append({
                    "path": rel_path,
                    "type": self._classify_config_file(config_file.name),
                    "size": self._get_file_size(rel_path)
                })
    
    def _identify_obsolete_files(self):
        """Identify potentially obsolete files"""
        print("🗂️  Identifying obsolete files...")
        
        obsolete_patterns = [
            r'\.bak$',
            r'\.backup$',
            r'\.old$',
            r'~$',
            r'\.orig$',
            r'\.rej$',
            r'\.swp$',
            r'\.swo$',
            r'Thumbs\.db$',
            r'\.DS_Store$'
        ]
        
        # Also check for files that might be obsolete based on naming
        potential_obsolete = []
        
        for file_path in self._get_all_files():
            file_str = str(file_path.relative_to(self.root_path))
            
            # Check against patterns
            for pattern in obsolete_patterns:
                if re.search(pattern, file_str):
                    self.inventory["obsolete_files"].append({
                        "path": file_str,
                        "reason": f"Matches pattern: {pattern}",
                        "size": self._get_file_size(file_str)
                    })
                    break
            
            # Check for numbered duplicates (file1.py, file2.py, etc.)
            if re.search(r'\d+\.(py|js|ts|md)$', file_str):
                potential_obsolete.append(file_str)
        
        # Add potential obsolete files
        for file_path in potential_obsolete:
            self.inventory["obsolete_files"].append({
                "path": file_path,
                "reason": "Numbered file - potential duplicate",
                "size": self._get_file_size(file_path)
            })
    
    def _analyze_documentation(self):
        """Analyze documentation files"""
        print("📚 Analyzing documentation...")
        
        doc_patterns = ['*.md', '*.rst', '*.txt']
        
        for pattern in doc_patterns:
            for doc_file in self.root_path.rglob(pattern):
                if self._should_skip_file(doc_file):
                    continue
                    
                rel_path = str(doc_file.relative_to(self.root_path))
                self.inventory["documentation_files"].append({
                    "path": rel_path,
                    "size": self._get_file_size(rel_path)
                }) 
   
    def _generate_cleanup_plan(self):
        """Generate comprehensive cleanup plan"""
        print("📋 Generating cleanup plan...")
        
        plan = {
            "safe_to_remove": [],
            "requires_review": [],
            "migration_needed": [],
            "consolidation_opportunities": [],
            "backup_strategy": {},
            "rollback_plan": {}
        }
        
        # Safe to remove: build artifacts
        for artifact in self.inventory["build_artifacts"]:
            plan["safe_to_remove"].append({
                "path": artifact["path"],
                "reason": "Build artifact",
                "action": "delete",
                "risk_level": "low"
            })
        
        # Safe to remove: obsolete files
        for obsolete in self.inventory["obsolete_files"]:
            plan["safe_to_remove"].append({
                "path": obsolete["path"],
                "reason": obsolete["reason"],
                "action": "delete",
                "risk_level": "low"
            })
        
        # Requires review: duplicates
        for dup_group in self.inventory["duplicate_files"]:
            if len(dup_group["files"]) > 1:
                plan["requires_review"].append({
                    "files": dup_group["files"],
                    "reason": "Duplicate content",
                    "action": "review_and_consolidate",
                    "risk_level": "medium",
                    "recommendation": f"Keep {dup_group['files'][0]}, review others"
                })
        
        # Migration needed: scattered source files
        source_files = []
        for file_path in self._get_all_files():
            if file_path.suffix in ['.py', '.js', '.ts', '.tsx']:
                rel_path = str(file_path.relative_to(self.root_path))
                if not any(skip in rel_path for skip in ['node_modules', '__pycache__', '.venv']):
                    source_files.append(rel_path)
        
        # Group by type for migration suggestions
        python_files = [f for f in source_files if f.endswith('.py')]
        js_files = [f for f in source_files if f.endswith(('.js', '.ts', '.tsx'))]
        
        if python_files:
            # Categorize Python files
            backend_files = [f for f in python_files if 'backend/src' in f or 'agents' in f or 'api' in f]
            script_files = [f for f in python_files if f not in backend_files and not f.startswith('test')]
            
            if backend_files:
                plan["migration_needed"].append({
                    "files": backend_files,
                    "target_location": "backend/src/",
                    "reason": "Consolidate Python backend code",
                    "risk_level": "high",
                    "dependencies": "Update import paths, configuration references"
                })
            
            if script_files:
                plan["migration_needed"].append({
                    "files": script_files,
                    "target_location": "backend/scripts/",
                    "reason": "Consolidate utility scripts",
                    "risk_level": "medium"
                })
        
        if js_files:
            frontend_files = [f for f in js_files if 'kubescape' in f or 'src' in f]
            config_files = [f for f in js_files if 'config' in f or f.endswith('.config.js')]
            
            if frontend_files:
                plan["migration_needed"].append({
                    "files": frontend_files,
                    "target_location": "frontend/src/",
                    "reason": "Consolidate frontend code",
                    "risk_level": "high",
                    "dependencies": "Update import paths, build configuration"
                })
            
            if config_files:
                plan["migration_needed"].append({
                    "files": config_files,
                    "target_location": "shared/configs/",
                    "reason": "Centralize configuration files",
                    "risk_level": "medium"
                })
        
        # Consolidation opportunities
        if len(self.inventory["requirements_files"]) > 1:
            plan["consolidation_opportunities"].append({
                "files": self.inventory["requirements_files"],
                "target": "backend/requirements.txt",
                "reason": "Multiple requirements files",
                "action": "merge_and_deduplicate",
                "risk_level": "medium"
            })
        
        if len(self.inventory["virtual_environments"]) > 1:
            plan["consolidation_opportunities"].append({
                "items": [venv["path"] for venv in self.inventory["virtual_environments"]],
                "target": ".venv",
                "reason": "Multiple virtual environments",
                "action": "consolidate_to_single_venv",
                "risk_level": "low"
            })
        
        # Add backup strategy
        plan["backup_strategy"] = {
            "create_backup": True,
            "backup_location": "backup_" + str(int(time.time())),
            "backup_files": ["requirements*.txt", "package*.json", "*.config.js"],
            "git_commit": "Create commit before cleanup operations"
        }
        
        # Add rollback plan
        plan["rollback_plan"] = {
            "git_reset": "Use git reset --hard to revert changes",
            "backup_restore": "Restore from backup directory if needed",
            "dependency_restore": "Reinstall from backed up requirements files"
        }
        
        self.inventory["cleanup_plan"] = plan
    
    def _get_all_files(self):
        """Get all files in the project"""
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                yield file_path
    
    def _get_all_files_and_dirs(self):
        """Get all files and directories"""
        for path in self.root_path.rglob('*'):
            yield path
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '.git/',
            'node_modules/',
            '__pycache__/',
            '.venv/',
            'venv/',
            '.pytest_cache/',
            '.coverage'
        ]
        
        path_str = str(file_path.relative_to(self.root_path))
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(self.root_path / file_path)
        except OSError:
            return 0
    
    def _get_path_size(self, path: Path) -> int:
        """Get total size of path (file or directory)"""
        if path.is_file():
            try:
                return path.stat().st_size
            except OSError:
                return 0
        elif path.is_dir():
            total = 0
            try:
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
            except OSError:
                pass
            return total
        return 0
    
    def _parse_requirements(self, content: str) -> List[str]:
        """Parse requirements.txt content"""
        packages = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Extract package name (before ==, >=, etc.)
                package = re.split(r'[>=<!=]', line)[0].strip()
                if package:
                    packages.append(package)
        return packages
    
    def _find_duplicate_dependencies(self, all_requirements: Dict[str, List[str]]):
        """Find duplicate dependencies across requirements files"""
        if len(all_requirements) <= 1:
            return
        
        all_packages = set()
        duplicates = defaultdict(list)
        
        for file_path, packages in all_requirements.items():
            for package in packages:
                if package in all_packages:
                    duplicates[package].append(file_path)
                else:
                    all_packages.add(package)
                    duplicates[package] = [file_path]
        
        # Filter to only actual duplicates
        actual_duplicates = {pkg: files for pkg, files in duplicates.items() if len(files) > 1}
        
        if actual_duplicates:
            if "duplicate_dependencies" not in self.inventory:
                self.inventory["duplicate_dependencies"] = {}
            self.inventory["duplicate_dependencies"] = actual_duplicates
    
    def _analyze_unused_dependencies(self, all_requirements: Dict[str, List[str]]):
        """Analyze for potentially unused dependencies"""
        print("🔍 Analyzing for unused dependencies...")
        
        # Get all Python files to check imports
        python_files = []
        for file_path in self._get_all_files():
            if file_path.suffix == '.py' and not self._should_skip_file(file_path):
                python_files.append(file_path)
        
        # Extract all imports from Python files
        used_packages = set()
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    imports = self._extract_imports(content)
                    used_packages.update(imports)
            except (IOError, OSError, UnicodeDecodeError):
                continue
        
        # Check which requirements might be unused
        potentially_unused = []
        for req_file, packages in all_requirements.items():
            for package in packages:
                # Normalize package names for comparison
                normalized_package = package.lower().replace('-', '_')
                if not any(normalized_package in used_pkg.lower() for used_pkg in used_packages):
                    potentially_unused.append({
                        "package": package,
                        "file": req_file,
                        "reason": "No import found in Python files"
                    })
        
        if potentially_unused:
            self.inventory["unused_dependencies"] = potentially_unused
    
    def _extract_imports(self, content: str) -> Set[str]:
        """Extract import statements from Python code"""
        imports = set()
        
        # Match import statements
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.update(matches)
        
        return imports
    
    def _classify_config_file(self, filename: str) -> str:
        """Classify configuration file type"""
        if 'docker' in filename.lower():
            return 'docker'
        elif filename in ['package.json', 'package-lock.json']:
            return 'npm'
        elif 'requirements' in filename:
            return 'python'
        elif filename.endswith('.config.js'):
            return 'build_config'
        elif filename.startswith('.env'):
            return 'environment'
        elif filename.endswith(('.yaml', '.yml')):
            return 'yaml_config'
        else:
            return 'general_config'
    
    def save_report(self, output_file: str = "project_inventory_report.json"):
        """Save inventory report to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.inventory, f, indent=2)
        print(f"📊 Report saved to {output_file}")
    
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*70)
        print("📊 PROJECT INVENTORY SUMMARY")
        print("="*70)
        
        # File analysis summary
        print(f"� Dupulicate files found: {len(self.inventory['duplicate_files'])}")
        if self.inventory['duplicate_files']:
            total_duplicates = sum(len(dup['files']) - 1 for dup in self.inventory['duplicate_files'])
            print(f"   → {total_duplicates} files can be removed")
        
        print(f"� ️  Build artifacts: {len(self.inventory['build_artifacts'])}")
        if self.inventory['build_artifacts']:
            artifact_size = sum(item.get('size', 0) for item in self.inventory['build_artifacts'])
            print(f"   → {artifact_size / (1024*1024):.1f} MB can be cleaned")
        
        print(f"🐍 Virtual environments: {len(self.inventory['virtual_environments'])}")
        if len(self.inventory['virtual_environments']) > 1:
            print(f"   → {len(self.inventory['virtual_environments']) - 1} can be consolidated")
        
        print(f"📦 Requirements files: {len(self.inventory['requirements_files'])}")
        if len(self.inventory['requirements_files']) > 1:
            print(f"   → Can be consolidated into single file")
        
        print(f"⚙️  Configuration files: {len(self.inventory['config_files'])}")
        print(f"🗂️  Potentially obsolete files: {len(self.inventory['obsolete_files'])}")
        print(f"📚 Documentation files: {len(self.inventory['documentation_files'])}")
        
        # Dependencies analysis
        if 'duplicate_dependencies' in self.inventory and self.inventory['duplicate_dependencies']:
            print(f"🔄 Duplicate dependencies: {len(self.inventory['duplicate_dependencies'])} packages")
        
        if 'unused_dependencies' in self.inventory and self.inventory['unused_dependencies']:
            print(f"❓ Potentially unused dependencies: {len(self.inventory['unused_dependencies'])} packages")
        
        # Cleanup plan summary
        plan = self.inventory["cleanup_plan"]
        print(f"\n🧹 CLEANUP RECOMMENDATIONS:")
        print(f"   ✅ Safe to remove: {len(plan['safe_to_remove'])} items")
        print(f"   ⚠️  Requires review: {len(plan['requires_review'])} items")
        print(f"   📦 Migration needed: {len(plan['migration_needed'])} groups")
        print(f"   🔄 Consolidation opportunities: {len(plan['consolidation_opportunities'])} items")
        
        # Risk assessment
        high_risk_items = sum(1 for group in plan['migration_needed'] if group.get('risk_level') == 'high')
        if high_risk_items > 0:
            print(f"\n⚠️  WARNING: {high_risk_items} high-risk migration operations identified")
            print("   → Backup recommended before proceeding")
        
        print(f"\n💾 Backup strategy: {plan['backup_strategy']['create_backup']}")
        print(f"🔄 Rollback plan: Available")
        
        # Next steps
        print(f"\n📋 NEXT STEPS:")
        print("1. Review the detailed report in 'project_inventory_report.json'")
        print("2. Create a backup before making changes")
        print("3. Start with safe-to-remove items")
        print("4. Review duplicates and consolidation opportunities")
        print("5. Plan migration strategy for high-risk items")


def main():
    """Main execution function"""
    inventory = ProjectInventory()
    results = inventory.analyze_project()
    
    inventory.print_summary()
    inventory.save_report()
    
    print(f"\n✅ Analysis complete! Check 'project_inventory_report.json' for detailed results.")


if __name__ == "__main__":
    main()