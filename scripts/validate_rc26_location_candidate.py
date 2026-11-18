"""RC26: real pinned Centinelas producer vs pinned Hub schema candidate.

Never changes producer or Hub checkout. Synthetic-only, module import + exact
SHA pins; evaluates candidate administrative location in memory only.
"""
import argparse,importlib.util,json,subprocess,sys
from pathlib import Path
from jsonschema import Draft7Validator
from rc26_location_contract import candidate_observation_schema,candidate_receipt

PINS={"centinelas":"3b80bb5e5bae3df1d1a358ffc250d42887132991",
      "hub":"b7a60e613fecb36448c719651625892b2bded565",
      "helpers":"0f62e4bdde10b5ac82787a329d6f15481ab9c7f0"}
def check(path,pin):
 actual=subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
 if actual!=pin:raise AssertionError("pinned source drift")
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec)
 sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod
def main():
 ap=argparse.ArgumentParser()
 for x in PINS:ap.add_argument("--"+x,required=True)
 a=ap.parse_args();c=Path(a.centinelas).resolve();h=Path(a.hub).resolve();u=Path(a.helpers).resolve()
 for name,path in (("centinelas",c),("hub",h),("helpers",u)):check(path,PINS[name])
 sys.path.insert(0,str(u/"packages/prii_export_utils/src"))
 cent=load("pinned_cent_for_rc26",c/"scripts/federation_export.py")
 row={"signal_id":"rc26-synthetic-1","matter_id":"rc26-synthetic-matter",
      "source_id":"rc26-synthetic-cee","captured_at":"2026-11-18T20:00:00Z",
      "confidence_score":0,"is_synthetic":True,"signal_type":"source_observation",
      "title":"synthetic CEE data","municipalities":["San Juan"],
      "signal_stage":"under_review","beat":"electoral_process",
      "evidence_tier":"T1","handoff_status":"not_handed_off"}
 streams=cent.build_streams([row],{"rc26-synthetic-cee":{"name":"Synthetic","source_family":"government"}},"2026-11-18T20:00:00Z")
 if len(streams["observations"])!=1:raise AssertionError("producer row conservation")
 obs=streams["observations"][0]
 if obs.get("location")!={"municipality":"San Juan"}:
    raise AssertionError("producer municipality-only location changed")
 official=json.loads((h/"schemas/federation_observation.schema.json").read_text())
 errs=list(Draft7Validator(official).iter_errors(obs))
 if not any(list(e.path)==["location"] for e in errs):
    raise AssertionError("expected real schema failure not reproduced")
 candidate=candidate_observation_schema(official)
 if list(Draft7Validator(candidate).iter_errors(obs)):
    raise AssertionError("in-memory candidate rejected genuine Centinelas projection")
 if obs["location"]!={"municipality":"San Juan"}:
    raise AssertionError("administrative municipality mutated")
 # The pinned Hub correlation helper consumes the exact same location.municipality,
 # so the proposed schema permits it without inventing point geometry.
 sys.path.insert(0,str(h/"src"))
 from hub.correlate import _municipality,_point
 if _municipality(obs)!="SAN JUAN" or _point(obs) is not None:
    raise AssertionError("Hub correlation changed or fictitious geometry appeared")
 receipt=candidate_receipt(official,candidate)
 if receipt["production_change_authorized"]:raise AssertionError("unsafe release flag")
 print("RC26_PINNED_ADMIN_LOCATION_CANDIDATE_PASS: real Centinelas projected municipality; official Hub schema rejects; isolated candidate accepts; Hub municipality correlation retained; no point geometry")
 print(json.dumps(receipt,sort_keys=True))
if __name__=="__main__":main()
