"""Offline, noncanonical Hub export package generator. Never enables discovery."""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

def generate(rows, output_dir, *, test_only=True):
    if not test_only: raise PermissionError("production export prohibited before certification")
    if not isinstance(rows,list): raise TypeError("rows must be list")
    seen=set(); normalized=[]
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get("id"),str) or not row["id"].strip():
            raise ValueError("row missing stable id")
        if row["id"] in seen: raise ValueError("duplicate stable id")
        if row.get("synthetic") is not True: raise ValueError("RC3 test export requires synthetic rows")
        seen.add(row["id"]);normalized.append(dict(row))
    target=Path(output_dir);target.mkdir(parents=True,exist_ok=True)
    payload="".join(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\\n" for x in sorted(normalized,key=lambda x:x["id"]))
    # prevent malformed escape regressions: each row on its own LF line
    payload=payload.replace("\\n","\n")
    raw=payload.encode("utf-8")
    digest=hashlib.sha256(raw).hexdigest()
    (target/"sources.jsonl").write_bytes(raw)
    identifier=hashlib.sha256(("test|sources.jsonl|"+digest).encode()).hexdigest()[:32]
    manifest={"package_id":"pkg_"+identifier,"producer":"transparencia-electoral-pr","producer_version":"rc3","export_contract_version":"rc3-provisional","mode":"test","created_at":"2026-11-15T00:00:00Z","federation":{"producer_repo":"transparencia-electoral-pr","hub_parent":"thehub-pr"},"files":[{"filename":"sources.jsonl","stream":"sources","record_count":len(normalized),"sha256":digest,"schema_id":"synthetic_electoral_source_fixture_v1"}],"readiness":"NONCANONICAL_TEST_ONLY"}
    (target/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest
