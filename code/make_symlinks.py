import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import os

def sync_with_symlinks(dir1, dir2, dry_run=False, output_file=None):
    """Create directory or file symlinks as needed"""
    # Keep as provided (relative or absolute)
    dir1_path = Path(dir1)
    dir2_path = Path(dir2)
    
    output = open(output_file, 'w') if output_file else None
    
    def find_symlinks_needed(rel_dir):
        symlinks = []
        source_dir = dir1_path / rel_dir
        target_dir = dir2_path / rel_dir
        
        if not source_dir.exists():
            return symlinks, []
        
        source_subdirs = {f.name for f in source_dir.iterdir() if f.is_dir()}
        target_subdirs = {f.name for f in target_dir.iterdir() if f.is_dir()} if target_dir.exists() else set()
        
        # Missing entire subdirectories
        for dirname in source_subdirs - target_subdirs:
            symlinks.append(('dir', rel_dir / dirname))
        
        # Missing files
        source_files = {f.name for f in source_dir.iterdir() if f.is_file()}
        target_files = {f.name for f in target_dir.iterdir() if f.is_file()} if target_dir.exists() else set()
        
        for filename in source_files - target_files:
            symlinks.append(('file', rel_dir / filename))
        
        return symlinks, [rel_dir / dirname for dirname in (source_subdirs & target_subdirs)]
    
    # Find all symlinks needed
    all_symlinks = []
    dirs_to_process = [Path()]
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        while dirs_to_process:
            results = list(executor.map(find_symlinks_needed, dirs_to_process))
            dirs_to_process = []
            for symlinks, subdirs in results:
                all_symlinks.extend(symlinks)
                dirs_to_process.extend(subdirs)
    
    # Create symlinks in parallel
    def create_link(item):
        link_type, rel_path = item
        source = dir1_path / rel_path
        target = dir2_path / rel_path
        
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Create relative symlink from target to source
            relative_source = os.path.relpath(source, target.parent)
            target.symlink_to(relative_source)
        
        msg = f"{'Would create' if dry_run else 'Created'} {link_type} symlink: {target} -> {source}"
        print(msg, file=output if output else None)
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(create_link, all_symlinks)
    
    if output:
        output.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync directories with symlinks")
    parser.add_argument("dir1", help="Source directory")
    parser.add_argument("dir2", help="Target directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--output", "-o", help="Write output to file instead of stdout")
    
    args = parser.parse_args()
    sync_with_symlinks(args.dir1, args.dir2, args.dry_run, args.output)