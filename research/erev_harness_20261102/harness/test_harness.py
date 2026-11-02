"""Regression and failure-path checks; fixtures are historical, not new CRUISE runs."""
from pathlib import Path
import csv,json,shutil,tempfile,unittest
from research import Harness,InvalidRun,HARNESS_DIR,log_review

class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='harness_test_')
        cls.root=Path(cls.temp.name)/'kit'
        shutil.copytree(HARNESS_DIR,cls.root,ignore=shutil.ignore_patterns('reports','__pycache__','.git'))
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        self.h=Harness(self.root)
        self.indices={p:p.read_bytes() for p in (self.root/'runs').glob('*/index.json')}
        idx=self.h.index('R0_BASE')
        self.manifest=json.loads((self.root/'runs/R0_BASE/attempts'/idx['attempt']/'manifest.json').read_text())
        self.files={k:self.root/self.manifest['assets'][k]['path'] for k in ['battery','velocity','generator']}
        self.work=Path(tempfile.mkdtemp(dir=self.root))
    def tearDown(self):
        for p,data in self.indices.items():p.write_bytes(data)
        shutil.rmtree(self.work)
    def altered_battery(self,mutator):
        p=self.work/'battery.csv'
        with self.files['battery'].open(newline='') as f:rows=list(csv.reader(f))
        mutator(rows)
        with p.open('w',newline='') as f:csv.writer(f).writerows(rows)
        return dict(self.files,battery=p)
    def test_regression_three_sensitivities(self):
        values=[x['central_delta_kWh_at_10percent'] for x in self.h.sensitivities()]
        expected=[.9310404996492228,.03458233969077096,.011427880513878996]
        self.assertEqual(len(values),3)
        for x,y in zip(values,expected):self.assertAlmostEqual(x,y,places=10)
    def test_accuracy_failure_not_promoted_to_adopted_model(self):
        r=self.h.latest('R0_BASE')
        self.assertEqual(r['data_status'],'VALIDATED_EXPORT')
        self.assertFalse(r['model_accuracy_targets_met'])
        self.assertFalse(r['automatic_parameter_adoption'])
        self.assertTrue(r['user_confirmed_unmodified'])
    def test_duplicate_upload_keeps_same_receipt(self):
        old=self.h.index('R0_BASE')['attempt']
        key=self.h.ingest('R0_BASE',self.files,confirmed=True)
        self.assertEqual(old,key)
    def test_truncated_export_rejected(self):
        files=self.altered_battery(lambda rows:rows.__delitem__(slice(-3,None)))
        self.h.ingest('R0_BASE',files)
        self.assertEqual(self.h.review('R0_BASE')['data_status'],'INVALID_EXPORT')
    def test_wrong_case_initial_SOC_rejected(self):
        self.h.ingest('PUBLIC_058',self.files)
        r=self.h.review('PUBLIC_058')
        self.assertEqual(r['data_status'],'INVALID_EXPORT')
        self.assertIn('Initial SOC',r['failure_reason'])
    def test_wrong_voltage_units_rejected(self):
        def mutate(rows):rows[1][rows[0].index('In/Voltage (BMS Monitor)')]='mV'
        self.h.ingest('R0_BASE',self.altered_battery(mutate))
        r=self.h.review('R0_BASE')
        self.assertEqual(r['data_status'],'INVALID_EXPORT')
        self.assertIn('Unit mismatch',r['failure_reason'])
    def test_coarse_export_cannot_become_dense_result(self):
        idx=self.h.index('PUBLIC_066')
        manifest=json.loads((self.root/'runs/PUBLIC_066/attempts'/idx['attempt']/'manifest.json').read_text())
        files={k:self.root/manifest['assets'][k]['path'] for k in ['battery','velocity','generator']}
        self.h.ingest('SMCT_DENSE_SAVED10',files)
        r=self.h.review('SMCT_DENSE_SAVED10')
        self.assertEqual(r['data_status'],'INVALID_EXPORT')
        self.assertIn('resolution',r['failure_reason'])
        # Test-only run must not leak into subsequent status assertions.
        shutil.rmtree(self.root/'runs/SMCT_DENSE_SAVED10')
    def test_expected_auxiliary_is_enforced(self):
        self.h.ingest('R3_AUX_M10',self.files)
        r=self.h.review('R3_AUX_M10')
        self.assertEqual(r['data_status'],'VALIDATED_EXPORT')
        self.assertFalse(r['protocol_checks']['auxiliary_matches'])
        self.assertFalse(r['numerical_comparison_usable'])
    def test_changed_baseline_not_used_for_sensitivity_pairs(self):
        def mutate(rows):
            col=rows[0].index('In/Current (BMS Monitor)')
            for row in rows[2:]:row[col]=str(float(row[col])*1.02)
        self.h.ingest('R0_BASE',self.altered_battery(mutate))
        r=self.h.review('R0_BASE')
        self.assertEqual(r['data_status'],'VALIDATED_EXPORT')
        self.assertFalse(r['protocol_checks']['baseline_energy_reproduced'])
        self.assertEqual(self.h.sensitivities(),[])
    def test_prepared_run_stays_pending_without_actual_exports(self):
        self.assertIsNone(self.h.latest('SMCT_DENSE_SAVED10'))
        self.assertEqual(self.h.next_action()['state'],'AWAITING_MANUAL_CRUISE_RUN')
    def test_successful_series_write_does_not_hide_fatal_failure(self):
        p=self.work/'solver.log'
        p.write_text('[message][simulation] Simulation ended.\nSeries result writing successful.\n[fatal error][simulation] Result writing failed.')
        result=log_review(p)
        self.assertEqual(result['status'],'REPORTED_FAILURE')
        self.assertFalse(result['final_success_verified'])
    def test_input_tampering_is_detected_before_cached_review(self):
        p=self.files['battery'];old=p.read_bytes()
        try:
            p.write_bytes(old+b'\n')
            with self.assertRaises(InvalidRun):self.h.review('R0_BASE')
        finally:p.write_bytes(old)
    def test_reference_tampering_is_detected(self):
        p=self.root/self.h.registry['runs']['R0_BASE']['reference'];old=p.read_bytes()
        try:
            p.write_bytes(old+b'\n')
            with self.assertRaises(InvalidRun):self.h.sensitivities()
        finally:p.write_bytes(old)
    def test_review_tampering_is_detected(self):
        p=self.root/self.h.index('R0_BASE')['review'];old=p.read_bytes()
        try:
            p.write_bytes(old+b'\n')
            with self.assertRaises(InvalidRun):self.h.latest('R0_BASE')
        finally:p.write_bytes(old)

if __name__=='__main__':unittest.main(verbosity=2)
