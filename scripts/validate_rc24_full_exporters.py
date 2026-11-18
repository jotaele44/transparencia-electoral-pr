"""Run exact pinned Centinelas and Spiderweb full CLI exporters on synthetic fixtures.

Outputs go only to disposable temp directories. The exact pinned TheHub package
validator checks each package; corruption must fail, restored snapshots must pass.
No real source polling, voter records, production writes or producer-repo changes.
"""
from __future__ import annotations
import argparse,csv,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path

PINS={
 "centinelas":"3b80bb5e5bae3df1d1a358ffc250d42887132991",
 "spiderweb":"9c37b42926e6d401e80598221162a4664f2202d0",
 "hub":"b7a60e613fecb36448c719651625892b2bded565",
 "helpers":"0f62e4bdde10b5ac82787a329d6f15481ab9c7f0",
}
def git_head(path):
 return subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
def check_pin(name,path):
 actual=git_head(path)
 if actual!=PINS[name]:raise AssertionError(f"{name} pin mismatch: {actual}")
def run(cmd,cwd,env=None,expect=0):
 p=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True)
 if p.returncode!=expect:
  raise AssertionError(f"command rc={p.returncode}, expected={expect}: {cmd}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
 return p
def hub_validator(hub):
 sys.path.insert(0,str(hub/"src"))
 from hub.validate import validate_package
 return validate_package
def validate_package(validate,pkg,label):
 errors=validate(pkg,validate_rows=True)
 if errors:raise AssertionError(f"{label} actual pinned TheHub validator rejected package: {errors}")
def corruption_and_restore(validate,pkg,label,work):
 snapshot=work/(label+"-rollback")
 shutil.copytree(pkg,snapshot)
 source=pkg/"sources.jsonl"
 if not source.exists():raise AssertionError(f"{label}: missing sources.jsonl")
 original=source.read_bytes()
 source.write_bytes(original+b'{"tampered":true}\n')
 if not validate(pkg,validate_rows=True):raise AssertionError(f"{label}: TheHub failed to detect tampered package")
 shutil.rmtree(pkg)
 shutil.copytree(snapshot,pkg)
 validate_package(validate,pkg,label+" restored rollback")
def main():
 p=argparse.ArgumentParser()
 for n in PINS:p.add_argument("--"+n,required=True)
 a=p.parse_args()
 c=Path(a.centinelas).resolve();s=Path(a.spiderweb).resolve();h=Path(a.hub).resolve();u=Path(a.helpers).resolve()
 for n,path in (("centinelas",c),("spiderweb",s),("hub",h),("helpers",u)):check_pin(n,path)
 if not (h/"src/hub/validate.py").is_file():raise AssertionError("pinned Hub validator missing")
 validate=hub_validator(h)
 helper_src=u/"packages/prii_export_utils/src"
 env=os.environ.copy();env["PYTHONPATH"]=str(helper_src)+os.pathsep+env.get("PYTHONPATH","")
 now="2026-11-18T18:00:00Z"
 with tempfile.TemporaryDirectory(prefix="rc24-exporters-") as td:
  w=Path(td)
  # Centinelas: full CLI export from a one-row synthetic signal ledger and registry.
  c_ledger=w/"centinelas-signals.jsonl"
  signal={"signal_id":"rc24-synthetic-signal-001","matter_id":"rc24-synthetic-matter-001",
   "signal_type":"electoral_source_publication","title":"Synthetic CEE calendar fixture",
   "summary":"Synthetic-only RC24 test; no real election allegation.",
   "source_id":"rc24-synthetic-cee-source","captured_at":now,"confidence_score":0,
   "is_synthetic":True,"agencies":["CEE"],"municipalities":["San Juan"],
   "signal_stage":"under_review","beat":"electoral_process","evidence_tier":"T1",
   "handoff_status":"not_handed_off","deadline_date":"2028-09-20"}
  c_ledger.write_text(json.dumps(signal)+"\n",encoding="utf-8")
  c_registry=w/"centinelas-registry.csv"
  with c_registry.open("w",newline="",encoding="utf-8") as fh:
   wr=csv.DictWriter(fh,fieldnames=["source_id","name","source_family","active","scrape_method"])
   wr.writeheader();wr.writerow({"source_id":signal["source_id"],"name":"Synthetic CEE source",
      "source_family":"official_electoral_source","active":"yes","scrape_method":"manual"})
  c_out=w/"centinelas-municipality-output"
  r=run([sys.executable,"scripts/federation_export.py","--ledger",str(c_ledger),"--sources",str(c_registry),
      "--out",str(c_out),"--mode","test"],c,env,0)
  # The pinned producer emits location={municipality: ...}; pinned Hub schema
  # requires lat+lon whenever location is present. This is a real schema gap,
  # not grounds to invent a centroid or coordinates.
  c_errors=validate(c_out,validate_rows=True)
  expected=("location: 'lat' is a required property","location: 'lon' is a required property")
  if not all(any(e.endswith(x) for e in c_errors) for x in expected):
   raise AssertionError(f"Centinelas municipality schema behavior changed unexpectedly: {c_errors}")
  cm=json.loads((c_out/"manifest.json").read_text())
  cc={x["stream"]:x["record_count"] for x in cm["files"]}
  if cc.get("sources")!=1 or cc.get("observations")!=1 or cc.get("source_monitors")!=1:
   raise AssertionError(f"Centinelas row/stream conservation failed: {cc}")
  # A separate no-location fixture is compatible; never synthesize geometry.
  signal_no_location=dict(signal);signal_no_location["signal_id"]="rc24-synthetic-signal-no-location"
  signal_no_location["matter_id"]="rc24-synthetic-matter-no-location";signal_no_location["municipalities"]=[]
  c_ledger_no_location=w/"centinelas-signals-no-location.jsonl"
  c_ledger_no_location.write_text(json.dumps(signal_no_location)+"\n",encoding="utf-8")
  c_out_valid=w/"centinelas-output-no-location"
  run([sys.executable,"scripts/federation_export.py","--ledger",str(c_ledger_no_location),"--sources",str(c_registry),
      "--out",str(c_out_valid),"--mode","test"],c,env,0)
  validate_package(validate,c_out_valid,"Centinelas full CLI without unsupported municipality-only location")
  corruption_and_restore(validate,c_out_valid,"centinelas",w)
  # Production mode must fail closed because the only row is explicitly synthetic.
  prod=run([sys.executable,"scripts/federation_export.py","--ledger",str(c_ledger),"--sources",str(c_registry),
      "--out",str(w/"centinelas-production"),"--mode","production"],c,env,1)
  if "synthetic rows are not allowed" not in (prod.stdout+prod.stderr):
   raise AssertionError("Centinelas production mode did not reject synthetic-only input")
  # Spiderweb: clone the exact pinned checkout into disposable fixture space and
  # replace only registries with empty synthetic fixtures; never modify its checkout.
  s_copy=w/"spiderweb-disposable"
  shutil.copytree(s,s_copy,ignore=shutil.ignore_patterns(".git"))
  hydro=s_copy/"manifests/pr_hydrography/source_registry.csv"
  hydro.parent.mkdir(parents=True,exist_ok=True)
  hydro.write_text("source_id,authority,universe,refresh_policy,evidence_tier,endpoint\n",encoding="utf-8")
  missing=s_copy/"configs/missing_persons_sources.yaml"
  missing.parent.mkdir(parents=True,exist_ok=True)
  missing.write_text("sources: {}\n",encoding="utf-8")
  s_pkg=w/"spiderweb-input";s_pkg.mkdir()
  src={"source_id":"rc24-synthetic-spider-source","kind":"fixture","confidence":0,
       "is_synthetic":True,"first_seen_at":now}
  rec={"id":"rc24-synthetic-observation-001","source_id":src["source_id"],
       "observation_type":"structure_sighting","observed_at":now,"confidence":0,
       "is_synthetic":True,"geometry":{"type":"Point","coordinates":[-66.1057,18.4655]}}
  (s_pkg/"sources.jsonl").write_text(json.dumps(src)+"\n",encoding="utf-8")
  (s_pkg/"observations.jsonl").write_text(json.dumps(rec)+"\n",encoding="utf-8")
  s_out=w/"spiderweb-output"
  r=run([sys.executable,"scripts/federation_export.py","--package",str(s_pkg),"--out",str(s_out),
      "--mode","test","--no-ppp-geometry"],s_copy,env,0)
  validate_package(validate,s_out,"Spiderweb full CLI")
  sm=json.loads((s_out/"manifest.json").read_text())
  sc={x["stream"]:x["record_count"] for x in sm["files"]}
  if sc.get("sources")!=1 or sc.get("entities",0)<2 or sc.get("relationships")!=1:
   raise AssertionError(f"Spiderweb row/stream conservation failed: {sc}")
  corruption_and_restore(validate,s_out,"spiderweb",w)
  prod=run([sys.executable,"scripts/federation_export.py","--package",str(s_pkg),"--out",str(w/"spiderweb-production"),
      "--mode","production","--no-ppp-geometry"],s_copy,env,1)
  if "synthetic rows are not allowed" not in (prod.stdout+prod.stderr):
   raise AssertionError("Spiderweb production mode did not reject synthetic-only input")
 print("RC24_FULL_EXPORTER_SCOPE: Centinelas CLI executed; municipality-only location rejected by pinned Hub schema (lat/lon required); no-location fixture passed; Spiderweb CLI + Hub validation tested")
 print("RC24_FAILURE_GATES_PASS: synthetic production rejection; Hub corruption detection and snapshot rollback")
 print("RC24_BOUNDARY: MoneySweep excluded; no live polling, real voter data, production writes, deployment or autonomous enforcement")
if __name__=="__main__":main()
