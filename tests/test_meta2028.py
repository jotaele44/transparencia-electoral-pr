import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from meta2028 import (validate_registry,observe_snapshot,deadline_check,unit_match,
 compare_result_manifests,custody_overlap,review_case,public_preview)
from rc6_security import AUDIENCE,synthetic_token,verify_token
KEY=b"r"*40;NOW=1794740000
def principal(name,role):
 claims={"sub":name,"role":role,"iss":"synthetic-rc6-idp","aud":AUDIENCE,"iat":NOW-50,"exp":NOW+50}
 return verify_token(synthetic_token(claims,KEY),KEY,now=NOW)
def case():
 return {"case_id":"synthetic-001","synthetic":True,"source_ids":["mock-source-a"],
         "finding_state":"UNRESOLVED","release_requested":False}
def unit(epoch="2024-certified",code="73",college="01"):
 return {"source_epoch":epoch,"municipality_raw":"Isabela","precinct_raw":"032","unit_raw":code,
         "college_raw":college,"ballot_type":"MUNICIPAL"}
def preview():
 return {"case_id":"synthetic-001","synthetic":True,"status":"OPEN","source_count":0,"classification":"UNRESOLVED"}
class META2028Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.registry=json.loads((ROOT/"evidence/meta2028_event_registry.json").read_text())
  cls.weak=json.loads((ROOT/"evidence/meta2028_2024_weakness_ledger.json").read_text())
  cls.metrics=json.loads((ROOT/"evidence/meta2028_kpis.json").read_text())
  cls.inventory=json.loads((ROOT/"evidence/meta2028_component_inventory.json").read_text())
 def test_registry_closed_counts(self):
  x=validate_registry(self.registry)
  self.assertEqual((x["events"],x["sources"]),(4,7))
  self.assertEqual(x["monitor"],"OFF")
  self.assertEqual(x["unbound_event_source_ids"],["cee_2028_rfp","ogp_electoral_code_2026_11_04"])
 def test_registry_duplicate_sources_rejected(self):
  d=copy.deepcopy(self.registry);d["source_registry"].append(copy.deepcopy(d["source_registry"][0]))
  with self.assertRaises(ValueError):validate_registry(d)
 def test_registry_duplicate_event_rejected(self):
  d=copy.deepcopy(self.registry);d["events"].append(copy.deepcopy(d["events"][0]))
  with self.assertRaises(ValueError):validate_registry(d)
 def test_registry_live_denied(self):
  d=copy.deepcopy(self.registry);d["production_monitor_enabled"]=True
  with self.assertRaises(PermissionError):validate_registry(d)
 def test_registry_fabricated_source_hash_denied(self):
  d=copy.deepcopy(self.registry);d["source_registry"][0]["original_sha256"]="f"*64
  with self.assertRaises(ValueError):validate_registry(d)
 def test_bound_event_source_url_conflict_rejected(self):
  d=copy.deepcopy(self.registry)
  d['events'][2]['source_url']='https://other.example.org/changed.pdf'
  with self.assertRaises(ValueError):validate_registry(d)
 def test_registry_bad_date_rejected(self):
  d=copy.deepcopy(self.registry);d["events"][0]["date"]="2028-02-30"
  with self.assertRaises(ValueError):validate_registry(d)
 def test_snapshot_changes_not_logical_or_guilt(self):
  x=observe_snapshot(b"before",b"after",source_id="mock",now_utc="2026-11-16T17:00:00Z")
  self.assertEqual(x["byte_change"],"BYTE_DIFFERENT")
  self.assertEqual(x["logical_schema_change"],"UNRESOLVED")
  self.assertEqual(x["alert"],"PROVISIONAL_REVIEW_REQUIRED")
 def test_snapshot_same_no_alert(self):
  x=observe_snapshot(b"x",b"x",source_id="mock",now_utc="2026-11-16T17:00:00Z")
  self.assertEqual(x["alert"],"NONE")
 def test_snapshot_no_bytes_rejected(self):
  with self.assertRaises(ValueError):observe_snapshot(None,b"new",source_id="mock",now_utc="2026-11-16T17:00:00Z")
 def test_deadline_scenario_late_mailing_start(self):
  x=deadline_check(deadline_kind="LATEST_START",legal_bound="2028-09-20",observed="2028-09-21")
  self.assertEqual(x["status"],"SYNTHETIC_LATE_OBSERVATION")
  self.assertFalse(x["official_compliance_finding"])
 def test_deadline_mail_end_exact(self):
  x=deadline_check(deadline_kind="LATEST_END",legal_bound="2028-10-03",observed="2028-10-03")
  self.assertEqual(x["status"],"SYNTHETIC_WITHIN_BOUND")
 def test_deadline_unknown_authority_blocked(self):
  with self.assertRaises(ValueError):deadline_check(deadline_kind="LATEST_START",legal_bound="2028-09-27",observed="2028-09-27")
 def test_real_compliance_assertion_blocked(self):
  with self.assertRaises(PermissionError):deadline_check(deadline_kind="LATEST_START",legal_bound="2028-09-20",observed="2028-09-21",synthetic=False)
 def test_unit_073_never_equal_73(self):
  x=unit_match(unit(code="073"),unit(code="73"))
  self.assertFalse(x["match"]);self.assertFalse(x["canonical_identity_proven"])
 def test_college_04_not_01(self):
  self.assertFalse(unit_match(unit(college="04"),unit(college="01"))["match"])
 def test_epoch_change_not_implicit_identity(self):
  self.assertFalse(unit_match(unit(epoch="2024-pre"),unit(epoch="2024-final"))["match"])
 def test_exact_tuple_still_candidate(self):
  x=unit_match(unit(),unit());self.assertTrue(x["match"])
  self.assertEqual(x["state"],"CANDIDATE_NOT_IDENTITY")
 def test_missing_unit_unresolved(self):
  x=unit();x.pop("precinct_raw")
  self.assertEqual(unit_match(x,unit())["state"],"UNRESOLVED")
 def test_municipal_partial_cannot_be_unit_pair(self):
  from hashlib import sha256
  def r(epoch,grain):
   raw=epoch.encode()
   return {"source_id":epoch,"authority":"CEE","geographic_level":grain,"source_epoch":epoch,
           "identity_state":"VERIFIED_BINDING","ballot_type":"MUNICIPAL",
           "sha256":sha256(raw).hexdigest(),"original_bytes":raw,"signed":True}
  x=compare_result_manifests(r("pre","MUNICIPALITY"),r("final","PRECINCT_UNIT_COLLEGE"))
  self.assertFalse(x["eligible"]);self.assertEqual(x["reason"],"GEOGRAPHIC_GRAIN_MISMATCH")
 def test_custody_district_overlap_cannot_prove_execution(self):
  x=custody_overlap({"representative_district":"16"},{"representative_district":"16"})
  self.assertFalse(x["execution_proven"]);self.assertEqual(x["state"],"UNRESOLVED")
 def test_separation_fixture_valid_but_no_release(self):
  x=review_case(case=case(),analyst=principal("a","analyst"),reviewer=principal("b","reviewer"),officer=principal("c","release_officer"))
  self.assertFalse(x["public_release_authorized"]);self.assertEqual(x["status"],"REVIEWED_FIXTURE_ONLY")
 def test_same_actor_reviewer_blocked(self):
  with self.assertRaises(PermissionError):
   review_case(case=case(),analyst=principal("a","analyst"),reviewer=principal("a","reviewer"),officer=principal("c","release_officer"))
 def test_premature_release_denied(self):
  c=case();c["release_requested"]=True
  with self.assertRaises(PermissionError):
   review_case(case=c,analyst=principal("a","analyst"),reviewer=principal("b","reviewer"),officer=principal("c","release_officer"))
 def test_real_cases_denied(self):
  c=case();c["synthetic"]=False
  with self.assertRaises(PermissionError):
   review_case(case=c,analyst=principal("a","analyst"),reviewer=principal("b","reviewer"),officer=principal("c","release_officer"))
 def test_public_preview_allowlist(self):
  self.assertEqual(public_preview(preview()),preview())
 def test_public_preview_sensitive_field_rejected(self):
  x=preview();x["voter_name"]="private"
  with self.assertRaises(ValueError):public_preview(x)
 def test_public_preview_html_injection_rejected(self):
  x=preview();x['case_id']='synthetic-<script>alert(1)</script>'
  with self.assertRaises(ValueError):public_preview(x)
 def test_public_preview_real_data_denied(self):
  x=preview();x["synthetic"]=False
  with self.assertRaises(PermissionError):public_preview(x)
 def test_weakness_ledger_source_bounded(self):
  self.assertEqual(len(self.weak["entries"]),8)
  self.assertEqual(len(set(x["id"] for x in self.weak["entries"])),8)
  self.assertTrue(all("not_proven" in x and "control" in x for x in self.weak["entries"]))
  self.assertEqual(self.weak["overall_certification"],"AUDIT_ONLY")
 def test_metric_denominators_do_not_claim_scores(self):
  self.assertEqual(len(self.metrics["metrics"]),8)
  self.assertEqual(self.metrics["status"],"DEFINITION_ONLY_NO_REAL_SCORES")
  self.assertTrue(all("NULL_IF_" in m["unknown_rule"] for m in self.metrics["metrics"]))
 def test_reused_components_are_not_live(self):
  self.assertEqual(self.inventory["cross_repo"]["TheHub"],"PINNED_REAL_VALIDATOR_TEST_ONLY")
  self.assertIn("NOT_RUNTIME_TESTED",self.inventory["cross_repo"]["Centinelas_PR"])
if __name__=="__main__":unittest.main()
