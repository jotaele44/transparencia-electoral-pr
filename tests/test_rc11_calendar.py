import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CalendarGate(unittest.TestCase):
 def test_calendar_disagreement_not_final(self):
  x=json.loads((ROOT/'evidence/rc11_2028_calendar_status.json').read_text())
  self.assertEqual(x['disposition']['state'],'REFERRED_TO_CEE_PRESIDENCY_FOR_RESOLUTION')
  self.assertIsNone(x['byte_sha256'])
  self.assertEqual(x['classification'],'DATE_CONTRADICTION_AND_LEGAL_DEPENDENCY_OPEN')
 def test_multiple_scenarios_preserved(self):
  x=json.loads((ROOT/'evidence/rc11_2028_calendar_status.json').read_text())
  self.assertEqual({v['mail_ballot_transmission_date'] for v in x['date_positions'] if 'mail_ballot_transmission_date' in v},{'2028-09-27'})
  self.assertIn('2028-09-20',str(x['date_positions']))
  self.assertIn('2028-09-23',str(x['date_positions']))
if __name__=='__main__':unittest.main()
