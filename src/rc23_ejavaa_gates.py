"""RC23: CEE eRE/eJAVAA agreement vs actual release evidence gates.

An official test-report approval and instruction to pursue operation are not
proof of successful deployment, current system security or 2028 operability.
"""
from __future__ import annotations
from hashlib import sha256

REQUIRED=("source_test_report","system_version","implementation_schedule",
          "deployment_receipt","security_qa","consumer_operability")

def classify_commission_agreement(record):
    if not isinstance(record,dict) or record.get("id")!="cee_ac_26_110":
        raise ValueError("specific CEE-AC-26-110 record required")
    if record.get("operative_action")!="UNANIMOUS_TEST_REPORT_APPROVAL_AND_OSIPE_DIRECTED_TO_TAKE_STEPS_TO_PUT_NEW_eRE_eJAVAA_VERSION_IN_OPERATION":
        raise ValueError("operative wording unresolved")
    if record.get("sha256") is not None and record.get("original_bytes_acquired") is not True:
        raise ValueError("cannot attach a source hash without original bytes")
    return {"authorized_to_pursue_operation":True,"actual_deployment_verified":False,
            "test_report_content_verified":False,"independent_security_qa_verified":False,
            "statutory_2028_readiness_certified":False,"classification":"DOCUMENTED_AUTHORIZATION_NOT_EXECUTION"}

def release_gate(rows):
    if not isinstance(rows,list):raise ValueError("gate list required")
    ids=[r.get("key") for r in rows if isinstance(r,dict)]
    if len(ids)!=len(rows) or set(ids)!=set(REQUIRED) or len(ids)!=len(set(ids)):
        raise ValueError("release gate cardinality mismatch")
    unresolved=[];accepted=[]
    for row in rows:
        if row.get("state") not in ("OPEN","BLOCKED","PASS"):
            raise ValueError("unrecognized gate state")
        if row["state"]=="PASS":
            if not row.get("original_source_bytes") or not isinstance(row["original_source_bytes"],bytes):
                raise ValueError("PASS requires original bytes")
            if not isinstance(row.get("sha256"),str) or sha256(row["original_source_bytes"]).hexdigest()!=row["sha256"]:
                raise ValueError("PASS requires matching digest")
            if not row.get("independent_review_receipt"):
                raise ValueError("PASS requires independent review")
            accepted.append(row["key"])
        else:
            unresolved.append(row["key"])
    return {"required":len(REQUIRED),"passed_source_integrity_and_review":len(accepted),
            "unresolved":sorted(unresolved),"production_release_approved":False,
            "classification":"AUDIT_ONLY"}

def source_identity(a,b):
    if not isinstance(a,dict) or not isinstance(b,dict):raise ValueError("source objects required")
    if any(not isinstance(r.get(k),str) or not r[k] for r in (a,b) for k in ("id","url")):
        return {"status":"UNRESOLVED","same_original_source_proven":False}
    if a["id"]!=b["id"] or a["url"]!=b["url"]:
        return {"status":"DISTINCT_MANIFESTATIONS","same_original_source_proven":False}
    return {"status":"SAME_SOURCE_LOCATOR_CANDIDATE","same_original_source_proven":False}
