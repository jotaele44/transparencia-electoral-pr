import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from export_dry_run import generate

class PinnedHubContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binding=json.loads((ROOT/"contracts/hub_binding_rc4.json").read_text())
        cls.manifest=json.loads((ROOT/"federation.json").read_text())
    def test_required_repo_fields(self):
        self.assertTrue(set(self.binding["hub_federation_manifest_required"])<=self.manifest.keys())
        self.assertEqual(self.manifest["hub_parent"],"thehub-pr")
    def test_synthetic_export_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            m=generate([{"id":"mock","synthetic":True}],tmp)
            self.assertTrue(set(self.binding["hub_export_manifest_required"])<=m.keys())
            self.assertEqual(m["producer"],self.manifest["program_id"])
    def test_no_implied_consumer_certification(self):
        self.assertEqual(self.binding["validated_consumers"],[])
        self.assertFalse(self.binding["live_federation_enabled"])
        self.assertEqual(self.binding["certification"],"OPEN")
        self.assertFalse(self.manifest["federation_readiness_gate"]["ready_for_hub_live_execution"])
    def test_exact_hub_schema_binding_shapes(self):
        for key in ("hub_commit","hub_federation_manifest_blob_sha","hub_export_manifest_blob_sha"):
            value=self.binding[key]
            self.assertEqual(len(value),40)
            self.assertTrue(all(ch in "0123456789abcdef" for ch in value))
if __name__=="__main__": unittest.main()
