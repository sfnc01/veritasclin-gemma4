from __future__ import annotations

from veritasclin.schemas.pack import EvidencePack


def pack_to_json(pack: EvidencePack) -> str:
    return pack.model_dump_json(indent=2)
