"""Fail-closed offline election-integrity case protocol. No external I/O or enforcement."""
import hashlib
import json
from datetime import datetime, timezone

STATES=("DETECTED","TRIAGED","EVIDENCE_VERIFIED","HUMAN_REVIEWED","REFERRAL_READY","REFERRED","OFFICIAL_DISPOSITION","CLOSED","WITHDRAWN")
ROUTES={"ELECTORAL_ADMINISTRATION":"CEE","RESULT_DISCREPANCY":"CEE","EQUIPMENT_PROCUREMENT":"CEE_REVIEW_REQUIRED","CAMPAIGN_FINANCE":"OCE","BOUNDARY_CHANGE":"CEE_REVIEW_REQUIRED","OTHER":"JURISDICTION_REVIEW"}
SENSITIVE={"voter_id","voter_name","voter_address","social_security_number","ssn","date_of_birth","phone","email","password","token","secret","credential","ip_address","precise_home_location"}
SEVERITIES={"UNASSESSED","LOW","MODERATE","HIGH"}
ALLOWED={"DETECTED":{"TRIAGED","WITHDRAWN"},"TRIAGED":{"EVIDENCE_VERIFIED","WITHDRAWN"},"EVIDENCE_VERIFIED":{"HUMAN_REVIEWED","WITHDRAWN"},"HUMAN_REVIEWED":{"REFERRAL_READY","WITHDRAWN"},"REFERRAL_READY":{"REFERRED","WITHDRAWN"},"REFERRED":{"OFFICIAL_DISPOSITION"},"OFFICIAL_DISPOSITION":{"CLOSED"},"CLOSED":set(),"WITHDRAWN":set()}

def _canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf-8")

def _check_privacy(node):
    if isinstance(node,dict):
        for k,v in node.items():
            if str(k).lower() in SENSITIVE: raise ValueError("sensitive field not permitted")
            _check_privacy(v)
    elif isinstance(node,list):
        for x in node:_check_privacy(x)

def _timestamp(s):
    if not isinstance(s,str) or not s.endswith("Z"):raise ValueError("UTC Z timestamp required")
    try:
        dt=datetime.fromisoformat(s.replace("Z","+00:00"))
    except (TypeError,ValueError) as exc:raise ValueError("invalid timestamp") from exc
    if dt.utcoffset().total_seconds()!=0:raise ValueError("must be UTC")
    return dt

def evidence(source_id,sha256,source_class="PRIMARY",contradictory=False):
    if not isinstance(source_id,str) or not source_id.strip():raise ValueError("source_id required")
    if not isinstance(sha256,str) or len(sha256)!=64 or any(ch not in "0123456789abcdef" for ch in sha256):raise ValueError("verified byte hash required")
    if source_class not in ("PRIMARY","INDEPENDENT_CORROBORATION"):raise ValueError("invalid source class")
    if type(contradictory) is not bool:raise ValueError("invalid contradictory marker")
    return {"source_id":source_id,"sha256":sha256,"source_class":source_class,"contradictory":contradictory}

def new_case(case_id,kind,detected_at,summary,*,synthetic=True):
    if synthetic is not True:raise PermissionError("RC5 supports synthetic cases only")
    if not isinstance(case_id,str) or not case_id.strip() or kind not in ROUTES:raise ValueError("invalid case id/type")
    if not isinstance(summary,str) or not summary.strip():raise ValueError("summary required")
    if any(term in summary.lower() for term in ("fraud proven","guilty","rigged election","stolen election")):raise ValueError("unsupported accusation")
    _timestamp(detected_at)
    o={"case_id":case_id,"kind":kind,"authority_candidate":ROUTES[kind],"summary":summary,"synthetic":True,"status":"DETECTED","severity":"UNASSESSED","evidence":[],"events":[],"referral_receipt":None,"public_release_authorized":False}
    _check_privacy(o)
    return o

def prioritize(case,*,document_discrepancy=False,deadline_proximity=False,impact_scope="UNKNOWN"):
    if type(document_discrepancy) is not bool or type(deadline_proximity) is not bool:raise ValueError("boolean indicators required")
    if impact_scope not in ("UNKNOWN","SINGLE_RECORD","MULTI_RECORD"):raise ValueError("invalid impact scope")
    # Priority is workflow triage only, not a finding on illegality or validity.
    score=15*document_discrepancy+10*deadline_proximity+10*(impact_scope=="MULTI_RECORD")
    return {"review_priority":score,"assessment":"CANDIDATE_NOT_FINDING","fraud_determination":None}

def transition(case,to_status,*,actor,timestamp,reason,sources=(),reviewer=None,authorized_by=None,receipt=None):
    if not isinstance(case,dict) or case.get("synthetic") is not True:raise PermissionError("synthetic-only RC5")
    _check_privacy(case)
    prev=case.get("status")
    if to_status not in ALLOWED.get(prev,set()):raise ValueError("illegal lifecycle transition")
    if not isinstance(actor,str) or not actor.strip() or not isinstance(reason,str) or not reason.strip():raise ValueError("actor and reason required")
    when=_timestamp(timestamp)
    if case["events"] and when<_timestamp(case["events"][-1]["timestamp"]):raise ValueError("nonmonotonic event time")
    if to_status=="EVIDENCE_VERIFIED":
        if not sources or not any(s.get("source_class")=="PRIMARY" for s in sources):raise ValueError("independent primary evidence required")
        ids=set()
        for s in sources:
            v=evidence(**s)
            if v["source_id"] in ids:raise ValueError("duplicate evidence id")
            ids.add(v["source_id"])
        case["evidence"]=[dict(s) for s in sources]
    if to_status=="HUMAN_REVIEWED":
        if not isinstance(reviewer,str) or not reviewer.strip() or reviewer==actor:raise PermissionError("separate identified reviewer required")
        if not case["evidence"]:raise ValueError("missing verified evidence")
    if to_status=="REFERRAL_READY":
        if case["authority_candidate"] not in ("CEE","OCE"):raise PermissionError("jurisdiction not adjudicated")
        if not case["evidence"]:raise ValueError("evidence missing")
        if not case.get("reviewed_by"):raise PermissionError("human review required")
    if to_status=="REFERRED":
        if not isinstance(authorized_by,str) or not authorized_by.strip() or authorized_by in (actor,case.get("reviewed_by")):raise PermissionError("separate authorization required")
        if not isinstance(receipt,str) or not receipt.strip():raise PermissionError("external receipt required; tool does not submit")
        case["referral_receipt"]=receipt
    if to_status=="OFFICIAL_DISPOSITION" and not sources:raise ValueError("official disposition reference required")
    if to_status=="HUMAN_REVIEWED":case["reviewed_by"]=reviewer
    previous_hash=case["events"][-1]["event_sha256"] if case["events"] else None
    event={"sequence":len(case["events"])+1,"from":prev,"to":to_status,"timestamp":timestamp,"actor":actor,"reason":reason,"source_ids":sorted(s["source_id"] for s in sources),"previous_hash":previous_hash}
    event["event_sha256"]=hashlib.sha256(_canonical(event)).hexdigest()
    case["events"].append(event)
    case["status"]=to_status
    _check_privacy(case)
    return case

def verify_event_chain(case):
    prior=None
    for i,e in enumerate(case.get("events",[])):
        if e.get("sequence")!=i+1 or e.get("previous_hash")!=prior:return False
        unsigned={k:v for k,v in e.items() if k!="event_sha256"}
        digest=hashlib.sha256(_canonical(unsigned)).hexdigest()
        if digest!=e.get("event_sha256"):return False
        prior=digest
    return True
