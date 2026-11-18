"""Run real pinned Centinelas and Spiderweb *pure producer functions* on fixtures.

No exporter command, real data, source polling, persistent output or federation
activation. MoneySweep remains blocked by its pinned source_monitors contract.
This is narrower than end-to-end producer export/consumer operation.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

PINS={
"centinelas":"3b80bb5e5bae3df1d1a358ffc250d42887132991",
"spiderweb":"9c37b42926e6d401e80598221162a4664f2202d0",
}
def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 if spec is None or spec.loader is None:raise RuntimeError("missing exact producer module")
 module=importlib.util.module_from_spec(spec)
 sys.modules[name]=module
 spec.loader.exec_module(module)
 return module
def check_pin(name,path):
 head=subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
 if head!=PINS[name]:raise AssertionError(f"{name}: unpinned HEAD {head}")
def main():
 if len(sys.argv)!=3:raise SystemExit("usage: validate_rc23_pinned_producer_runtime.py <centinelas> <spiderweb>")
 c=Path(sys.argv[1]).resolve();s=Path(sys.argv[2]).resolve()
 check_pin("centinelas",c);check_pin("spiderweb",s)
 sys.path.insert(0,str(c/"scripts"))
 cent=load_module("centinelas_exact_producer",c/"scripts/federation_export.py")
 signal={"is_synthetic":True,"signal_id":"synthetic-meta23","matter_id":"synthetic-matter",
   "captured_at":"2026-11-18T12:00:00Z","confidence_score":0,
   "source_id":"synthetic-cee","signal_type":"electoral_source_publication",
   "title":"Synthetic 2028 calendar observation","summary":"Test fixture only",
   "agencies":["CEE"],"municipalities":[],"signal_stage":"under_review",
   "beat":"electoral_process","evidence_tier":"T1","handoff_status":"not_handed_off"}
 stream=cent.build_streams([signal],{"synthetic-cee":{"name":"Synthetic CEE","source_family":"government"}},"2026-11-18T12:00:00Z")
 if len(stream["sources"])!=1 or len(stream["observations"])!=1:raise AssertionError("Centinelas record-count mismatch")
 if not all(row.get("synthetic") is True for rows in stream.values() for row in rows):
    raise AssertionError("Centinelas fixture lost synthetic indicator")
 if stream["observations"][0]["attributes"]["signal_id"]!="synthetic-meta23":
    raise AssertionError("Centinelas lineage mismatch")
 env=load_module("spiderweb_exact_envelope",s/"federation/envelope.py")
 fixture={"producer":"spiderweb-pr","record_type":"source_observation","record_id":"synthetic-rc23",
    "source_id":"synthetic-cee","timestamp":"2026-11-18T12:00:00Z",
    "lineage":["synthetic_fixture_only"],"payload":{"source_ref":"cee-ejavaa-approval-fixture"},
    "synthetic":True}
 obj=env.EvidenceEnvelope.from_dict(fixture)
 result=obj.to_dict()
 if result["record_id"]!=fixture["record_id"] or result["synthetic"] is not True:
    raise AssertionError("Spiderweb envelope did not conserve synthetic identity")
 try:env.EvidenceEnvelope.from_dict({"producer":"spiderweb-pr"})
 except ValueError:pass
 else:raise AssertionError("Spiderweb missing source identity incorrectly accepted")
 if env.CONTRACT_VERSION!="1.0":raise AssertionError("Unexpected Spiderweb version")
 print("RC23_PINNED_PRODUCER_PURE_RUNTIME_PASS: Centinelas build_streams; Spiderweb EvidenceEnvelope; synthetic row conservation; missing-ID rejection")
 print("RC23_BOUNDARY: No real producer export, consumer E2E, network access, production writes, or MoneySweep activation")
if __name__=="__main__":main()
