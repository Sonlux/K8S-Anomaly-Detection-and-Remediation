#!/usr/bin/env python3
"""
Project Cleanup Plan Implementation
Provides safe cleanup and migration strategies based on inventory analysis
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict
import argparse

class ProjectCleanup:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.backup_created = False
        
    def create_backup_branch(self):
        """Create a backup git branch before cleanup"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status'], 
                                  capture_output=True, text=True, cwd=self.root_path)
            if result.returncode != 0:
                print("⚠️  Not in a git repository. Backup branch not created.")
                return False
            
            # Create backup branch
            branch_name = "cleanup-backup"
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                          cwd=self.root_path, check=True)
            subprocess.run(['git', 'checkout', 'main'], 
                          cwd=self.root_path, check=True)
            
            print(f"✅ Created backup branch: {branch_name}")
            self.backup_created = True
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create backup branch: {e}")
            return False
    
    def phase_1_safe_removal(self, dry_run: bool = True):
        """Phase 1: Remove build artifacts and cache files"""
        print("\n🧹 PHASE 1: Safe Removal of Build Artifacts")
        print("=" * 50)
        
        safe_to_remove = [
            ".next/",
            "backend/__pycache__/",
            "backend/src/__pycache__/",
            "backend/src/agents/__pycache__/", 
            "backend/models/__pycache__/",
            "frontend/__pycache__/",
            "dummy1.py",
            "container2"
        ]
        
        total_removed = 0
        
        for item in safe_to_remove:
            item_path = self.root_path / item
            if item_path.exists():
                size = self._get_path_size(item_path)
                print(f"{'[DRY RUN] ' if dry_run else ''}Removing: {item} ({size / (1024*1024):.1f} MB)")
                
                if not dry_run:
                    try:
                        if item_path.is_dir():
                            shutil.rmtree(item_path)
                        else:
                            item_path.unlink()
                        total_removed += size
                    except Exception as e:
                        print(f"❌ Failed to remove {item}: {e}")
                else:
                    total_removed += size
            else:
                print(f"⏭️  Skipping {item} (not found)")
        
        # Remove vim swap files
        self._remove_swap_files(dry_run)
        
        print(f"\n✅ Phase 1 complete. Space {'would be' if dry_run else ''} freed: {total_removed / (1024*1024):.1f} MB")
        return total_removed
    
    def phase_2_consolidate_dependencies(self, dry_run: bool = True):
        """Phase 2: Consolidate requirements and virtual environments"""
        print("\n📦 PHASE 2: Consolidate Dependencies")
        print("=" * 50)
        
        # Consolidate requirements files
        requirements_files = [
            "requirements.txt",
            "backend/requirements.txt",
            "backend/requirements-dashboard.txt", 
            "backend/nvidia_api_requirements.txt"
        ]
        
        self._consolidate_requirements(requirements_files, "backend/requirements.txt", dry_run)
        
        # Consolidate virtual environments
        venv_dirs = ["backend/.venv/", "backend/venv_rag/"]
        self._consolidate_virtual_environments(venv_dirs, dry_run)
        
        print("✅ Phase 2 complete.")
    
    def phase_3_restructure(self, dry_run: bool = True):
        """Phase 3: Restructure project directories"""
        print("\n🏗️  PHASE 3: Restructure Project")
        print("=" * 50)
        print("⚠️  HIGH RISK: This phase requires careful testing")
        
        if not dry_run:
            response = input("This will restructure the entire project. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Phase 3 cancelled.")
                return
        
        # Create new directory structure
        self._create_directory_structure(dry_run)
        
        # Move source files
        self._move_source_files(dry_run)
        
        print("✅ Phase 3 complete. TESTING REQUIRED!")
    
    def _consolidate_requirements(self, source_files: List[str], target: str, dry_run: bool):
        """Consolidate multiple requirements files"""
        print(f"\n📋 Consolidating requirements files into {target}")
        
        all_packages = set()
        package_versions = {}
        
        for req_file in source_files:
            req_path = self.root_path / req_file
            if req_path.exists():
                print(f"  Reading: {req_file}")
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and not line.startswith('-'):
                                # Extract package name and version
                                if '==' in line:
                                    pkg, version = line.split('==', 1)
                                    package_versions[pkg.strip()] = version.strip()
                                elif '>=' in line:
                                    pkg = line.split('>=')[0].strip()
                                    if pkg not in package_versions:
                                        package_versions[pkg] = line.split('>=')[1].strip()
                                else:
                                    pkg = line.strip()
                                    if pkg not in package_versions:
                                        package_versions[pkg] = ""
                                all_packages.add(pkg.strip())
                except Exception as e:
                    print(f"    ❌ Error reading {req_file}: {e}")
        
        if not dry_run:
            # Create backend directory if it doesn't exist
            target_path = self.root_path / target
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write consolidated requirements
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write("# Consolidated requirements file\n")
                f.write("# Generated by project cleanup script\n\n")
                
                for pkg in sorted(all_packages):
                    if package_versions.get(pkg):
                        f.write(f"{pkg}=={package_versions[pkg]}\n")
                    else:
                        f.write(f"{pkg}\n")
            
            print(f"  ✅ Created consolidated {target}")
        else:
            print(f"  [DRY RUN] Would create {target} with {len(all_packages)} packages")
    
    def _consolidate_virtual_environments(self, venv_dirs: List[str], dry_run: bool):
        """Remove duplicate virtual environments"""
        print(f"\n🐍 Consolidating virtual environments")
        
        for venv_dir in venv_dirs:
            venv_path = self.root_path / venv_dir
            if venv_path.exists():
                size = self._get_path_size(venv_path)
                print(f"  {'[DRY RUN] ' if dry_run else ''}Removing: {venv_dir} ({size / (1024*1024):.1f} MB)")
                
                if not dry_run:
                    try:
                        shutil.rmtree(venv_path)
                    except Exception as e:
                        print(f"    ❌ Failed to remove {venv_dir}: {e}")
    
    def _create_directory_structure(self, dry_run: bool):
        """Create new project directory structure"""
        print("\n📁 Creating new directory structure")
        
        directories = [
            "backend/src/",
            "backend/tests/", 
            "backend/scripts/",
            "backend/config/",
            "frontend/src/",
            "frontend/public/",
            "shared/configs/",
            "shared/docs/"
        ]
        
        for directory in directories:
            dir_path = self.root_path / directory
            print(f"  {'[DRY RUN] ' if dry_run else ''}Creating: {directory}")
            
            if not dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def _move_source_files(self, dry_run: bool):
        """Move source files to new structure"""
        print("\n📦 Moving source files")
        
        moves = [
            # Backend files - already moved in previous tasks
            # ("k8s/src/", "backend/src/"),
            # ("k8s/kubescape/backend/", "backend/src/"),
            # ("k8s/tests/", "backend/tests/"),
            # ("k8s/config/", "backend/config/"),
            
            # Frontend files - already moved in previous tasks
            # ("k8s/kubescape/src/", "frontend/src/"),
            # ("k8s/kubescape/public/", "frontend/public/"),
            
            # Scripts
            ("project_inventory.py", "backend/scripts/"),
            ("dataset-generator.py", "backend/scripts/"),
            ("agp.py", "backend/scripts/"),
            
            # Configs
            ("next.config.js", "frontend/"),
            ("tailwind.config.js", "shared/configs/"),
            ("postcss.config.js", "shared/configs/")
        ]
        
        for source, target in moves:
            source_path = self.root_path / source
            target_path = self.root_path / target
            
            if source_path.exists():
                print(f"  {'[DRY RUN] ' if dry_run else ''}Moving: {source} -> {target}")
                
                if not dry_run:
                    try:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        if source_path.is_dir():
                            shutil.move(str(source_path), str(target_path))
                        else:
                            shutil.move(str(source_path), str(target_path / source_path.name))
                    except Exception as e:
                        print(f"    ❌ Failed to move {source}: {e}")
    
    def _remove_swap_files(self, dry_run: bool):
        """Remove vim swap files"""
        swap_patterns = [".git/*.swo", ".git/*.swp"]
        
        for pattern in swap_patterns:
            for swap_file in self.root_path.glob(pattern):
                print(f"{'[DRY RUN] ' if dry_run else ''}Removing swap file: {swap_file.name}")
                if not dry_run:
                    try:
                        swap_file.unlink()
                    except Exception as e:
                        print(f"❌ Failed to remove {swap_file}: {e}")
    
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
    
    def generate_cleanup_script(self, output_file: str = "run_cleanup.py"):
        """Generate a standalone cleanup script"""
        script_content = '''#!/usr/bin/env python3
"""
Generated Project Cleanup Script
Run with: python run_cleanup.py --phase 1 --execute
"""

import argparse
from cleanup_plan import ProjectCleanup

def main():
    parser = argparse.ArgumentParser(description='Project Cleanup Tool')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], 
                       help='Cleanup phase to run (1=safe removal, 2=consolidation, 3=restructure)')
    parser.add_argument('--execute', action='store_true', 
                       help='Execute changes (default is dry run)')
    parser.add_argument('--all', action='store_true',
                       help='Run all phases')
    
    args = parser.parse_args()
    
    cleanup = ProjectCleanup()
    
    if not args.execute:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("Add --execute flag to perform actual cleanup")
    
    # Create backup branch
    if args.execute:
        cleanup.create_backup_branch()
    
    if args.all:
        cleanup.phase_1_safe_removal(dry_run=not args.execute)
        cleanup.phase_2_consolidate_dependencies(dry_run=not args.execute)
        cleanup.phase_3_restructure(dry_run=not args.execute)
    elif args.phase == 1:
        cleanup.phase_1_safe_removal(dry_run=not args.execute)
    elif args.phase == 2:
        cleanup.phase_2_consolidate_dependencies(dry_run=not args.execute)
    elif args.phase == 3:
        cleanup.phase_3_restructure(dry_run=not args.execute)
    else:
        print("Please specify --phase or --all")

if __name__ == "__main__":
    main()
'''
        
        with open(output_file, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Generated cleanup script: {output_file}")

def main():
    """Main function for direct execution"""
    parser = argparse.ArgumentParser(description='Project Cleanup Plan')
    parser.add_argument('--generate-script', action='store_true',
                       help='Generate standalone cleanup script')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    cleanup = ProjectCleanup()
    
    if args.generate_script:
        cleanup.generate_cleanup_script()
        return
    
    print("🔍 PROJECT CLEANUP PLAN")
    print("=" * 50)
    print("This tool will analyze and clean up the project structure.")
    print("Run with --generate-script to create a standalone cleanup tool.")
    
    # Show what each phase would do
    cleanup.phase_1_safe_removal(dry_run=True)
    cleanup.phase_2_consolidate_dependencies(dry_run=True) 
    cleanup.phase_3_restructure(dry_run=True)

if __name__ == "__main__":
    main()