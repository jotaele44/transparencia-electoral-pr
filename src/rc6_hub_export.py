"""Hub-schema synthetic fixture; never production data or election evidence."""
import hashlib
from pathlib import Path
from rc6_security import canonical

CREATED="2026-11-17T08:00:00Z"
PRODUCER="transparencia-electoral-pr"

def _lineage(phase):
    return {"producer_script":"rc6_hub_export.py","producer_phase":phase,
            "source_inputs":["synthetic_fixture_only"],"extraction_method":"deterministic_fixture"}

def _write_jsonl(path,rows):
    payload=b"".join(canonical(r)+b"\n" for r in rows)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()

def build_fixture(output_dir,source_refs):
    if not isinstance(source_refs,list) or any(not isinstance(v,str) or not v.strip() or len(v)>100 for v in source_refs):
        raise ValueError("invalid refs")
    if len(set(source_refs))!=len(source_refs):
        raise ValueError("duplicate source ref")
    sources=[];monitors=[];observations=[]
    for ref in sorted(source_refs):
        key=hashlib.sha256(("synthetic-rc6:"+ref).encode()).hexdigest()[:32]
        source_id="src_"+key
        sources.append({"source_id":source_id,"source_type":"synthetic_electoral_test",
            "source_name":"Synthetic source "+ref,"source_ref":ref,"confidence":0.0,
            "lineage":_lineage("SYNTHETIC_CONTRACT_TEST"),"synthetic":True,
            "created_at":CREATED,"extracted_at":CREATED})
        monitors.append({"monitor_id":"mon_"+hashlib.sha256(("monitor:"+ref).encode()).hexdigest()[:32],
            "source_ref":ref,"name":"Synthetic monitor "+ref,"declared_status":"unknown",
            "cadence":"event","last_success_basis":"NOT_RECORDED","last_success_at":None,
            "source_url":None,"lineage":_lineage("SYNTHETIC_MONITOR_CONTRACT_TEST"),
            "synthetic":True,"created_at":CREATED,"extracted_at":CREATED})
        observations.append({"observation_id":"obs_"+hashlib.sha256(("observation:"+ref).encode()).hexdigest()[:32],
            "source_id":source_id,"observation_type":"electoral_source_publication",
            "observed_at":CREATED,"attributes":{"source_ref":ref,"event":"synthetic_calendar_publication"},
            "confidence":0.0,"lineage":_lineage("SYNTHETIC_EVENT_CONTRACT_TEST"),
            "synthetic":True,"created_at":CREATED,"extracted_at":CREATED})
    path=Path(output_dir);path.mkdir(parents=True,exist_ok=True)
    entries=[]
    for filename,stream,rows,schema in (
        ("sources.jsonl","sources",sources,"federation_source.schema.json"),
        ("observations.jsonl","observations",observations,"federation_observation.schema.json"),
        ("source_monitors.jsonl","source_monitors",monitors,"federation_source_monitor.schema.json")):
        digest=_write_jsonl(path/filename,rows)
        entries.append({"filename":filename,"stream":stream,"record_count":len(rows),
                        "sha256":digest,"schema_id":schema})
    seed="|".join(f"{x['filename']}:{x['sha256']}" for x in sorted(entries,key=lambda x:x["filename"]))
    manifest={"package_id":"pkg_"+hashlib.sha256(("test|"+seed).encode()).hexdigest()[:32],
        "producer":PRODUCER,"producer_version":"rc19-test-only","export_contract_version":"1.0.0",
        "mode":"test","created_at":CREATED,"federation":{"producer_repo":PRODUCER,"hub_parent":"thehub-pr"},
        "files":entries}
    (path/"manifest.json").write_bytes(canonical(manifest)+b"\n")
    return manifest

if __name__=="__main__":
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument("output")
    p.add_argument("--refs",nargs="*",default=["mock-2024-001","mock-2028-001"])
    a=p.parse_args()
    print(json.dumps(build_fixture(a.output,a.refs),sort_keys=True))
