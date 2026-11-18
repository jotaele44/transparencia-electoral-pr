"""RC26 strict read-only verifier for frozen RC24 targeted source artifact.

Does not alter or extract evidence. Zip member byte identity is verified
independently against embedded acquisition manifest and caller-pinned ZIP SHA.
"""
from __future__ import annotations
from zipfile import ZipFile
from pathlib import Path, PurePosixPath
from hashlib import sha256
import argparse,json,stat,sys,os

PINNED_RC24_ROUND2_SHA256="553be37c5b5931b1c0e6ff92c652d102c5527772aadf4a4dac32e429fccf95cf"
MAX_ZIP_BYTES=80_000_000
MAX_TOTAL_UNCOMPRESSED=100_000_000

def verify_archive(path,expected_zip_sha):
    p=Path(path)
    if not p.is_file() or p.stat().st_size<=0 or p.stat().st_size>MAX_ZIP_BYTES:
        raise ValueError("missing or oversized frozen artifact")
    if not isinstance(expected_zip_sha,str) or len(expected_zip_sha)!=64:
        raise ValueError("exact ZIP SHA required")
    outer=sha256(p.read_bytes()).hexdigest()
    if outer!=expected_zip_sha:raise ValueError("outer archive hash mismatch")
    with ZipFile(p) as z:
        infos=z.infolist()
        names=[x.filename for x in infos if not x.is_dir()]
        if len(names)!=len(set(names)):raise ValueError("duplicate archive path")
        if sum(x.file_size for x in infos)>MAX_TOTAL_UNCOMPRESSED:
            raise ValueError("uncompressed archive too large")
        for x in infos:
            norm=PurePosixPath(x.filename)
            if norm.is_absolute() or '..' in norm.parts or '\\' in x.filename:
                raise ValueError("unsafe archive path")
            if stat.S_ISLNK(x.external_attr >> 16):
                raise ValueError("archive link forbidden")
        if "source_manifest.json" not in names:raise ValueError("manifest missing")
        manifest=json.loads(z.read("source_manifest.json"))
        counts=manifest["counts"]
        expected=("requested","acquired","blocked","failed")
        if any(type(counts.get(k)) is not int or counts[k]<0 for k in expected):
            raise ValueError("invalid manifest denominator")
        if counts["requested"]!=counts["acquired"]+counts["blocked"]+counts["failed"]:
            raise ValueError("source count mismatch")
        rows=manifest["sources"]
        if len(rows)!=counts["requested"]:raise ValueError("source row conservation failed")
        good=[];failed=[];raw=set()
        ids=set()
        for r in rows:
            ident=r["id"]
            if not isinstance(ident,str) or not ident or ident in ids:raise ValueError("duplicate/invalid source ID")
            ids.add(ident)
            if r["status"]=="ACQUIRED":
                rel=r["path"]
                if not isinstance(rel,str):raise ValueError("missing original pathname")
                member="raw/"+os.path.basename(rel)
                if member not in names:raise ValueError("source member missing: "+member)
                b=z.read(member)
                digest=sha256(b).hexdigest()
                if digest!=r["sha256"] or len(b)!=r["bytes"]:
                    raise ValueError("original source byte identity mismatch: "+ident)
                good.append({"source_id":ident,"path":member,"bytes":len(b),"sha256":digest})
                raw.add(member)
            elif r["status"] in ("FAILED","BLOCKED"):
                if r.get("sha256") is not None or r.get("path") is not None:
                    raise ValueError("unacquired source has bytes/hash")
                failed.append({"source_id":ident,"state":r["status"]})
            else:raise ValueError("unrecognized acquisition status")
        if len(good)!=counts["acquired"] or len(failed)!=counts["failed"]+counts["blocked"]:
            raise ValueError("acquired/failed category counts inconsistent")
        if set(names)-raw-{"source_manifest.json"}:
            raise ValueError("unmanifested source payload in archive")
    return {"result":"LOCAL_READBACK_PASS","archive_sha256":outer,"archive_size_bytes":p.stat().st_size,
        "source_rows":len(rows),"originals_rehashed":len(good),
        "source_failures":failed,"member_sha256":good,
        "independent_offdevice_recovery_pass":False,
        "remote_storage_destination_verified":False,
        "source_authenticity_not_proven_by_hash_alone":True,
        "certification":"AUDIT_ONLY"}

if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("archive",help="Previously downloaded official RC24 artifact ZIP")
 parser.add_argument("--sha256",default=PINNED_RC24_ROUND2_SHA256)
 a=parser.parse_args()
 print(json.dumps(verify_archive(a.archive,a.sha256),ensure_ascii=False,sort_keys=True,indent=2))
