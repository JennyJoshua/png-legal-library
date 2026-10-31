import json
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from portal_api import search_request,health_response

class PortalApiTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.index=Path(self.temp.name)/"index.json"
  self.record={"node_id":"x","document_id":"act-1","version_id":"1234567890abcdef","document_title":"Test PNG Act","source_checksum_sha256":"a"*64,"source_reference":"PDF page 4","structure_path":[{"kind":"section","number":"2"}],"page_number":4,"text":"A court may issue an order.","number":"2","kind":"section","source_url":"https://example.gov.pg/act"}
  self.index.write_text(json.dumps({"records":[self.record]}),encoding="utf-8")
 def tearDown(self):self.temp.cleanup()
 def test_search_returns_traceable_result(self):
  result=search_request({"query":"court order"},self.index)
  self.assertEqual(result["result_count"],1);self.assertEqual(result["results"][0]["document_id"],"act-1")
 def test_any_match_supported(self):
  result=search_request({"query":"court absent","match":"any"},self.index)
  self.assertEqual(result["result_count"],1)
 def test_empty_query_rejected(self):
  with self.assertRaisesRegex(ValueError,"Enter a search term"):search_request({"query":" "},self.index)
 def test_non_object_rejected(self):
  with self.assertRaisesRegex(ValueError,"JSON object"):search_request([],self.index)
 def test_invalid_match_rejected(self):
  with self.assertRaisesRegex(ValueError,"Match must"):search_request({"query":"court","match":"maybe"},self.index)
 def test_invalid_limit_rejected(self):
  for limit in (0,51,True,"5"):
   with self.subTest(limit=limit):
    with self.assertRaisesRegex(ValueError,"Result limit"):search_request({"query":"court","limit":limit},self.index)
 def test_health_missing_index(self):
  result=health_response(self.index.parent/"missing.json")
  self.assertEqual(result["status"],"index_missing")
if __name__=="__main__":unittest.main()
