import zipfile

import pandas as pd
import pytest

from nervedata import FreeSurferStats

ASEG = """\
# Title Segmentation Statistics
# Measure BrainSeg, BrainSegVol, Brain Segmentation Volume, 1234567.000000, mm^3
# Measure lhSurfaceHoles, lhSurfaceHoles, Number of defect holes in lh surfaces prior to fixing, {lh}, unitless
# Measure rhSurfaceHoles, rhSurfaceHoles, Number of defect holes in rh surfaces prior to fixing, {rh}, unitless
# Measure SurfaceHoles, SurfaceHoles, Total number of defect holes in surfaces prior to fixing, {tot}, unitless
# ColHeaders  Index SegId NVoxels Volume_mm3 StructName
  1   4     1000     1000.0  Left-Lateral-Ventricle
"""


def write_dir(root, name, lh, rh):
    (root / name / "stats").mkdir(parents=True)
    (root / name / "stats" / "aseg.stats").write_text(ASEG.format(lh=lh, rh=rh, tot=lh + rh))


def write_zip(root, name, lh, rh):
    with zipfile.ZipFile(root / f"{name}.zip", "w") as zf:
        zf.writestr(f"{name}/stats/aseg.stats", ASEG.format(lh=lh, rh=rh, tot=lh + rh))


@pytest.fixture
def fs_root(tmp_path):
    write_zip(tmp_path, "sub-A_ses-00A", 4, 5)
    write_zip(tmp_path, "sub-A_ses-02A", 1, 2)
    write_dir(tmp_path, "sub-B_ses-00A", 10, 3)
    # Same session as both dir and zip: dir should win
    write_dir(tmp_path, "sub-C_ses-00A", 7, 7)
    write_zip(tmp_path, "sub-C_ses-00A", 99, 99)
    # Zip without aseg.stats
    with zipfile.ZipFile(tmp_path / "sub-D_ses-00A.zip", "w") as zf:
        zf.writestr("sub-D_ses-00A/stats/wmparc.stats", "")
    (tmp_path / "unrelated.txt").write_text("")
    return tmp_path


def test_surface_holes(fs_root):
    df = FreeSurferStats(fs_root).surface_holes.set_index(["participant_id", "session_id"])

    assert len(df) == 5
    assert df.loc[("sub-A", "ses-00A"), ["lh_surface_holes", "rh_surface_holes", "surface_holes"]].tolist() == [4, 5, 9]
    assert df.loc[("sub-A", "ses-02A"), "surface_holes"] == 3
    assert df.loc[("sub-B", "ses-00A"), "surface_holes"] == 13


def test_directory_preferred_over_zip(fs_root):
    df = FreeSurferStats(fs_root).surface_holes.set_index(["participant_id", "session_id"])
    assert df.loc[("sub-C", "ses-00A"), "surface_holes"] == 14
    assert df.loc[("sub-C", "ses-00A"), "source"] == "sub-C_ses-00A"


def test_missing_aseg_reported(fs_root):
    df = FreeSurferStats(fs_root).surface_holes.set_index(["participant_id", "session_id"])
    row = df.loc[("sub-D", "ses-00A")]
    assert pd.isna(row["surface_holes"])
    assert "FileNotFoundError" in row["error"]


def test_all_measures(fs_root):
    m = FreeSurferStats(fs_root).measures
    assert "BrainSeg" in m.columns
    assert m["BrainSeg"].dropna().eq(1234567.0).all()
