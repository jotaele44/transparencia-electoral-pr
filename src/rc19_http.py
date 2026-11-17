"""RC19: bounded, read-only HTTP publication intake.

The caller must supply an exact, pre-registered source record. GET only;
HTTPS, exact host allowlist, no redirects, no cookies/auth, no disk writes.
A 304 response is a server validator response, NOT a fresh byte comparison.
"""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler
import ssl

MAX_SINGLE_SOURCE_BYTES = 25_000_000
MAX_TIMEOUT_SECONDS = 20
TRUSTED_PUBLIC_HOSTS = frozenset({
    "www.ceepur.org", "ww2.ceepur.org", "bvirtualogp.pr.gov",
    "uscode.house.gov", "senado.pr.gov", "www.camara.pr.gov",
    "www-static.comisionadoelectoralpip.com", "www.lexjuris.com",
})
DEFAULT_CONTENT_TYPES = frozenset({
    "application/pdf", "text/html", "application/json", "text/plain"
})

class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def _utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("capture time must be ISO-8601 UTC Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid capture timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("capture timestamp must have zero UTC offset")
    return parsed

def _safe_header(value, name, limit=1024):
    if value is None:
        return None
    if not isinstance(value, str) or not value or len(value) > limit:
        raise ValueError(f"invalid {name} validator")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError(f"control character in {name}")
    return value

def _validate_source(source):
    if not isinstance(source, dict):
        raise ValueError("registered source record required")
    sid, url = source.get("source_id"), source.get("url")
    if not isinstance(sid, str) or not sid.strip():
        raise ValueError("stable source_id required")
    if not isinstance(url, str):
        raise ValueError("exact source URL required")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.fragment
            or (parsed.port is not None and parsed.port != 443)):
        raise ValueError("only exact public HTTPS URLs on default TLS port")
    hosts = source.get("allowed_hosts")
    if not isinstance(hosts, list) or not hosts or any(
        not isinstance(h, str) or h not in TRUSTED_PUBLIC_HOSTS for h in hosts
    ):
        raise ValueError("source host list is not in the static allowlist")
    if parsed.hostname.lower() not in hosts:
        raise ValueError("URL host is not authorized for this source")
    types = source.get("allowed_content_types", sorted(DEFAULT_CONTENT_TYPES))
    if not isinstance(types, list) or not types or any(t not in DEFAULT_CONTENT_TYPES for t in types):
        raise ValueError("unsupported content-type policy")
    limit = source.get("max_bytes", MAX_SINGLE_SOURCE_BYTES)
    timeout = source.get("timeout_seconds", 15)
    if type(limit) is not int or not 1 <= limit <= MAX_SINGLE_SOURCE_BYTES:
        raise ValueError("per-source byte limit outside hard ceiling")
    if type(timeout) not in (int, float) or not 1 <= timeout <= MAX_TIMEOUT_SECONDS:
        raise ValueError("timeout outside hard ceiling")
    return sid, url, parsed.hostname.lower(), frozenset(types), limit, float(timeout)

def _default_opener():
    # Disable environment proxies and automatic redirects. TLS verification
    # remains enabled by the standard SSL context.
    return build_opener(
        ProxyHandler({}),
        _RejectRedirects(),
    )

