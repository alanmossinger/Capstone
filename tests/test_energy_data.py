"""The v5 source parsers: OGOR-A rows become lease-months, EIA-923 keeps its grain, the manifest and provenance labels are complete."""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src import config, energy_data, plots

matplotlib.use("Agg")

OGORA_TWO_LEASES = (
    '" 00016"," A004","201001","00","U","000000000","000000000","000000000","177194003101","14","WD   31","00687","INEOS","WD030","000000000","X01","","",""\n'
    '" 00016"," E016","201001","31","G","000000100","000016325","000000050","177194064700","11","WD   31","00276","EXXON","WD030","000000000","Q04","19720331","",""\n'
    '" 00016"," E017","201001","28","O","000000200","000000500","000000010","177194064701","11","WD   31","00276","EXXON","WD030","000000000","Q05","19720331","",""\n'
    '" 00017"," B001","201002","30","O","000000900","000000000","000000000","177194064702","11","WD   32","00276","EXXON","WD031","000000000","Q01","19800101","",""\n'
)


def test_read_ogora_types_and_keys():
    rows = energy_data.read_ogora(OGORA_TWO_LEASES)
    assert list(rows.columns[:19]) == energy_data.OGORA_COLUMNS
    assert rows["lease_number"].tolist() == ["00016", "00016", "00016", "00017"]  # leading blank stripped
    assert rows["oil_bbl"].tolist() == [0, 100, 200, 900] and rows["gas_mcf"].iloc[1] == 16325
    assert rows["month"].iloc[0] == pd.Timestamp("2010-01-01") and rows["month"].iloc[3] == pd.Timestamp("2010-02-01")


def test_lease_monthly_sums_completions_and_flags_producing():
    lease = energy_data.lease_monthly(energy_data.read_ogora(OGORA_TWO_LEASES))
    first = lease[lease["lease_number"] == "00016"].iloc[0]
    assert first["oil_bbl"] == 300 and first["gas_mcf"] == 16825 and first["water_bbl"] == 60
    assert first["n_completions"] == 3 and first["n_producing"] == 2 and first["days_on_prod"] == 31
    assert first["operator_name"] == "EXXON" and bool(first["producing"])
    assert len(lease) == 2


def test_generation_monthly_sums_fuels_within_a_prime_mover_and_maps_technology():
    raw = pd.DataFrame({
        "period": ["2020-01"] * 5, "plantCode": ["9"] * 5, "plantName": ["Copper"] * 5,
        "fuelType": ["ALL", "ALL", "NG", "DFO", "SUN"], "primeMover": ["ALL", "CT", "CT", "CT", "PV"],
        "generation": [10.0, 7.0, 6.0, 1.0, 3.0], "gross-generation": [11.0, 8.0, 7.0, 1.0, 3.0],
        "total-consumption-btu": [1.0, 1.0, 1.0, 0.0, 0.0], "consumption-for-eg-btu": [1.0, 1.0, 1.0, 0.0, 0.0]})
    gen = energy_data.generation_monthly(raw)
    assert len(gen) == 2  # the subtotals are dropped; NG and DFO add up within CT
    assert gen["technology"].tolist() == ["Gas CC", "Solar"] and gen["generation_mwh"].tolist() == [7.0, 3.0]
    assert gen["n_fuels"].tolist() == [2, 1]


def test_manifest_entry_requires_a_known_provenance(tmp_path):
    file = tmp_path / "x.txt"
    file.write_text("abc", encoding="utf-8")
    entry = energy_data.manifest_entry("S13", "BSEE", "https://example", [file], "2024", "bbl", "lease-month")
    assert set(entry) >= {"source_id", "url", "retrieved_utc", "files", "vintage", "units", "grain", "provenance"}
    assert entry["files"]["x.txt"] == energy_data.sha256(file)
    with pytest.raises(ValueError):
        energy_data.manifest_entry("S13", "BSEE", "https://example", [file], "2024", "bbl", "lease-month", provenance="GUESS")


def test_finish_prints_the_provenance_label_and_rejects_others():
    plots.set_style()
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    plots.finish(fig, "t", "s", "c", lbnl=False, sources=[config.SOURCE_BSEE], provenance="OBSERVED")
    assert any("Provenance: OBSERVED" in t.get_text() for t in fig.texts)
    plt.close(fig)
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plots.finish(fig, "t", "s", "c", lbnl=False, provenance="MAYBE")
    plt.close(fig)
