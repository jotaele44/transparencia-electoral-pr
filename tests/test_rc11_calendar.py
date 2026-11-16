import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CalendarGate(unittest.TestCase):
 def test_calendar_disagreement_historically_preserved(self):
  x=json.loads((ROOT/'evidence/rc11_2028_calendar_status.json').read_text())
  self.assertEqual(x['disposition']['state'],'RESOLVED_BY_CEE_RS_26_010')
  self.assertEqual(x['disposition']['prior_state'],'REFERRED_TO_CEE_PRESIDENCY_FOR_RESOLUTION')
  self.assertEqual(x['disposition']['final_presidential_determination'],'CEE-RS-26-010, signed 2026-09-08')
  self.assertIsNone(x['disposition']['primary_source_bytes_sha256'])
  self.assertIsNone(x['byte_sha256'])
  self.assertEqual(x['classification'],'HISTORICAL_DISAGREEMENT_SUPERSEDED_BY_SIGNED_RESOLUTION')
 def test_multiple_scenarios_preserved(self):
  x=json.loads((ROOT/'evidence/rc11_2028_calendar_status.json').read_text())
  self.assertEqual({v['mail_ballot_transmission_date'] for v in x['date_positions'] if 'mail_ballot_transmission_date' in v},{'2028-09-27'})
  self.assertIn('2028-09-20',str(x['date_positions']))
  self.assertIn('2028-09-23',str(x['date_positions']))
if __name__=='__main__':unittest.main()
