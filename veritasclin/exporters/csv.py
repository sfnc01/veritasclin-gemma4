from __future__ import annotations

import io
import json

import pandas as pd

from veritasclin.schemas.caution import CautionItem
from veritasclin.schemas.claims import Claim


def claims_to_csv(claims: list[Claim]) -> str:
    rows = [
        {
            "id": claim.id,
            "text": claim.text,
            "claim_type": claim.claim_type,
            "support_status": claim.support_status,
            "pmids": ";".join(claim.pmids),
            "evidence_level": claim.evidence_level,
            "risk_level": claim.risk_level,
            "rationale": claim.rationale,
            "limitation_note": claim.limitation_note or "",
        }
        for claim in claims
    ]
    buffer = io.StringIO()
    pd.DataFrame(rows).to_csv(buffer, index=False)
    return buffer.getvalue()


def caution_map_to_json(cautions: list[CautionItem]) -> str:
    return json.dumps([item.model_dump(mode="json") for item in cautions], indent=2)
