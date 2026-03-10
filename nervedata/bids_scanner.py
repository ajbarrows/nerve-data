import pandas as pd
from pathlib import Path


class BIDSDataset:
    """
    Represents a BIDS dataset on disk and provides scanning utilities
    to report subject/session/modality coverage.
    """

    MODALITIES = ['anat', 'dwi', 'fmap', 'func', 'motion', 'mrs']

    def __init__(self, bids_dir: str | Path, modalities: list[str] | None = None):
        self.bids_dir = Path(bids_dir)
        self.modalities = modalities or self.MODALITIES
        self._detail: pd.DataFrame | None = None
        self._summary: pd.DataFrame | None = None

    def scan(self) -> "BIDSDataset":
        """Walk the BIDS directory and record modality presence per subject/session."""
        data = []

        for subject_dir in sorted(self.bids_dir.glob('sub-*')):
            if not subject_dir.is_dir():
                continue

            subject_id = subject_dir.name
            session_dirs = sorted(d for d in subject_dir.glob('ses-*') if d.is_dir())

            if session_dirs:
                for session_dir in session_dirs:
                    row = {'subject': subject_id, 'session': session_dir.name}
                    for modality in self.modalities:
                        mod_dir = session_dir / modality
                        row[modality] = mod_dir.exists() and any(mod_dir.iterdir())
                    data.append(row)
            else:
                row = {'subject': subject_id, 'session': 'ses-01'}
                for modality in self.modalities:
                    mod_dir = subject_dir / modality
                    row[modality] = mod_dir.exists() and any(mod_dir.iterdir())
                data.append(row)

        df = pd.DataFrame(data).sort_values(['subject', 'session']).reset_index(drop=True)
        self._detail = df
        self._summary = (
            df.set_index('subject')
            .melt(id_vars='session')
            .groupby('variable')
            .value_counts()
            .reset_index()
            .query("value")
            .pivot(index='session', columns='variable', values='count')
        )
        return self

    def _ensure_scanned(self):
        if self._detail is None:
            self.scan()

    @property
    def detail(self) -> pd.DataFrame:
        """Full subject × session × modality DataFrame."""
        self._ensure_scanned()
        return self._detail

    @property
    def summary(self) -> pd.DataFrame:
        """Modality counts pivoted by session."""
        self._ensure_scanned()
        return self._summary

    @property
    def n_subjects(self) -> int:
        return self.detail['subject'].nunique()
