"""Separated sandbox checkpoint receipt store. NOT a real off-site WORM anchor.

It refuses overwrites and validates independent receipt bytes; both stores
still share the local trust domain in this test.
"""
import hashlib
import json
import os
from pathlib import Path
from rc6_security import canonical
from rc7_guards import verify_checkpoint

def anchor_once(directory, checkpoint):
    if not isinstance(checkpoint,dict):
        raise ValueError("checkpoint required")
    digest=checkpoint.get("checkpoint_sha256")
    if not verify_checkpoint(checkpoint, trusted_external_digest=digest):
        raise ValueError("checkpoint invalid")
    root=Path(directory)
    if not root.is_dir():
        raise ValueError("anchor directory missing")
    file=root / (digest+".json")
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    if hasattr(os,"O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    payload=canonical({"checkpoint":checkpoint, "digest":digest})+b"\n"
    fd=os.open(file,flags,0o600)
    with os.fdopen(fd,"wb") as out:
        out.write(payload)
        out.flush()
        os.fsync(out.fileno())
    return {"receipt_file":str(file),"receipt_sha256":hashlib.sha256(payload).hexdigest(),"sandbox_only":True}

def verify_anchor(receipt_file, expected_receipt_sha256, checkpoint, *, minimum_sequence=1):
    if not isinstance(expected_receipt_sha256,str) or len(expected_receipt_sha256)!=64:
        return False
    try:
        payload=Path(receipt_file).read_bytes()
        if hashlib.sha256(payload).hexdigest()!=expected_receipt_sha256:
            return False
        obj=json.loads(payload)
        if set(obj)!={"checkpoint","digest"} or obj["checkpoint"]!=checkpoint:
            return False
        return verify_checkpoint(checkpoint, trusted_external_digest=obj["digest"],minimum_sequence=minimum_sequence)
    except (OSError,TypeError,ValueError,KeyError):
        return False
