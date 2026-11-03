"""Extract measures from FreeSurfer aseg.stats headers across a derivatives directory.

Examples:
    uv run scripts/freesurfer_stats.py ABCD/7.0/dairc/derivatives/freesurfer
    uv run scripts/freesurfer_stats.py ABCD/7.0/dairc/derivatives/freesurfer -o abcd7_holes.csv
    uv run scripts/freesurfer_stats.py ABCD/7.0/dairc/derivatives/freesurfer --all-measures
"""

import argparse

from nervedata import FreeSurferStats

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("root", help="FreeSurfer derivatives directory (sub-*_ses-* dirs or .zip)")
parser.add_argument("--output", "-o", default="surface_holes.tsv",
                    help="Output file; .csv for comma-separated, otherwise tab (default: %(default)s)")
parser.add_argument("--all-measures", action="store_true",
                    help="Write every '# Measure' in the header, not just surface holes")
parser.add_argument("--workers", "-j", type=int, default=16,
                    help="Parallel file reads (default: %(default)s)")
args = parser.parse_args()

fs = FreeSurferStats(args.root, workers=args.workers)
df = fs.measures if args.all_measures else fs.surface_holes
sep = "," if args.output.endswith(".csv") else "\t"
df.to_csv(args.output, sep=sep, index=False, na_rep="n/a")

n_err = df["error"].notna().sum() if "error" in df else 0
print(f"Wrote {len(df)} rows to {args.output} ({n_err} errors)")
