"""RC19 bounded read-only HTTP publication acquisition.

GET-only, HTTPS-only, exact-host allowlisted, redirect-blocked and bounded.
Response bytes remain in memory; no persistence, scheduling, alerts, enforcement,
or legal adjudication. Production use additionally requires network egress controls.
"""
from __future__ import annotations
from ipaddress import ip_address
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from rc18_publication import intake, MAX_BYTES

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def _header(headers, name):
    try:
        return headers.get(name)
    except AttributeError:
        return None

def _safe_header(value, name):
    if value is None:
        return None
    if not isinstance(value, str) or chr(13) in value or chr(10) in value:
        raise ValueError(f"invalid {name} header value")
    return value

def _validate_target(url, allowed_hosts):
    if not isinstance(url, str):
        raise ValueError("exact URL required")
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.fragment:
        raise ValueError("HTTPS URL without credentials or fragment required")
    try:
        if p.port not in (None, 443):
            raise ValueError("nonstandard HTTPS port prohibited")
    except ValueError as exc:
        raise ValueError("invalid URL port") from exc
    host = p.hostname.lower()
    try:
        ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("IP-literal hosts prohibited")
    if not isinstance(allowed_hosts, (set, frozenset, list, tuple)):
        raise ValueError("exact host allowlist required")
    if host not in {str(x).lower() for x in allowed_hosts}:
        raise PermissionError("host not in exact allowlist")
    return host

def _not_modified(source_id, url, previous, headers=None):
    if previous is None or previous.get("url") != url or not previous.get("sha256"):
        return {"state": "NOT_MODIFIED_WITHOUT_BASELINE", "source_id": source_id,
                "url": url, "status": 304, "payload_bytes": None, "sha256": None,
                "source_deletion_proven": False, "legal_change_verified": False,
                "alert_allowed": False}
    return {"state": "NOT_MODIFIED", "source_id": source_id, "url": url, "status": 304,
            "sha256": previous["sha256"], "byte_length": previous.get("byte_length"),
            "etag": _header(headers, "ETag") or previous.get("etag"),
            "last_modified": _header(headers, "Last-Modified") or previous.get("last_modified"),
            "payload_bytes": None, "source_deletion_proven": False,
            "legal_change_verified": False, "alert_allowed": False}

