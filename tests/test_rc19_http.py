import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc19_http import fetch_publication, compare_observations

class Headers(dict):
    def get(self,k,d=None): return super().get(k,d)

class Response:
    def __init__(self,body=b"%PDF-1.4 test",status=200,headers=None,url=None):
        self.body=body; self.status=status
        self.headers=Headers(headers or {"Content-Type":"application/pdf","Content-Length":str(len(body)),"ETag":'"v1"',"Last-Modified":"Tue, 17 Nov 2026 08:00:00 GMT"})
        self.closed=False; self.url=url
    def read(self,n=-1):
        v=self.body[:n]; self.body=self.body[n:]; return v
    def close(self): self.closed=True
    def geturl(self): return self.url or URL

class Opener:
    def __init__(self,response): self.response=response; self.request=None; self.timeout=None
    def open(self,request,timeout): self.request=request; self.timeout=timeout; return self.response

URL="https://www.ceepur.org/test.pdf"
HOSTS={"www.ceepur.org"}
TIME="2026-11-17T08:09:00Z"

def fetch(body=b"%PDF-1.4 test",headers=None,previous=None,status=200,max_bytes=1000,url=URL):
    response=Response(body,status,headers,url=url)
    op=Opener(response)
    result=fetch_publication(source_id="cee_test",url=url,observed_utc=TIME,allowed_hosts=HOSTS,
                             previous=previous,opener=op,max_bytes=max_bytes)
    return result,op,response

