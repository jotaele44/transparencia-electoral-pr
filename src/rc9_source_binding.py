"""Conservative source and election-reporting identity proof gates, offline only."""
from collections import Counter
from datetime import datetime
from hashlib import sha256
from pathlib import Path

REQUIRED=("source_id","authority","source_epoch","geographic_level","sha256","bytes")
SPECIAL_UNITS={"72":"EARLY_MAIL","73":"ACCESSIBLE_HOME","74":"JAVAA_SPECIAL_COLLEGE","76":"INCARCERATED","77":"ABSENTEE"}

def verify_manifestation(item):
    if not isinstance(item,dict) or any(k not in item for k in REQUIRED):
        raise ValueError("missing required source manifestation fields")
    raw=item["bytes"]
    if not isinstance(raw,bytes):
        raise ValueError("original source bytes required")
    digest=item["sha256"]
    if not isinstance(digest,str) or len(digest)!=64 or any(x not in "0123456789abcdef" for x in digest):
        raise ValueError("invalid sha256")
    if sha256(raw).hexdigest()!=digest:raise ValueError("source bytes do not match digest")
    if any(not isinstance(item[k],str) or not item[k].strip() for k in ("source_id","authority","source_epoch","geographic_level")):
        raise ValueError("source identity metadata missing")
    return {k:item[k] for k in REQUIRED if k!="bytes"}

def bind_pair(left,right,*,official_relation_id=None,scope_verified=False,identity_verified=False):
    a,b=verify_manifestation(left),verify_manifestation(right)
    if a["source_id"]==b["source_id"] and a["sha256"]!=b["sha256"]:
        raise ValueError("ambiguous source id reused across different bytes")
    if official_relation_id is None or not isinstance(official_relation_id,str) or not official_relation_id.strip():
        return {"status":"UNRESOLVED","reason":"NO_AUTHORITATIVE_PAIR_BINDING","left":a,"right":b}
    if scope_verified is not True or identity_verified is not True:
        return {"status":"CANDIDATE_NOT_IDENTITY","reason":"SOURCE_SCOPE_OR_RECORD_IDENTITY_UNVERIFIED","left":a,"right":b}
    if a["geographic_level"]!=b["geographic_level"]:
        raise ValueError("geographic aggregation levels differ")
    return {"status":"BOUND_EVIDENCE_CANDIDATE","relation_id":official_relation_id,"left":a,"right":b,"certification":"PROVISIONAL"}

def classify_unit(raw):
    if not isinstance(raw,str) or not raw:
        return {"state":"UNRESOLVED","unit_raw":raw}
    if raw in SPECIAL_UNITS:
        return {"state":"SPECIAL_VOTING_MODALITY","unit_raw":raw,"modality":SPECIAL_UNITS[raw],"normal_spatial_college_equivalence":False}
    return {"state":"STANDARD_CANDIDATE_NOT_IDENTITY","unit_raw":raw,"modality":None,"normal_spatial_college_equivalence":None}

def municipal_snapshot(rows):
    """Preserve per-municipality coverage; do not infer islandwide totals."""
    if not isinstance(rows,list):raise ValueError("rows must be list")
    result={};bad=[]
    for index,row in enumerate(rows):
        if not isinstance(row,dict) or any(k not in row for k in ("municipality_id","reported","total")):
            bad.append(index);continue
        key=row["municipality_id"]
        a,b=row["reported"],row["total"]
        if not isinstance(key,str) or not key.strip() or type(a) is not int or type(b) is not int or a<0 or b<0 or a>b or key in result:
            bad.append(index);continue
        result[key]={"reported":a,"total":b,"unreported":b-a}
    return {"input_count":len(rows),"validated_count":len(result),"unresolved_count":len(bad),"unresolved_indices":bad,"municipalities":result,"islandwide_complete":False,"certification":"CANDIDATE_NOT_IDENTITY"}
