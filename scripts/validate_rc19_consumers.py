"""Validate synthetic META-2028 events against exact pinned federation contracts.

This is schema/manifest integration, not production runtime activation. The
TheHub package validator is separately exercised against the exact pinned code.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from jsonschema import Draft7Validator, FormatChecker

PINNED={
 "centinelas":"3b80bb5e5bae3df1d1a358ffc250d42887132991",
 "moneysweep":"c26b5028fd42a653eacb2bca48fd3ec8589d2a0f",
 "spiderweb":"9c37b42926e6d401e80598221162a4664f2202d0",
 "thehub":"b7a60e613fecb36448c719651625892b2bded565",
}
NOW="2026-11-17T08:00:00Z"
LINEAGE={"producer_script":"rc19_synthetic_contract_fixture.py","producer_phase":"SCHEMA_COMPATIBILITY_TEST","source_inputs":["synthetic_fixture_only"],"extraction_method":"fixed_test_fixture"}
def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def validate(schema,row):
    errors=list(Draft7Validator(schema,format_checker=FormatChecker()).iter_errors(row))
    return sorted((list(e.path),e.message) for e in errors)
def require_valid(schema,row,label):
    errors=validate(schema,row)
    if errors: raise AssertionError(f"{label} rejected: {errors}")
def require_invalid(schema,row,label):
    errors=validate(schema,row)
    if not errors: raise AssertionError(f"{label} unexpectedly accepted")
def head(path):
    return subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
def blob(path,relative):
    return subprocess.check_output(["git","-C",str(path),"rev-parse",f"HEAD:{relative}"],text=True).strip()
def check_pin(name,path):
    actual=head(path)
    if actual!=PINNED[name]: raise AssertionError(f"{name} commit mismatch: {actual}")
def make_manifest(producer,stream):
    digest=hashlib.sha256(("synthetic:"+producer+":"+stream).encode()).hexdigest()
    return {"package_id":"pkg_"+hashlib.sha256((producer+stream).encode()).hexdigest()[:32],
      "producer":producer,"export_contract_version":"1.0.0","mode":"test","created_at":NOW,
      "federation":{"producer_repo":producer,"hub_parent":"thehub-pr"},
      "files":[{"filename":stream+".jsonl","stream":stream,"record_count":1,"sha256":digest,"schema_id":"federation_"+stream+".schema.json"}]}
def main():
    p=argparse.ArgumentParser()
    for name in PINNED:p.add_argument("--"+name,required=True)
    a=p.parse_args(); dirs={name:Path(getattr(a,name)).resolve() for name in PINNED}
    for name,path in dirs.items():check_pin(name,path)
    cm=load(dirs["centinelas"]/"federation.json")
    mm=load(dirs["moneysweep"]/"federation.json")
    sm=load(dirs["spiderweb"]/"federation.json")
    if cm["program_id"]!="centinelas-pr" or not cm["federation_readiness_gate"]["ready_for_hub_live_execution"]:
        raise AssertionError("Centinelas manifest identity/readiness changed")
    if mm["program_id"]!="moneysweep-pr" or mm["federation_readiness_gate"]["ready_for_hub_live_execution"] is not False:
        raise AssertionError("MoneySweep must remain explicitly not ready for live Hub execution")
    if sm["program_id"]!="spiderweb-pr" or not sm["federation_readiness_gate"]["ready_for_hub_live_execution"]:
        raise AssertionError("Spiderweb manifest identity/readiness changed")
    c_export=(dirs["centinelas"]/"scripts/federation_export.py").read_text()
    if "source_monitors" not in c_export or "source_monitor_row" not in c_export:
        raise AssertionError("Centinelas source-monitor export contract not found")
    c_manifest_schema=load(dirs["centinelas"]/"schemas/federation_export_manifest.schema.json")
    m_manifest_schema=load(dirs["moneysweep"]/"schemas/federation_export_manifest.schema.json")
    s_manifest_schema=load(dirs["spiderweb"]/"schemas/federation_export_manifest.schema.json")
    h=dirs["thehub"]
    h_manifest_schema=load(h/"schemas/federation_export_manifest.schema.json")
    h_source=load(h/"schemas/federation_source.schema.json")
    h_entity=load(h/"schemas/federation_entity.schema.json")
    h_relationship=load(h/"schemas/federation_relationship.schema.json")
    h_observation=load(h/"schemas/federation_observation.schema.json")
    h_monitor=load(h/"schemas/federation_source_monitor.schema.json")
    s_monitor=load(dirs["spiderweb"]/"schemas/federation_source_monitor.schema.json")
    if blob(dirs["spiderweb"],"schemas/federation_source_monitor.schema.json")!=blob(h,"schemas/federation_source_monitor.schema.json"):
        raise AssertionError("Spiderweb source-monitor schema blob differs from pinned Hub schema")
    signal_schema=load(dirs["centinelas"]/"schemas/signal.schema.json")
    signal={"signal_id":"sig_rc19_synthetic_001","matter_id":"matter_rc19_calendar_001",
      "signal_type":"electoral_source_publication","title":"Synthetic CEE calendar publication event",
      "summary":"Synthetic-only contract fixture; no real election allegation.","source_id":"cee_calendar_fixture",
      "source_url":"https://www.ceepur.org/fixture.pdf","captured_at":NOW,"published_at":NOW,
      "signal_stage":"under_review","beat":"electoral_process","municipalities":[],"agencies":["CEE"],
      "entities":[],"estimated_value":None,"deadline_date":"2028-09-20","urgency_score":None,
      "confidence_score":0.0,"evidence_tier":"T1","handoff_status":"not_handed_off","is_synthetic":True}
    require_valid(signal_schema,signal,"Centinelas signal")
    bad_signal=dict(signal);bad_signal["confidence_score"]=101
    require_invalid(signal_schema,bad_signal,"Centinelas out-of-range confidence")
    source_id="src_"+hashlib.sha256(b"rc19-source").hexdigest()[:32]
    entity_id="ent_"+hashlib.sha256(b"rc19-entity").hexdigest()[:32]
    source={"source_id":source_id,"source_type":"official_publication_candidate","source_name":"Synthetic CEE calendar source",
      "source_ref":"cee_2028_calendar_fixture","source_url":"https://www.ceepur.org/fixture.pdf","confidence":0.0,
      "lineage":LINEAGE,"synthetic":True,"created_at":NOW,"extracted_at":NOW}
    entity={"entity_id":entity_id,"source_id":source_id,"name":"2028 electoral calendar fixture",
      "normalized_name":"2028_electoral_calendar_fixture","entity_type":"electoral_event_calendar",
      "jurisdiction":"Puerto Rico","confidence":0.0,"lineage":LINEAGE,"synthetic":True,"created_at":NOW,"extracted_at":NOW}
    agency_entity_id="ent_"+hashlib.sha256(b"rc19-agency").hexdigest()[:32]
    agency_entity={"entity_id":agency_entity_id,"source_id":source_id,"name":"Synthetic CEE agency",
      "normalized_name":"synthetic_cee_agency","entity_type":"agency","jurisdiction":"Puerto Rico",
      "confidence":0.0,"lineage":LINEAGE,"synthetic":True,"created_at":NOW,"extracted_at":NOW}
    relationship={"relationship_id":"rel_"+hashlib.sha256(b"rc19-rel").hexdigest()[:32],
      "source_id":source_id,"source_entity_id":entity_id,"target_entity_id":agency_entity_id,
      "relationship_type":"electoral_calendar_published_by","evidence_source_id":source_id,"confidence":0.0,
      "lineage":LINEAGE,"synthetic":True,"created_at":NOW,"extracted_at":NOW}
    observation={"observation_id":"obs_"+hashlib.sha256(b"rc19-obs").hexdigest()[:32],"source_id":source_id,
      "entity_id":entity_id,"observation_type":"electoral_source_publication","observed_at":NOW,
      "attributes":{"source_ref":"cee_2028_calendar_fixture","modality":"ABSENTEE_APPLICATION","status":"UNRESOLVED"},
      "confidence":0.0,"lineage":LINEAGE,"synthetic":True,"created_at":NOW,"extracted_at":NOW}
    monitor={"monitor_id":"mon_"+hashlib.sha256(b"rc19-monitor").hexdigest()[:32],
      "source_ref":"cee_2028_calendar_fixture","name":"Synthetic CEE 2028 calendar monitor",
      "declared_status":"unknown","cadence":"event","last_success_basis":"NOT_RECORDED","last_success_at":None,
      "source_url":"https://www.ceepur.org/fixture.pdf","lineage":LINEAGE,"synthetic":True,
      "created_at":NOW,"extracted_at":NOW}
    for schema,row,label in ((h_source,source,"Hub source"),(h_entity,entity,"Hub entity"),(h_entity,agency_entity,"Hub agency entity"),
      (h_relationship,relationship,"Hub relationship"),(h_observation,observation,"Hub observation"),
      (h_monitor,monitor,"Hub source monitor"),(s_monitor,monitor,"Spiderweb source monitor")):
        require_valid(schema,row,label)
    bad_monitor=dict(monitor);bad_monitor["last_success_at"]=NOW
    require_invalid(h_monitor,bad_monitor,"NOT_RECORDED monitor with fabricated success time")
    for schema,label in ((h_manifest_schema,"Hub"),(c_manifest_schema,"Centinelas"),(s_manifest_schema,"Spiderweb")):
        require_valid(schema,make_manifest("transparencia-electoral-pr","source_monitors"),label+" source-monitor manifest")
    require_valid(m_manifest_schema,make_manifest("moneysweep-pr","sources"),"MoneySweep core manifest")
    require_invalid(m_manifest_schema,make_manifest("moneysweep-pr","source_monitors"),"MoneySweep unsupported source_monitors stream")
    print("RC19_PINNED_CONSUMER_SCHEMA_PASS: Centinelas signal; Hub source/entity/relationship/observation/source_monitor; Spiderweb source_monitor; manifests")
    print("RC19_BLOCKED_BOUNDARY: MoneySweep live Hub execution remains false; its pinned manifest schema does not declare source_monitors")
if __name__=="__main__":main()