class RC19HTTP(unittest.TestCase):
    def test_fetch_hash_and_bytes(self):
        r,_,resp=fetch()
        self.assertEqual(r["state"],"HTTP_200_OBSERVED")
        self.assertEqual(r["payload_bytes"],b"%PDF-1.4 test")
        self.assertEqual(len(r["sha256"]),64)
        self.assertTrue(resp.closed)

    def test_sends_etag_and_last_modified_conditionals(self):
        prev={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":12,
              "etag":'"old"',"last_modified":"Mon, 16 Nov 2026 08:00:00 GMT"}
        _,op,_=fetch(previous=prev)
        self.assertEqual(op.request.get_header("If-none-match"),'"old"')
        self.assertEqual(op.request.get_header("If-modified-since"),"Mon, 16 Nov 2026 08:00:00 GMT")

    def test_etag_change_same_bytes_is_metadata_only(self):
        old={"source_id":"cee_test","url":URL,"sha256":"a"*64,"etag":'"v1"',"last_modified":"Mon"}
        new={"source_id":"cee_test","url":URL,"sha256":"a"*64,"etag":'"v2"',"last_modified":"Tue","state":"HTTP_200_OBSERVED"}
        c=compare_observations(old,new)
        self.assertEqual(c["state"],"BYTE_IDENTICAL")
        self.assertTrue(c["metadata_only_change"])

    def test_same_url_changed_bytes_is_candidate(self):
        old={"source_id":"cee_test","url":URL,"sha256":"a"*64}
        r,_,_=fetch(body=b"%PDF-1.7 changed",previous=old)
        self.assertEqual(r["comparison"]["state"],"SAME_URL_BYTES_CHANGED_CANDIDATE")
        self.assertFalse(r["alert_allowed"])

    def test_304_requires_exact_url_baseline(self):
        prev={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":12,"etag":'"v1"'}
        r,_,_=fetch(previous=prev,status=304)
        self.assertEqual(r["state"],"NOT_MODIFIED")
        self.assertEqual(r["sha256"],"a"*64)
        r,_,_=fetch(status=304)
        self.assertEqual(r["state"],"NOT_MODIFIED_WITHOUT_BASELINE")
        moved={"source_id":"cee_test","url":"https://www.ceepur.org/old.pdf","sha256":"a"*64}
        r,_,_=fetch(previous=moved,status=304)
        self.assertEqual(r["state"],"NOT_MODIFIED_WITHOUT_BASELINE")

    def test_redirect_never_followed(self):
        r,_,_=fetch(status=302)
        self.assertEqual(r["state"],"REDIRECT_BLOCKED")

    def test_response_url_change_is_blocked(self):
        r,_,_=fetch(url=URL)
        self.assertEqual(r["state"],"HTTP_200_OBSERVED")
        r,_,_=fetch(url=URL)
        self.assertEqual(r["state"],"HTTP_200_OBSERVED")
        response=Response(url="https://evil.example/redirected")
        op=Opener(response)
        r=fetch_publication(source_id="cee_test",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,opener=op)
        self.assertEqual(r["state"],"REDIRECT_BLOCKED")

    def test_404_not_deletion(self):
        r,_,_=fetch(status=404)
        self.assertEqual(r["state"],"HTTP_STATUS_UNRESOLVED")
        self.assertFalse(r["source_deletion_proven"])

    def test_oversize_content_length_rejected(self):
        op=Opener(Response(b"%PDF-a",headers={"Content-Type":"application/pdf","Content-Length":"99999999"}))
        with self.assertRaises(ValueError):
            fetch_publication(source_id="x",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,max_bytes=100,opener=op)

    def test_oversize_stream_rejected(self):
        with self.assertRaises(ValueError):
            fetch(body=b"%PDF-"+b"x"*100,max_bytes=50)

    def test_declared_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            fetch(body=b"%PDF-abc",headers={"Content-Type":"application/pdf","Content-Length":"3"})

    def test_invalid_pdf_signature_rejected(self):
        with self.assertRaises(ValueError):
            fetch(body=b"<html>not pdf</html>")

    def test_non_allowlisted_host_rejected(self):
        with self.assertRaises(PermissionError):
            fetch_publication(source_id="x",url="https://evil.example/x",observed_utc=TIME,allowed_hosts=HOSTS,opener=Opener(Response()))

    def test_http_url_rejected(self):
        with self.assertRaises(ValueError):
            fetch_publication(source_id="x",url="http://www.ceepur.org/x",observed_utc=TIME,allowed_hosts=HOSTS,opener=Opener(Response()))

    def test_credentials_and_ip_literal_rejected(self):
        for url in ("https://u:p@www.ceepur.org/x","https://127.0.0.1/x"):
            with self.assertRaises((ValueError,PermissionError)):
                fetch_publication(source_id="x",url=url,observed_utc=TIME,allowed_hosts=HOSTS,opener=Opener(Response()))

    def test_invalid_timeout_and_size_rejected(self):
        for kwargs in ({"timeout":31},{"max_bytes":0},{"max_bytes":40000001}):
            with self.assertRaises(ValueError):
                fetch_publication(source_id="x",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,opener=Opener(Response()),**kwargs)

    def test_not_modified_without_baseline_has_no_hash(self):
        r,_,_=fetch(status=304)
        self.assertIsNone(r["sha256"])

    def test_non200_does_not_mark_source_deleted(self):
        r,_,_=fetch(status=500)
        self.assertFalse(r["source_deletion_proven"])

    def test_moved_source_keeps_old_and_new_url_distinct(self):
        old={"source_id":"cee_test","url":"https://www.ceepur.org/old.pdf","sha256":"a"*64}
        r,_,_=fetch(body=b"%PDF-new",previous=old)
        self.assertEqual(r["comparison"]["state"],"URL_AND_BYTES_CHANGED_CANDIDATE")

    def test_http_error_304_uses_exact_previous_hash(self):
        headers=Headers({"ETag":'"v1"'})
        err=HTTPError(URL,304,"Not Modified",headers,None)
        op=RaisingOpener(err)
        previous={"source_id":"cee_test","url":URL,"sha256":"b"*64,"byte_length":20}
        r=fetch_publication(source_id="cee_test",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,previous=previous,opener=op)
        self.assertEqual(r["state"],"NOT_MODIFIED")
        self.assertEqual(r["sha256"],"b"*64)

    def test_http_error_redirect_is_blocked(self):
        err=HTTPError(URL,302,"Found",Headers({"Location":"https://evil.example/"}),None)
        r=fetch_publication(source_id="cee_test",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,opener=RaisingOpener(err))
        self.assertEqual(r["state"],"REDIRECT_BLOCKED")

    def test_http_error_404_is_not_deletion(self):
        err=HTTPError(URL,404,"Not Found",Headers(),None)
        r=fetch_publication(source_id="cee_test",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,opener=RaisingOpener(err))
        self.assertEqual(r["state"],"HTTP_STATUS_UNRESOLVED")
        self.assertFalse(r["source_deletion_proven"])

    def test_network_error_is_open_not_deletion(self):
        r=fetch_publication(source_id="cee_test",url=URL,observed_utc=TIME,allowed_hosts=HOSTS,opener=RaisingOpener(URLError("offline")))
        self.assertEqual(r["state"],"FETCH_FAILED")
        self.assertFalse(r["source_deletion_proven"])

    def test_etag_header_injection_rejected(self):
        previous={"source_id":"cee_test","url":URL,"sha256":"a"*64,"etag":'"ok"\\r\\nX-Evil: yes'}
        with self.assertRaises(ValueError):
            fetch(previous=previous)

if __name__=="__main__": unittest.main()
