import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from rc8_reporting_units import evaluate,compare
def row(p="001",u="02",c="003"):
    return {"PREKEY":p,"UNIKEY":u,"COLKEY":c,"INSCRITOS":"250","STATUS":"fixture"}
class Units(unittest.TestCase):
    def test_leading_zero_preserved(self):
        x=evaluate([row()],ballot="ESTATAL")
        self.assertEqual(x["keys"],[["001","02","003"]])
        self.assertIsNone(x["official_denominator"])
    def test_no_leading_zero_merge(self):
        x=compare([row("001")],[row("1")],ballot="ESTATAL")
        self.assertEqual((x["intersection"],x["a_only"],x["b_only"],x["union"],x["symmetric_difference"]),(0,1,1,2,2))
    def test_collision_quarantined(self):
        x=evaluate([row(),row()],ballot="ESTATAL")
        self.assertEqual(x["keyed_count"],1)
        self.assertEqual(x["unresolved_count"],1)
        self.assertEqual(x["input_count"],2)
    def test_no_missing_key_synthesis(self):
        x=evaluate([{"PREKEY":"001","COLKEY":"003"}],ballot="ESTATAL")
        self.assertEqual(x["unresolved_count"],1)
        self.assertEqual(x["keyed_count"],0)
    def test_join_blocked_on_collision(self):
        x=compare([row(),row()],[row()],ballot="ESTATAL")
        self.assertEqual(x["status"],"BLOCKED_UNRESOLVED_KEYS")
    def test_no_numeric_normalization(self):
        x=evaluate([row(p=1)],ballot="ESTATAL")
        self.assertEqual(x["unresolved_count"],1)
    def test_keyed_unresolved_conservation(self):
        x=evaluate([row(),row(),row("002")],ballot="MUNICIPAL")
        self.assertEqual(x["keyed_count"]+x["unresolved_count"],x["input_count"])
    def test_cross_ballot_unverified(self):
        a=evaluate([row()],ballot="ESTATAL")
        b=evaluate([row()],ballot="LEGISLATIVA")
        self.assertFalse(a["identity_status"]=="VERIFIED")
        self.assertNotEqual(a["ballot"],b["ballot"])
    def test_nulls(self):
        x=evaluate([row(c=None)],ballot="ESTATAL")
        self.assertEqual(x["unresolved_count"],1)
if __name__=="__main__":unittest.main()
