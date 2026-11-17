import sys,unittest
from io import BytesIO
from urllib.error import HTTPError
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc19_http import fetch_read_only,_RejectRedirects

URL="https://www.ceepur.org/example.pdf"
T="2026-11-17T20:00:00Z"
SOURCE={"source_id":"cee_test","url":URL,"allowed_hosts":["www.ceepur.org"],"allowed_content_types":["application/pdf"],"max_bytes":1000,"timeout_seconds":5}

class FakeResponse:
 def __init__(self,status=200,headers=None,body=b"%PDF-1.7 test",url=URL):
  self.status=status;self.headers=headers or {"Content-Type":"application/pdf","Content-Length":str(len(body)),"ETag":"\"v1\"","Last-Modified":"Tue, 17 Nov 2026 20:00:00 GMT"}
  self.body=body;self.url=url;self.closed=False
 def getcode(self):return self.status
 def geturl(self):return self.url
 def read(self,n=-1):return self.body[:n]
 def close(self):self.closed=True

class FakeOpener:
 def __init__(self,response=None,error=None):self.response=response;self.error=error;self.request=None;self.timeout=None
 def open(self,request,timeout=None):
  self.request=request;self.timeout=timeout
  if self.error:raise self.error
  return self.response

class RC19HTTP(unittest.TestCase):
 def test_valid_pdf_capture_hashes_exact_body(self):
  r=FakeResponse();o=FakeOpener(r);x=fetch_read_only(SOURCE,observed_utc=T,opener=o)
  import hashlib
  self.assertEqual(x["sha256"],hashlib.sha256(r.body).hexdigest())
  self.assertEqual(x["state"],"FIRST_OBSERVATION");self.assertEqual(x["payload"],r.body)
  self.assertTrue(r.closed)
 def test_get_only_no_credentials_or_cookies(self):
  o=FakeOpener(FakeResponse());fetch_read_only(SOURCE,observed_utc=T,opener=o)
  self.assertEqual(o.request.get_method(),"GET")
  self.assertIsNone(o.request.get_header("Authorization"))
  self.assertIsNone(o.request.get_header("Cookie"))
 def test_conditional_etag_and_last_modified(self):
  p={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":10,"etag":"\"v0\"","last_modified":"Mon, 16 Nov 2026 20:00:00 GMT"}
  o=FakeOpener(FakeResponse());fetch_read_only(SOURCE,observed_utc=T,previous=p,opener=o)
  self.assertEqual(o.request.get_header("If-none-match"),"\"v0\"")
  self.assertEqual(o.request.get_header("If-modified-since"),"Mon, 16 Nov 2026 20:00:00 GMT")
 def test_304_is_not_byte_identity(self):
  from email.message import Message
  h=Message();h["ETag"]='"v0"'
  err=HTTPError(URL,304,"Not Modified",h,BytesIO(b""))
  p={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":10,"etag":'"v0"'}
  x=fetch_read_only(SOURCE,observed_utc=T,previous=p,opener=FakeOpener(error=err))
  self.assertEqual(x["state"],"HTTP_NOT_MODIFIED")
  self.assertEqual(x["byte_identity"],"NOT_REVALIDATED_BYTES")
  self.assertIsNone(x["payload"])
 def test_304_without_prior_validator_fails(self):
  from email.message import Message
  h=Message();err=HTTPError(URL,304,"Not Modified",h,BytesIO(b""))
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(error=err))
 def test_same_url_new_bytes_detected_even_same_etag(self):
  p={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":10,"etag":'"v1"'}
  r=FakeResponse(body=b"%PDF-1.7 changed",headers={"Content-Type":"application/pdf","Content-Length":"16","ETag":'"v1"'})
  x=fetch_read_only(SOURCE,observed_utc=T,previous=p,opener=FakeOpener(r))
  self.assertEqual(x["state"],"SAME_URL_BYTES_CHANGED")
 def test_identical_bytes_stay_identical_with_new_etag(self):
  body=b"%PDF-1.7 test";p={"source_id":"cee_test","url":URL,"sha256":__import__("hashlib").sha256(body).hexdigest(),"byte_length":len(body),"etag":'"old"'}
  r=FakeResponse(body=body,headers={"Content-Type":"application/pdf","Content-Length":str(len(body)),"ETag":'"new"'})
  x=fetch_read_only(SOURCE,observed_utc=T,previous=p,opener=FakeOpener(r))
  self.assertEqual(x["state"],"BYTE_IDENTICAL")
 def test_url_change_kept_as_candidate(self):
  p={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":10}
  s={**SOURCE,"url":"https://www.ceepur.org/revised.pdf"}
  r=FakeResponse(url=s["url"])
  x=fetch_read_only(s,observed_utc=T,previous=p,opener=FakeOpener(r))
  self.assertEqual(x["state"],"URL_AND_BYTES_CHANGED")
 def test_unapproved_host_fails(self):
  s={**SOURCE,"url":"https://evil.example/a.pdf","allowed_hosts":["evil.example"]}
  with self.assertRaises(ValueError):fetch_read_only(s,observed_utc=T,opener=FakeOpener(FakeResponse()))
 def test_http_scheme_fails(self):
  s={**SOURCE,"url":"http://www.ceepur.org/a.pdf"}
  with self.assertRaises(ValueError):fetch_read_only(s,observed_utc=T,opener=FakeOpener(FakeResponse()))
 def test_nondefault_port_fails(self):
  s={**SOURCE,"url":"https://www.ceepur.org:444/a.pdf"}
  with self.assertRaises(ValueError):fetch_read_only(s,observed_utc=T,opener=FakeOpener(FakeResponse()))
 def test_redirect_status_fails_closed(self):
  r=FakeResponse(status=302,headers={"Location":"https://evil.example/","Content-Type":"application/pdf"})
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(r))
 def test_redirect_handler_never_follows(self):
  self.assertIsNone(_RejectRedirects().redirect_request(None,None,302,"Found",{},"https://evil.example"))
 def test_wrong_content_type_fails(self):
  r=FakeResponse(headers={"Content-Type":"text/html","Content-Length":"13"})
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(r))
 def test_pdf_signature_mismatch_fails(self):
  r=FakeResponse(body=b"not a pdf",headers={"Content-Type":"application/pdf","Content-Length":"9"})
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(r))
 def test_compressed_response_fails(self):
  r=FakeResponse(headers={"Content-Type":"application/pdf","Content-Length":"13","Content-Encoding":"gzip"})
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(r))
 def test_content_length_limit_fails_before_read(self):
  r=FakeResponse(headers={"Content-Type":"application/pdf","Content-Length":"1001"})
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(r))
 def test_stream_limit_fails(self):
  r=FakeResponse(body=b"x"*1001,headers={"Content-Type":"text/plain"})
  s={**SOURCE,"allowed_content_types":["text/plain"]}
  with self.assertRaises(ValueError):fetch_read_only(s,observed_utc=T,opener=FakeOpener(r))
 def test_content_length_mismatch_fails(self):
  r=FakeResponse(body=b"%PDF-1.7",headers={"Content-Type":"application/pdf","Content-Length":"999"})
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,opener=FakeOpener(r))
 def test_validator_header_injection_fails(self):
  p={"source_id":"cee_test","url":URL,"sha256":"a"*64,"byte_length":10,"etag":"v1\r\nAuthorization: bad"}
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,previous=p,opener=FakeOpener(FakeResponse()))
 def test_capture_timestamp_strict(self):
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc="2026-11-17T20:00:00-04:00",opener=FakeOpener(FakeResponse()))
 def test_source_identity_mismatch_fails(self):
  p={"source_id":"other","url":URL,"sha256":"a"*64,"byte_length":10,"etag":"v1"}
  with self.assertRaises(ValueError):fetch_read_only(SOURCE,observed_utc=T,previous=p,opener=FakeOpener(FakeResponse()))

if __name__=="__main__":unittest.main()
