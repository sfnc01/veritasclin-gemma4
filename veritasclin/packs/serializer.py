from __future__ import annotations

from pathlib import Path

from veritasclin.exporters.csv import caution_map_to_json, claims_to_csv
from veritasclin.exporters.json_export import pack_to_json
from veritasclin.exporters.markdown import pack_to_markdown
from veritasclin.schemas.pack import EvidencePack


def save_pack_bundle(pack: EvidencePack, directory: str | Path) -> dict[str, Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "pack_json": target / "pack.json",
        "dossier_md": target / "dossier.md",
        "claim_ledger_csv": target / "claim_ledger.csv",
        "caution_map_json": target / "caution_map.json",
    }
    paths["pack_json"].write_text(pack_to_json(pack), encoding="utf-8")
    paths["dossier_md"].write_text(pack_to_markdown(pack), encoding="utf-8")
    paths["claim_ledger_csv"].write_text(claims_to_csv(pack.claim_ledger), encoding="utf-8")
    paths["caution_map_json"].write_text(caution_map_to_json(pack.caution_map), encoding="utf-8")
    return paths
