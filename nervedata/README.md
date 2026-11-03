# Tools for data management

## sync_directories.py

CLI to compare directories `source` and `target`:

- Maintain files in `target` that are also in `source` (they're presumed to be updated versions)
- Create symbolic links between `target` and `source` for files that are in `source` but not in `target` to avoid copying

Note: this tool does not (currently) compare file content, just whether it exists.

## bids_scanner.py

Walk BIDS-compliant directory and report the counts of subject-timepoint combinations for each (specified) file type.

## freesurfer_stats.py

Extract header measures (e.g. surface defect holes) from FreeSurfer `stats/aseg.stats` across `sub-*_ses-*` derivatives. Reads directly from `.zip` archives without extracting them.

```bash
uv run scripts/freesurfer_stats.py ABCD/7.0/dairc/derivatives/freesurfer -o surface_holes.tsv
uv run scripts/freesurfer_stats.py ABCD/7.0/dairc/derivatives/freesurfer --all-measures -o aseg_measures.tsv
```

```python
from nervedata import FreeSurferStats
fs = FreeSurferStats("ABCD/7.0/dairc/derivatives/freesurfer")
fs.surface_holes   # participant_id, session_id, lh/rh/total surface holes
fs.measures        # every `# Measure` in the header (eTIV, BrainSegVol, ...)
```
