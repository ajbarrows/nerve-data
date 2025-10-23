# Tools for data management

## make_symlinks.py

CLI to compare directories `source` and `target`:

- Maintain files in `target` that are also in `source` (they're presumed to be updated versions)
- Create symbolic links between `target` and `source` for files that are in `source` but not in `target` to avoid copying

Note: this tool does not (currently) compare file content, just whether it exists.

## bids_scanner.py

Walk BIDS-compliant directory and report the counts of subject-timepoint combinations for each (specified) file type.