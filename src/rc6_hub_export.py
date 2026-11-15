"""Hub-schema synthetic source fixture, distinct from noncanonical RC3 export."""
import hashlib
import json
from pathlib import Path
from rc6_security import canonical

CREATED="2026-11-15T00:00:00Z"
PRODUCER="transparencia-electoral-pr"

def build_fixture(output_dir,source_refs):
    if not isinstance(source_refs,list) or any(not isinstance(v,str) or not v.strip() or len(v)>100 for v in source_refs):raise ValueError("invalid refs")
    if len(set(source_refs))!=len(source_refs):raise ValueError("duplicate source ref")
    rows=[]
    for ref in sorted(source_refs):
        key=hashlib.sha256(("synthetic-rc6:"+ref).encode()).hexdigest()[:32]
        rows.append({"source_id":"src_"+key,"source_type":"synthetic_electoral_test","source_name":"Synthetic source "+ref,"source_ref":ref,"confidence":0.0,"lineage":{"producer_script":"rc6_hub_export.py","producer_phase":"SYNTHETIC_CONTRACT_TEST","source_inputs":[],"extraction_method":"deterministic_fixture"},"synthetic":True,"created_at":CREATED,"extracted_at":CREATED})
    payload=b"".join(canonical(r)+b"\n" for r in rows)
    digest=hashlib.sha256(payload).hexdigest()
    manifest={"package_id":"pkg_"+hashlib.sha256(("test|sources.jsonl|"+digest).encode()).hexdigest()[:32],"producer":PRODUCER,"producer_version":"rc6-test-only","export_contract_version":"repo_federation_manifest_v1","mode":"test","created_at":CREATED,"federation":{"producer_repo":PRODUCER,"hub_parent":"thehub-pr"},"files":[{"filename":"sources.jsonl","stream":"sources","record_count":len(rows),"sha256":digest,"schema_id":"federation_source.schema.json"}]}
    path=Path(output_dir)
    path.mkdir(parents=True,exist_ok=True)
    (path/"sources.jsonl").write_bytes(payload)
    (path/"manifest.json").write_bytes(canonical(manifest)+b"\n")
    return manifest

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("output")
    p.add_argument("--refs",nargs="*",default=["mock-2024-001","mock-2028-001"])
    a=p.parse_args()
    print(json.dumps(build_fixture(a.output,a.refs),sort_keys=True))
