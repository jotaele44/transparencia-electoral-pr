"""Offline write-once demo files + verifiable chain. Not WORM or immutable storage."""
import hashlib
import json
import os
from pathlib import Path
from rc6_security import canonical

def build_chain(entries):
    if not isinstance(entries,list): raise ValueError("event list required")
    previous=None
    result=[]
    for index,event in enumerate(entries,1):
        if not isinstance(event,dict) or set(event)!={"event_id","event_type","synthetic"}: raise ValueError("unrecognized event")
        if event["synthetic"] is not True: raise PermissionError("real events disabled")
        if not isinstance(event["event_id"],str) or not event["event_id"].strip(): raise ValueError("event id required")
        if event["event_type"] not in ("CREATED","TRIAGED","REVIEWED","WITHDRAWN"): raise ValueError("event not allowed")
        if any(row["event_id"]==event["event_id"] for row in result): raise ValueError("duplicate event id")
        record={**event,"index":index,"prev_digest":previous}
        record["digest"]=hashlib.sha256(canonical(record)).hexdigest()
        previous=record["digest"]
        result.append(record)
    return result

def verify_chain(chain, *, expected_tip=None, expected_count=None):
    if not isinstance(chain,list): return False
    if expected_count is not None and len(chain)!=expected_count:return False
    prev=None
    ids=set()
    for idx,row in enumerate(chain,1):
        if not isinstance(row,dict) or row.get("index")!=idx or row.get("prev_digest")!=prev:return False
        if row.get("event_id") in ids:return False
        ids.add(row.get("event_id"))
        try:
            digest=hashlib.sha256(canonical({k:v for k,v in row.items() if k!="digest"})).hexdigest()
        except (ValueError,TypeError):return False
        if row.get("digest")!=digest:return False
        prev=digest
    return expected_tip is None or prev==expected_tip

def write_once(target,chain):
    """O_EXCL denies overwrite; no security claims for host privileged users."""
    if not verify_chain(chain): raise ValueError("invalid chain")
    target=Path(target)
    if not target.parent.is_dir(): raise ValueError("parent missing")
    blob=canonical({"events":chain,"count":len(chain),"tip":chain[-1]["digest"] if chain else None})+b"\n"
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    if hasattr(os,"O_NOFOLLOW"):flags|=os.O_NOFOLLOW
    fd=os.open(target,flags,0o600)
    try:
        with os.fdopen(fd,"wb") as file:
            file.write(blob)
            file.flush()
            os.fsync(file.fileno())
    except BaseException:
        try:target.unlink()
        except OSError:pass
        raise
    return hashlib.sha256(blob).hexdigest()

def verify_snapshot(path,expected_sha256):
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64:return False
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:return False
    try:
        doc=json.loads(raw)
        if set(doc)!={"events","count","tip"}:return False
        return verify_chain(doc["events"],expected_tip=doc["tip"],expected_count=doc["count"])
    except (ValueError,TypeError,KeyError):return False
