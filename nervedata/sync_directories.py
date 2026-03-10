import argparse
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class DirectorySyncer:
    """
    Syncs a source directory into a target directory using symlinks.

    Files and directories present in source but absent in target are
    symlinked (not copied). Optionally, files that exist in both but
    are byte-identical can be detected and replaced with symlinks.
    """

    def __init__(
        self,
        source: str | Path,
        target: str | Path,
        dry_run: bool = False,
        output_file: str | None = None,
        check_content: bool = False,
    ):
        self.source = Path(source)
        self.target = Path(target)
        self.dry_run = dry_run
        self.output_file = output_file
        self.check_content = check_content

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _checksum(filepath: Path) -> str:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    def _find_symlinks_needed(self, rel_dir: Path) -> tuple[list, list]:
        """Return (symlinks_needed, subdirs_to_recurse) for rel_dir."""
        symlinks = []
        source_dir = self.source / rel_dir
        target_dir = self.target / rel_dir

        if not source_dir.exists():
            return [], []

        source_subdirs = {f.name for f in source_dir.iterdir() if f.is_dir()}
        target_subdirs = (
            {f.name for f in target_dir.iterdir() if f.is_dir()}
            if target_dir.exists()
            else set()
        )

        for dirname in source_subdirs - target_subdirs:
            symlinks.append(('dir', rel_dir / dirname))

        source_files = {f.name for f in source_dir.iterdir() if f.is_file()}
        target_files = (
            {f.name for f in target_dir.iterdir() if f.is_file()}
            if target_dir.exists()
            else set()
        )

        for filename in source_files - target_files:
            symlinks.append(('file', rel_dir / filename))

        if self.check_content:
            for filename in source_files & target_files:
                src = source_dir / filename
                tgt = target_dir / filename
                if self._checksum(src) == self._checksum(tgt):
                    symlinks.append(('duplicate', rel_dir / filename))

        shared_subdirs = [rel_dir / d for d in source_subdirs & target_subdirs]
        return symlinks, shared_subdirs

    def _create_link(self, item: tuple, output=None):
        link_type, rel_path = item
        source = self.source / rel_path
        target = self.target / rel_path
        rel_source = os.path.relpath(source, target.parent)

        if link_type == 'duplicate':
            msg = f"{'Would replace' if self.dry_run else 'Replaced'} duplicate with symlink: {target} -> {source}"
            print(msg, file=output)
            if not self.dry_run:
                target.unlink()
                target.symlink_to(rel_source)
        else:
            if not self.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(rel_source)
            msg = f"{'Would create' if self.dry_run else 'Created'} {link_type} symlink: {target} -> {source}"
            print(msg, file=output)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync(self):
        """Run the sync. Creates symlinks in target for anything missing from source."""
        output = open(self.output_file, 'w') if self.output_file else None
        try:
            all_symlinks = []
            dirs_to_process = [Path()]

            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                while dirs_to_process:
                    results = list(executor.map(self._find_symlinks_needed, dirs_to_process))
                    dirs_to_process = []
                    for symlinks, subdirs in results:
                        all_symlinks.extend(symlinks)
                        dirs_to_process.extend(subdirs)

            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                executor.map(lambda item: self._create_link(item, output), all_symlinks)
        finally:
            if output:
                output.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync directories with symlinks")
    parser.add_argument("source", help="Source directory")
    parser.add_argument("target", help="Target directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--output", "-o", help="Write output to file instead of stdout")
    parser.add_argument(
        "--check-content",
        action="store_true",
        help="Compare file checksums and replace duplicates with symlinks",
    )

    args = parser.parse_args()
    DirectorySyncer(
        source=args.source,
        target=args.target,
        dry_run=args.dry_run,
        output_file=args.output,
        check_content=args.check_content,
    ).sync()
