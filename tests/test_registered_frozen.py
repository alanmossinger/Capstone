"""The registered v7 record in results/registered_v7/ is never edited after the 17 October 2026 audit."""

import hashlib
import json

from src import paths

FROZEN = paths.RESULTS / "registered_v7"


def test_every_frozen_file_matches_its_hash():
    manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        # line endings are normalised so a Windows checkout and a Linux checkout hash alike
        data = (FROZEN / name).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == digest, f"{name} changed after it was frozen"


def test_no_unlisted_file_in_the_frozen_folder():
    manifest = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
    on_disk = {p.name for p in FROZEN.glob("*.csv")}
    assert on_disk == set(manifest["files"])


FROZEN_V9 = paths.RESULTS / "v9"


def test_the_v9_challenger_record_matches_its_hashes():
    manifest = json.loads((FROZEN_V9 / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        data = (FROZEN_V9 / name).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == digest, f"results/v9/{name} changed after it was frozen"
    on_disk = {p.name for p in FROZEN_V9.iterdir() if p.is_file() and p.name != "manifest.json"}
    assert on_disk == set(manifest["files"]), "a file was added to or removed from the frozen v9 record"