def fetch_publication(*, source_id, url, observed_utc, allowed_hosts, previous=None,
                      timeout=10, max_bytes=10_000_000, opener=None):
    """Fetch one caller-authorized source once; return observation and in-memory bytes."""
    _validate_target(url, allowed_hosts)
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source ID required")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0.1 <= timeout <= 30:
        raise ValueError("timeout must be 0.1..30 seconds")
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or not 1 <= max_bytes <= MAX_BYTES:
        raise ValueError("max_bytes outside bounded range")
    headers = {
        "Accept": "application/pdf,text/html,application/json,text/plain;q=0.9",
        "User-Agent": "Transparencia-Electoral-PR/RC19 read-only"
    }
    if previous is not None:
        if not isinstance(previous, dict) or previous.get("source_id") != source_id:
            raise ValueError("previous observation must use same source ID")
        if previous.get("url") == url:
            etag = _safe_header(previous.get("etag"), "ETag")
            modified = _safe_header(previous.get("last_modified"), "Last-Modified")
            if etag:
                headers["If-None-Match"] = etag
            if modified:
                headers["If-Modified-Since"] = modified
    req = Request(url, headers=headers, method="GET")
    client = opener if opener is not None else build_opener(_NoRedirect())
    response = None
    try:
        response = client.open(req, timeout=float(timeout))
    except HTTPError as exc:
        try:
            if exc.code == 304:
                return _not_modified(source_id, url, previous, exc.headers)
            if 300 <= exc.code < 400:
                return {"state": "REDIRECT_BLOCKED", "source_id": source_id, "url": url,
                        "status": exc.code, "payload_bytes": None,
                        "source_deletion_proven": False, "legal_change_verified": False,
                        "alert_allowed": False}
            return {"state": "HTTP_STATUS_UNRESOLVED", "source_id": source_id, "url": url,
                    "status": exc.code, "payload_bytes": None,
                    "source_deletion_proven": False, "legal_change_verified": False,
                    "alert_allowed": False}
        finally:
            exc.close()
    except (URLError, TimeoutError, OSError) as exc:
        return {"state": "FETCH_FAILED", "source_id": source_id, "url": url,
                "error_type": type(exc).__name__, "payload_bytes": None,
                "source_deletion_proven": False, "legal_change_verified": False,
                "alert_allowed": False}
    try:
        status = getattr(response, "status", None)
        if status is None:
            status = response.getcode()
        if status == 304:
            return _not_modified(source_id, url, previous, response.headers)
        if 300 <= status < 400:
            return {"state": "REDIRECT_BLOCKED", "source_id": source_id, "url": url,
                    "status": status, "payload_bytes": None,
                    "source_deletion_proven": False, "legal_change_verified": False,
                    "alert_allowed": False}
        if status != 200:
            return {"state": "HTTP_STATUS_UNRESOLVED", "source_id": source_id, "url": url,
                    "status": status, "payload_bytes": None,
                    "source_deletion_proven": False, "legal_change_verified": False,
                    "alert_allowed": False}
        final_url = response.geturl() if hasattr(response, "geturl") else url
        if final_url != url:
            return {"state": "REDIRECT_BLOCKED", "source_id": source_id, "url": url,
                    "final_url": final_url, "status": status, "payload_bytes": None,
                    "source_deletion_proven": False, "legal_change_verified": False,
                    "alert_allowed": False}
        rh = response.headers
        content_type = (_header(rh, "Content-Type") or "").split(";", 1)[0].strip().lower()
        declared = _header(rh, "Content-Length")
        declared_length = None
        if declared is not None:
            try:
                declared_length = int(declared)
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid Content-Length") from exc
            if declared_length < 0 or declared_length > max_bytes:
                raise ValueError("Content-Length exceeds configured maximum")
        chunks = []
        total = 0
        while True:
            part = response.read(min(65536, max_bytes - total + 1))
            if not part:
                break
            total += len(part)
            if total > max_bytes:
                raise ValueError("response body exceeds configured maximum")
            chunks.append(part)
        payload = b"".join(chunks)
        if not payload:
            raise ValueError("empty response body")
        if declared_length is not None and declared_length != len(payload):
            raise ValueError("Content-Length does not match received bytes")
        snapshot = intake(source_id=source_id, url=url, observed_utc=observed_utc,
                          payload=payload, content_type=content_type)
        result = {
            "state": "HTTP_200_OBSERVED", "source_id": source_id, "url": url, "status": 200,
            "sha256": snapshot["sha256"], "byte_length": snapshot["byte_length"],
            "content_type": content_type, "etag": _safe_header(_header(rh, "ETag"), "ETag"),
            "last_modified": _safe_header(_header(rh, "Last-Modified"), "Last-Modified"),
            "server_date": _safe_header(_header(rh, "Date"), "Date"),
            "received_utc": observed_utc, "payload_bytes": payload,
            "original_authority_verified": False, "legal_change_verified": False,
            "source_deletion_proven": False, "alert_allowed": False
        }
        if previous is not None:
            result["comparison"] = compare_observations(previous, result)
        return result
    finally:
        try:
            response.close()
        except Exception:
            pass

def compare_observations(old, new):
    """Hash-first comparison. ETag/Last-Modified are validators, not content identity."""
    if not isinstance(old, dict) or not isinstance(new, dict):
        raise ValueError("two observations required")
    if old.get("source_id") != new.get("source_id"):
        raise ValueError("source IDs differ")
    if new.get("state") == "NOT_MODIFIED":
        return {"state": "HTTP_NOT_MODIFIED", "bytes_changed": False,
                "metadata_only_change": False, "legal_change_verified": False,
                "alert_allowed": False}
    if new.get("state") != "HTTP_200_OBSERVED":
        return {"state": "SOURCE_NOT_OBSERVED", "deletion_proven": False,
                "search_false_negative": "OPEN", "legal_change_verified": False,
                "alert_allowed": False}
    same_bytes = old.get("sha256") == new.get("sha256")
    same_url = old.get("url") == new.get("url")
    if same_bytes:
        return {"state": "BYTE_IDENTICAL" if same_url else "BYTE_IDENTICAL_AT_CHANGED_URL",
                "bytes_changed": False, "url_changed": not same_url,
                "metadata_only_change": old.get("etag") != new.get("etag") or old.get("last_modified") != new.get("last_modified"),
                "legal_change_verified": False, "alert_allowed": False}
    return {"state": "SAME_URL_BYTES_CHANGED_CANDIDATE" if same_url else "URL_AND_BYTES_CHANGED_CANDIDATE",
            "bytes_changed": True, "url_changed": not same_url,
            "metadata_only_change": False, "logical_relation": "UNRESOLVED",
            "legal_change_verified": False, "requires_human_review": True,
            "alert_allowed": False}
