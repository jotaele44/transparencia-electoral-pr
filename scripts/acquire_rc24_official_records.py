#!/usr/bin/env python3
"""Acquire only allowlisted primary electoral/legal records for RC24.

Raw originals are retained as a CI artifact, not committed into Git. Failures
are recorded without inventing a digest. No datasets or voter records are fetched.
"""
from __future__ import annotations
import hashlib, json, mimetypes, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

SOURCES = [
 ("CEE-AC-26-110","https://www.ceepur.org/acuerdos-de-comision/docs/2026/CEE-AC-26-110.pdf","pdf"),
 ("CEE-AC-26-149","https://www.ceepur.org/acuerdos-de-comision/docs/2026/CEE-AC-26-149.pdf","pdf"),
 ("CEE-RS-26-010","https://www.ceepur.org/resoluciones-de-comision/2026/CEE-RS-26-010.pdf","pdf"),
 ("CEE-AC-25-112","https://www.ceepur.org/acuerdos-de-comision/docs/ACUERDO-CEE-AC-25-112-APROBACION-DE-PROPUESTA-Y-CALENDARIO-DE-EJECUCION-PROPUESTO-PARA-MEJORAS-AL-MODULO-eRE.pdf","pdf"),
 ("CEE-AC-25-031","https://www.ceepur.org/acuerdos-de-comision/docs/2025/CEE-AC-25-031.pdf","pdf"),
 ("CEE-AC-25-009","https://www.ceepur.org/acuerdos-de-comision/docs/2025/CEE-AC-25-009.pdf","pdf"),
 ("CEE-AC-26-113","https://www.ceepur.org/acuerdos-de-comision/docs/2026/CEE-AC-26-113.pdf","pdf"),
 ("SENATE-ACTA-2026-03-12","https://senado.pr.gov/document_vault/actas_senado/0312.26.pdf","pdf"),
 ("LEY39-SUTRA-PDF","https://sutra.oslpr.org/SutraFilesGen/158328/0039s0717.pdf","pdf"),
 ("LEY39-SUTRA-DOC","https://sutra.oslpr.org/SutraFilesGen/158328/0039s0717.doc","doc"),
 ("CEE-2028-REGULATIONS-INDEX","https://www.ceepur.org/reglamentos/","html"),
 ("CEE-JAVAA-PUBLIC-GUIDANCE","https://ww2.ceepur.org/Home/SolicituddeVoto","html"),
 ("CEE-2028-RFP-CALENDAR-CONTEXT","https://www.ceepur.org/subastas/docs/2026/RFP-Escrutinio/us/RFP-Opscan-2028-EN-FINAL.pdf","pdf"),
]
ALLOWED={"ceepur.org","www.ceepur.org","ww2.ceepur.org","senado.pr.gov","sutra.oslpr.org"}
MAX_BYTES=50*1024*1024
OUT=Path("artifacts/rc24")
def now(): return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def acquire(item):
    rid,url,kind=item
    host=(urlparse(url).hostname or "").lower()
    if host not in ALLOWED: raise ValueError(f"host not allowlisted: {host}")
    entry={"id":rid,"url":url,"retrieved_at_utc":now(),"status":"OPEN","http_status":None,
           "content_type":None,"bytes":None,"sha256":None,"path":None,"pdf_pages":None,
           "pdf_metadata":None,"error":None}
    for attempt in range(3):
        try:
            req=Request(url,headers={"User-Agent":"transparencia-electoral-pr/RC24 primary-record preservation; contact via public CEE channels","Accept":"application/pdf,application/msword,application/octet-stream,text/html,*/*"})
            with urlopen(req,timeout=35) as response:
                status=response.status
                data=response.read(MAX_BYTES+1)
                entry["http_status"]=status
                entry["content_type"]=response.headers.get("Content-Type")
                entry["final_url"]=response.geturl()
            if len(data)>MAX_BYTES: raise ValueError("response exceeds 50 MiB bounded acquisition limit")
            if kind=="pdf" and not data.startswith(b"%PDF-"):
                raise ValueError("response is not a PDF byte stream")
            if kind=="html" and not (b"<html" in data[:2048].lower() or b"<!doctype" in data[:2048].lower()):
                raise ValueError("response is not recognizable HTML")
            if kind=="doc" and not (data.startswith(bytes.fromhex("D0CF11E0A1B11AE1")) or data.startswith(b"PK")):
                raise ValueError("response is not recognizable DOC/DOCX bytes")
            ext={"pdf":"pdf","doc":"doc","html":"html"}[kind]
            target=OUT/"raw"/f"{rid}.{ext}"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            entry.update(status="ACQUIRED",bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),path=str(target))
            if kind=="pdf":
                try:
                    from pypdf import PdfReader
                    reader=PdfReader(str(target),strict=False)
                    entry["pdf_pages"]=len(reader.pages)
                    md=reader.metadata
                    entry["pdf_metadata"]={str(k):str(v) for k,v in (md or {}).items()}
                except Exception as e:
                    entry["pdf_metadata_error"]=f"{type(e).__name__}: {e}"
            return entry
        except HTTPError as e:
            entry.update(http_status=e.code,error=f"HTTPError: {e.reason}")
            if e.code not in (408,425,429,500,502,503,504): break
        except (URLError,TimeoutError,ConnectionError) as e:
            entry["error"]=f"{type(e).__name__}: {e}"
        except Exception as e:
            entry["error"]=f"{type(e).__name__}: {e}"
            break
        if attempt<2: time.sleep(2**(attempt+1))
    entry["status"]="BLOCKED" if entry["http_status"] in (401,403,404,410) else "FAILED"
    return entry
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results=[acquire(s) for s in SOURCES]
    manifest={"release":"RC24","acquisition_time_utc":now(),"scope":"13 allowlisted official primary sources only","sources":results,
      "counts":{"requested":len(results),"acquired":sum(x["status"]=="ACQUIRED" for x in results),
      "blocked":sum(x["status"]=="BLOCKED" for x in results),"failed":sum(x["status"]=="FAILED" for x in results)},
      "note":"A successful HTTP fetch and SHA-256 prove acquired bytes for this retrieval only; neither proves legal authority, document completeness, or factual claims within the document."}
    (OUT/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest["counts"],sort_keys=True))
    for x in results: print(json.dumps({k:x.get(k) for k in ("id","status","http_status","bytes","sha256","pdf_pages","error")},ensure_ascii=False))
if __name__=="__main__": main()
