"""The raw-data manifest names every input with a source and a hash, and the check tells present, missing and changed files apart."""

import pandas as pd

from src import get_data


def test_manifest_lists_every_source_with_a_hash():
    m = pd.read_csv(get_data.MANIFEST)
    assert m["sha256"].str.fullmatch("[0-9a-f]{64}").all()
    assert not (m["source"] == "?").any(), m[m["source"] == "?"]["path"].tolist()
    assert set(m["how"]) <= {"script", "workflow", "hand"}
    assert {"lbnl/lbnl_ix_queue_data_file_thru2024_v2.xlsx", "lbnl/queues_2023_clean_data_r1.xlsx", "forward/ercot_dam_spp_2025.parquet"} <= set(m["path"])
    assert m["path"].is_unique


def test_source_of_prefers_the_exact_file_then_the_longest_folder():
    assert get_data.source_of("lbnl/queues_2023_clean_data_r1.xlsx")[0] == "S18"
    assert get_data.source_of("lbnl/lbnl_ix_queue_data_file_thru2024_v2.xlsx")[0] == "S1"
    assert get_data.source_of("bsee/forward/ogora2025delimit.zip")[0] == "S19"
    assert get_data.source_of("bsee/ogora2010delimit.zip")[0] == "S13"
    assert get_data.source_of("iso/gis_2024/x.xlsx")[0] == "S18"
    assert get_data.source_of("iso/pjm_queue.xml")[0] == "S7"


def test_check_reports_ok_missing_and_differs(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    (raw / "a").mkdir(parents=True)
    (raw / "a" / "same.txt").write_bytes(b"same")
    (raw / "a" / "changed.txt").write_bytes(b"old")
    manifest = tmp_path / "manifest.csv"
    pd.DataFrame({"source": ["S1"] * 3, "path": ["a/same.txt", "a/changed.txt", "a/gone.txt"],
                  "sha256": [get_data.sha256(raw / "a" / "same.txt"), get_data.sha256(raw / "a" / "changed.txt"), "0" * 64],
                  "how": ["hand"] * 3, "where": ["x"] * 3}).to_csv(manifest, index=False)
    (raw / "a" / "changed.txt").write_bytes(b"new")
    monkeypatch.setattr(get_data.paths, "DATA_RAW", raw)
    monkeypatch.setattr(get_data, "MANIFEST", manifest)
    status = get_data.check().set_index("path")["status"]
    assert status.to_dict() == {"a/same.txt": "ok", "a/changed.txt": "differs", "a/gone.txt": "missing"}
    assert get_data.report(get_data.check()) is False


def test_bundle_carries_the_hash_records(tmp_path, monkeypatch):
    import zipfile

    raw = tmp_path / "raw"
    (raw / "iso").mkdir(parents=True)
    (raw / "iso" / "snapshot.parquet").write_bytes(b"data")
    (raw / "iso" / "SHA256.txt").write_text("abc  snapshot.parquet\n", encoding="utf-8")
    manifest = tmp_path / "manifest.csv"
    pd.DataFrame({"source": ["S7"], "path": ["iso/snapshot.parquet"], "sha256": [get_data.sha256(raw / "iso" / "snapshot.parquet")],
                  "how": ["hand"], "where": ["x"]}).to_csv(manifest, index=False)
    monkeypatch.setattr(get_data.paths, "DATA_RAW", raw)
    monkeypatch.setattr(get_data, "MANIFEST", manifest)
    monkeypatch.setattr(get_data, "BUNDLE", tmp_path / "dist" / "bundle.zip")
    names = set(zipfile.ZipFile(get_data.bundle()).namelist())
    assert names == {"data/raw_manifest.csv", "data/raw/iso/snapshot.parquet", "data/raw/iso/SHA256.txt"}
