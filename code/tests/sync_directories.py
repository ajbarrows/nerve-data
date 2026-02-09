# test_sync_symlinks.py
import pytest
from pathlib import Path
import tempfile
import shutil
import os

def create_test_structure(base_dir):
    """Helper to create test directory structure"""
    dir1 = base_dir / "dir1"
    dir2 = base_dir / "dir2"
    
    # Create dir1 structure
    (dir1 / "subdir1").mkdir(parents=True)
    (dir1 / "subdir2").mkdir(parents=True)
    (dir1 / "file1.txt").write_text("content1")
    (dir1 / "subdir1" / "file2.txt").write_text("content2")
    (dir1 / "subdir2" / "file3.txt").write_text("content3")
    
    # Create dir2 with some overlapping structure
    dir2.mkdir()
    (dir2 / "subdir1").mkdir()
    (dir2 / "file_new.txt").write_text("new content")
    
    return dir1, dir2

@pytest.fixture
def temp_dirs():
    """Fixture to create and cleanup temporary test directories"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_directory_symlink_creation(temp_dirs):
    """Test that entire missing directories are symlinked"""
    dir1, dir2 = create_test_structure(temp_dirs)
    
    sync_directories(str(dir1), str(dir2), dry_run=False)
    
    # subdir2 should be a symlink (doesn't exist in dir2)
    assert (dir2 / "subdir2").is_symlink()
    assert (dir2 / "subdir2" / "file3.txt").read_text() == "content3"

def test_file_symlink_creation(temp_dirs):
    """Test that missing files in existing directories are symlinked"""
    dir1, dir2 = create_test_structure(temp_dirs)
    
    sync_directories(str(dir1), str(dir2), dry_run=False)
    
    # file1.txt should be symlinked (missing from dir2)
    assert (dir2 / "file1.txt").is_symlink()
    # file2.txt should be symlinked (subdir1 exists in both)
    assert (dir2 / "subdir1" / "file2.txt").is_symlink()

def test_dry_run_no_changes(temp_dirs):
    """Test that dry run makes no actual changes"""
    dir1, dir2 = create_test_structure(temp_dirs)
    
    sync_directories(str(dir1), str(dir2), dry_run=True)
    
    # Nothing should be created
    assert not (dir2 / "subdir2").exists()
    assert not (dir2 / "file1.txt").exists()

def test_relative_symlinks(temp_dirs):
    """Test that symlinks are relative, not absolute"""
    dir1, dir2 = create_test_structure(temp_dirs)
    
    sync_directories(str(dir1), str(dir2), dry_run=False)
    
    link_target = os.readlink(dir2 / "file1.txt")
    assert not Path(link_target).is_absolute()

def test_checksum_duplicate_detection(temp_dirs):
    """Test that identical files are detected with checksum"""
    dir1, dir2 = create_test_structure(temp_dirs)
    
    # Add duplicate file
    (dir2 / "file1.txt").write_text("content1")
    
    sync_directories(str(dir1), str(dir2), dry_run=False, check_content=True)
    
    # file1.txt should now be a symlink (was duplicate)
    assert (dir2 / "file1.txt").is_symlink()

def test_existing_files_preserved(temp_dirs):
    """Test that existing unique files in dir2 are not touched"""
    dir1, dir2 = create_test_structure(temp_dirs)
    
    original_content = (dir2 / "file_new.txt").read_text()
    
    sync_directories(str(dir1), str(dir2), dry_run=False)
    
    # file_new.txt should still exist and not be a symlink
    assert not (dir2 / "file_new.txt").is_symlink()
    assert (dir2 / "file_new.txt").read_text() == original_content

def test_nested_directories(temp_dirs):
    """Test deeply nested directory structures"""
    dir1 = temp_dirs / "dir1"
    dir2 = temp_dirs / "dir2"
    
    (dir1 / "a" / "b" / "c").mkdir(parents=True)
    (dir1 / "a" / "b" / "c" / "deep.txt").write_text("deep content")
    dir2.mkdir()
    
    sync_directories(str(dir1), str(dir2), dry_run=False)
    
    # Entire 'a' directory should be symlinked
    assert (dir2 / "a").is_symlink()