import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd


class FreeSurferStats:
    """
    Extracts header measures from FreeSurfer ``stats/aseg.stats`` files
    across a directory of ``sub-*_ses-*`` derivatives.

    Each session may be an extracted directory or a ``.zip`` archive; for
    archives only the aseg.stats member is read, so nothing is decompressed
    to disk. If both forms exist for a session, the directory is used.
    """

    NAME_RE = re.compile(r"^(sub-[^_]+)_(ses-[^_./]+)")
    MEASURE_RE = re.compile(r"^# Measure (\w+), \w+, .*, ([-\d.eE+]+), \S+\s*$")
    SURFACE_HOLES = {
        "lhSurfaceHoles": "lh_surface_holes",
        "rhSurfaceHoles": "rh_surface_holes",
        "SurfaceHoles": "surface_holes",
    }

    def __init__(self, root: str | Path, workers: int = 16):
        self.root = Path(root)
        self.workers = workers
        self._measures: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _parse_header(cls, text: str) -> dict[str, float]:
        """Return every ``# Measure`` value in the aseg.stats header."""
        out = {}
        for line in text.splitlines():
            if not line.startswith("#"):
                break  # header ends where the data table starts
            m = cls.MEASURE_RE.match(line)
            if m:
                out[m.group(1)] = float(m.group(2))
        return out

    @staticmethod
    def _read_aseg(path: Path) -> str:
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as zf:
                member = next(
                    (n for n in zf.namelist() if n.endswith("stats/aseg.stats")), None
                )
                if member is None:
                    raise FileNotFoundError(f"no stats/aseg.stats in {path.name}")
                return zf.read(member).decode()
        return (path / "stats" / "aseg.stats").read_text()

    def _find_sessions(self) -> list[Path]:
        entries = {}
        for p in sorted(self.root.iterdir()):
            m = self.NAME_RE.match(p.name)
            if not m or not (p.is_dir() or p.suffix == ".zip"):
                continue
            if p.is_dir() or m.groups() not in entries:
                entries[m.groups()] = p
        return list(entries.values())

    def _scan_one(self, path: Path) -> dict:
        sub, ses = self.NAME_RE.match(path.name).groups()
        row = {"participant_id": sub, "session_id": ses, "source": path.name}
        try:
            row.update(self._parse_header(self._read_aseg(path)))
        except (OSError, zipfile.BadZipFile) as e:
            row["error"] = f"{type(e).__name__}: {e}"
        return row

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self) -> "FreeSurferStats":
        """Read the aseg.stats header of every session under root."""
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            rows = list(executor.map(self._scan_one, self._find_sessions()))
        self._measures = pd.DataFrame(rows)
        return self

    @property
    def measures(self) -> pd.DataFrame:
        """All header measures, one row per participant/session."""
        if self._measures is None:
            self.scan()
        return self._measures

    @property
    def surface_holes(self) -> pd.DataFrame:
        """Surface defect hole counts (lh, rh, total) per participant/session."""
        df = self.measures.rename(columns=self.SURFACE_HOLES)
        cols = ["participant_id", "session_id", *self.SURFACE_HOLES.values(), "source"]
        if "error" in df:
            cols.append("error")
        df = df.reindex(columns=cols)
        holes = list(self.SURFACE_HOLES.values())
        df[holes] = df[holes].astype("Int64")
        return df.sort_values(["participant_id", "session_id"], ignore_index=True)

