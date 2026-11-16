"""RC10: bounded source-pair reconciliation, never canonical or election certification.

The functions check internal integrity of synthetic rows and explicit source ID
bindings. Passing checks cannot prove that a purported CEE record is genuine.
"""
import hashlib
from collections import Counter

KEY=("election_id","contest_id","source_reporting_unit_id","candidate_id","vote_method")
VERSION_FIELDS=("version_id","manifestation_sha256","source_epoch","authority")

def _sha(d):
    return isinstance(d,str) and len(d)==64 and all(c in "0123456789abcdef" for c in d)

def verify_manifestations(items):
    if not isinstance(items,list) or len(items)!=2:raise ValueError("exactly two manifestations required")
    seen=set()
    for r in items:
        if not isinstance(r,dict) or any(k not in r for k in VERSION_FIELDS+("source_bytes","synthetic")):
            raise ValueError("manifestation fields required")
        if r["synthetic"] is not True:raise PermissionError("RC10 accepts synthetic source bytes only")
        if any(not isinstance(r[k],str) or not r[k].strip() for k in ("version_id","source_epoch","authority")):
            raise ValueError("unbound manifestation descriptor")
        if not isinstance(r["source_bytes"],bytes) or not _sha(r["manifestation_sha256"]):
            raise ValueError("byte-level evidence required")
        if hashlib.sha256(r["source_bytes"]).hexdigest()!=r["manifestation_sha256"]:
            raise ValueError("source manifestation byte mismatch")
        if r["version_id"] in seen:raise ValueError("duplicate version id")
        seen.add(r["version_id"])
    return {"manifestation_count":2,"bytes_validated":2,"identity_status":"CANDIDATE_NOT_IDENTITY"}

def index(rows,*,version):
    if not isinstance(rows,list):raise ValueError("rows list required")
    out={};unresolved=[]
    for i,r in enumerate(rows):
        if not isinstance(r,dict) or any(k not in r for k in KEY+("votes","version_id","synthetic")):
            unresolved.append({"index":i,"reason":"MISSING_FIELDS"});continue
        if r["synthetic"] is not True or r["version_id"]!=version:
            unresolved.append({"index":i,"reason":"VERSION_OR_SYNTHETIC_MISMATCH"});continue
        key=tuple(r[k] for k in KEY)
        if any(not isinstance(x,str) or not x.strip() for x in key):
            unresolved.append({"index":i,"reason":"INVALID_ID"});continue
        if type(r["votes"]) is not int or r["votes"]<0:
            unresolved.append({"index":i,"reason":"INVALID_VOTE_COUNT"});continue
        if key in out:
            unresolved.append({"index":i,"reason":"DUPLICATE_KEY","key":key});continue
        out[key]=r["votes"]
    return out,unresolved

def reconcile(manifestations,left,right,*,expected_keys=None,independent_source_binding=None):
    """Do not infer source-row equivalence across epochs from names or counts."""
    verify_manifestations(manifestations)
    a,b=manifestations
    if not isinstance(independent_source_binding,dict) or independent_source_binding.get("binding_status")!="PRIMARY_SOURCE_LINK_PENDING":
        raise PermissionError("unverified evidence cannot claim an authoritative binding")
    if a["authority"]!=b["authority"]:raise ValueError("source authority conflict")
    lhs,la=index(left,version=a["version_id"])
    rhs,lb=index(right,version=b["version_id"])
    ka,kb=set(lhs),set(rhs)
    overlap=ka&kb
    mismatches=sum(lhs[k]!=rhs[k] for k in overlap)
    exact_matches=len(overlap)-mismatches
    if expected_keys is None:
        denominator={"state":"OPEN","expected_count":None,"missing_expected":None,"unexpected_observed":None}
    else:
        if not isinstance(expected_keys,list) or any(not isinstance(x,tuple) or len(x)!=len(KEY) for x in expected_keys):
            raise ValueError("expected keys must be explicit complete tuples")
        exp=set(expected_keys)
        if len(exp)!=len(expected_keys):raise ValueError("duplicate expected key")
        observed=ka|kb
        denominator={"state":"FIXTURE_ONLY_INTERNAL_CHECK","expected_count":len(exp),"missing_expected":len(exp-observed),"unexpected_observed":len(observed-exp)}
    result={"left_rows":len(left),"right_rows":len(right),"left_keyed":len(lhs),"right_keyed":len(rhs),
            "left_unresolved":la,"right_unresolved":lb,"intersection":len(overlap),
            "left_only":len(ka-kb),"right_only":len(kb-ka),"union":len(ka|kb),
            "symmetric_difference":len(ka^kb),"same_value":exact_matches,
            "different_value":mismatches,"denominator":denominator,
            "authoritative_pair_identity":"UNRESOLVED","actual_election_discrepancy_proven":False,
            "certification":"AUDIT_ONLY","comparison_kind":"SYNTHETIC_KEY_INTERSECTION_NOT_LEGAL_FINDING"}
    assert result["union"]==result["intersection"]+result["symmetric_difference"]
    assert result["intersection"]==result["same_value"]+result["different_value"]
    assert result["left_rows"]==result["left_keyed"]+len(la)
    assert result["right_rows"]==result["right_keyed"]+len(lb)
    if la or lb:
        result["row_conservation"]="UNRESOLVED_ROWS_PRESERVED"
    else:result["row_conservation"]="ALL_FIXTURE_ROWS_CLASSIFIED"
    return result
