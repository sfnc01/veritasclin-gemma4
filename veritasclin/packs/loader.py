from __future__ import annotations

import json
from pathlib import Path

from veritasclin.schemas.pack import EvidencePack


class PackLoader:
    def load(self, path: str | Path) -> EvidencePack:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return EvidencePack.model_validate(data)

    def loads(self, text: str | bytes) -> EvidencePack:
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        return EvidencePack.model_validate(json.loads(text))
