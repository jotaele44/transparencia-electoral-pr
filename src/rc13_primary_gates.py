"""RC13 conservative primary-source and electoral identity gate (pure offline tests)."""
from hashlib import sha256
from datetime import datetime, timezone

def require_manifestation(source):
    fields=("source_id","original_bytes","sha256","authority","source_epoch","source_url")
    if not isinstance(source,dict) or any(k not in source for k in fields):
        raise ValueError("original-byte source fields required")
    if any(not isinstance(source[k],str) or not source[k].strip() for k in ("source_id","authority","source_epoch","source_url")):
        raise ValueError("source identity incomplete")
    if not source["source_url"].startswith("https://"):raise ValueError("source URL invalid")
    if not isinstance(source["original_bytes"],bytes):raise ValueError("bytes unavailable")
    digest=source["sha256"]
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("invalid sha256")
    if sha256(source["original_bytes"]).hexdigest()!=digest:raise ValueError("sha256 mismatch")
    return {"source_id":source["source_id"],"source_epoch":source["source_epoch"],"authority":source["authority"],"sha256":digest,"length":len(source["original_bytes"])}

def compare_report_manifestations(left,right,*,authoritative_crosswalk=None):
    a,b=require_manifestation(left),require_manifestation(right)
    if a["source_id"]==b["source_id"] and a["sha256"]!=b["sha256"]:
        raise ValueError("source ID collision")
    if a["source_epoch"]==b["source_epoch"]:raise ValueError("source epochs must differ")
    # Crosswalk requires a distinct signed authoritative document: its name or operator declaration is not enough.
    identity="UNRESOLVED"
    if authoritative_crosswalk is not None:
        c=require_manifestation(authoritative_crosswalk)
        if c["source_id"] in {a["source_id"],b["source_id"]}:raise ValueError("self attestment forbidden")
        identity="CANDIDATE_NOT_IDENTITY"
    return {"source_version_relation":"BYTE_IDENTICAL" if a["sha256"]==b["sha256"] else "BYTE_DIFFERENT",
            "logical_relation":identity,"real_result_comparison":"BLOCKED",
            "certification":"AUDIT_ONLY"}

def reconcile_unit_keys(left,right,*,ballot_type,authoritative_unit_map=None):
    """Observe raw tuples only; do not merge special units or differing source epochs."""
    if not isinstance(ballot_type,str) or ballot_type not in ("ESTATAL","LEGISLATIVA","MUNICIPAL","PRESIDENCIAL","PLEBISCITO"):
        raise ValueError("ballot type required")
    if authoritative_unit_map is not None: raise PermissionError("real unit crosswalk not yet certified")
    def idx(records):
        if not isinstance(records,list):raise ValueError("rows list required")
        out={};unresolved=[]
        for position,r in enumerate(records):
            fields=("source_epoch","municipality_raw","precinct_raw","unit_raw","college_raw","ballot_type")
            if not isinstance(r,dict) or any(k not in r for k in fields):
                unresolved.append({"index":position,"reason":"MISSING_FIELDS"});continue
            if any(not isinstance(r[k],str) or not r[k] for k in fields):
                unresolved.append({"index":position,"reason":"INVALID_RAW_KEY"});continue
            if r["ballot_type"]!=ballot_type:
                unresolved.append({"index":position,"reason":"BALLOT_SCOPE_CONFLICT"});continue
            key=tuple(r[k] for k in fields)
            if key in out:
                unresolved.append({"index":position,"reason":"DUPLICATE_KEY"});continue
            out[key]=r
        return out,unresolved
    a,ua=idx(left);b,ub=idx(right)
    ka,kb=set(a),set(b)
    return {"left_rows":len(left),"right_rows":len(right),
            "left_keyed":len(a),"right_keyed":len(b),
            "left_unresolved":ua,"right_unresolved":ub,
            "intersection":len(ka&kb),"left_only":len(ka-kb),"right_only":len(kb-ka),
            "union":len(ka|kb),"symmetric_difference":len(ka^kb),
            "official_denominator":None,"identity":"CANDIDATE_NOT_IDENTITY",
            "counts_close":len(a)+len(ua)==len(left) and len(b)+len(ub)==len(right)
                and len(ka|kb)==len(ka&kb)+len(ka^kb),
            "certification":"UNRESOLVED"}