def fetch_read_only(source, *, observed_utc, previous=None, opener=None):
    """Fetch one exact registered public source into memory using HTTP GET only.

    Returns bytes to the caller; never writes files or sends alerts. Caller is
    responsible for freezing bytes and the returned manifest in an authorized
    evidence store. Redirects and partial responses fail closed.
    """
    sid, url, host, allowed_types, max_bytes, timeout = _validate_source(source)
    _utc(observed_utc)
    headers = {
        "Accept": ", ".join(sorted(allowed_types)),
        "Accept-Encoding": "identity",
        "User-Agent": "META2028-ReadOnly-Evidence-Monitor/1.0",
    }
    if previous is not None:
        if not isinstance(previous, dict) or previous.get("source_id") != sid:
            raise ValueError("previous snapshot source identity mismatch")
        etag = _safe_header(previous.get("etag"), "ETag")
        modified = _safe_header(previous.get("last_modified"), "Last-Modified", 256)
        if etag:
            headers["If-None-Match"] = etag
        if modified:
            headers["If-Modified-Since"] = modified
    request = Request(url, headers=headers, method="GET")
    client = opener if opener is not None else _default_opener()
    response = None
    not_modified = False
    try:
        response = client.open(request, timeout=timeout)
    except HTTPError as exc:
        if exc.code != 304:
            raise
        response = exc
        not_modified = True
    try:
        status = getattr(response, "status", None) or response.getcode()
        response_url = response.geturl() if hasattr(response, "geturl") else url
        if response_url != url:
            raise ValueError("response URL changed; redirects are not accepted")
        response_headers = response.headers
        etag = _safe_header(response_headers.get("ETag"), "ETag")
        modified = _safe_header(response_headers.get("Last-Modified"), "Last-Modified", 256)
        date_header = _safe_header(response_headers.get("Date"), "Date", 256)
        if status == 304 or not_modified:
            if previous is None or not (previous.get("etag") or previous.get("last_modified")):
                raise ValueError("304 without a prior conditional snapshot")
            return {
                "source_id": sid, "url": url, "observed_utc": observed_utc,
                "http_status": 304, "state": "HTTP_NOT_MODIFIED",
                "etag": etag or previous.get("etag"),
                "last_modified": modified or previous.get("last_modified"),
                "http_date": date_header, "sha256": previous.get("sha256"),
                "byte_length": previous.get("byte_length"), "payload": None,
                "byte_identity": "NOT_REVALIDATED_BYTES",
                "publication_change": "UNKNOWN",
            }
        if status != 200:
            raise ValueError(f"unexpected HTTP status {status}; only 200/304 accepted")
        encoding = response_headers.get("Content-Encoding")
        if encoding and encoding.strip().lower() not in ("", "identity"):
            raise ValueError("compressed representation rejected; request identity bytes")
        raw_type = response_headers.get("Content-Type", "")
        content_type = raw_type.split(";", 1)[0].strip().lower()
        if content_type not in allowed_types:
            raise ValueError("response content-type outside source policy")
        length = response_headers.get("Content-Length")
        if length is not None:
            if not length.isdigit():
                raise ValueError("invalid Content-Length")
            if int(length) > max_bytes:
                raise ValueError("Content-Length exceeds per-source limit")
        payload = response.read(max_bytes + 1)
        if not isinstance(payload, bytes) or not payload:
            raise ValueError("empty or non-byte response")
        if len(payload) > max_bytes:
            raise ValueError("streamed body exceeds per-source limit")
        if length is not None and len(payload) != int(length):
            raise ValueError("Content-Length/body length mismatch")
        if content_type == "application/pdf" and not payload.startswith(b"%PDF-"):
            raise ValueError("PDF content-type without PDF signature")
        digest = sha256(payload).hexdigest()
        state = "FIRST_OBSERVATION"
        if previous is not None:
            if previous.get("sha256") == digest:
                state = "BYTE_IDENTICAL"
            elif previous.get("url") == url:
                state = "SAME_URL_BYTES_CHANGED"
            else:
                state = "URL_AND_BYTES_CHANGED"
        return {
            "source_id": sid, "url": url, "observed_utc": observed_utc,
            "http_status": 200, "state": state, "etag": etag,
            "last_modified": modified, "http_date": date_header,
            "content_type": content_type, "content_length_header": length,
            "byte_length": len(payload), "sha256": digest, "payload": payload,
            "byte_identity": "HASHED_RESPONSE_BODY",
            "publication_change": "REVIEW_REQUIRED" if state not in ("FIRST_OBSERVATION", "BYTE_IDENTICAL") else "NOT_ESTABLISHED",
        }
    finally:
        if response is not None and hasattr(response, "close"):
            response.close()
