import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs' / 'battery_coordinate_audit_20261013'
OUT.mkdir(parents=True, exist_ok=True)

def ocv(s):
    return 322.397 + 1.29836*s - 0.0184756*s*s + 0.000143235*s**3

def resistance(s):
    return 0.0806969 - 0.000281326*s + 0.00000166726*s*s

rows = []
for test in ('61905060', '61905061'):
    base = ROOT / 'independent_tests_20261013' / ('ANL' + test)
    meta = json.loads((base / 'checkpoint.json').read_text())
    with (base / 'reference_native.csv').open() as f:
        first = next(csv.DictReader(f))
    s = meta['initial_SOC_model_percent']
    actual = float(first['meter_voltage_V'])
    current = float(first['meter_current_A_discharge_positive'])
    predicted = ocv(s) - resistance(s)*current
    rows.append(dict(test=test, model_initial_soc_percent=s,
        displayed_soc_percent=float(first['displayed_SOC_percent']),
        hpcm2_soc_percent=float(first['HPCM2_SOC_percent']),
        first_voltage_V=actual, first_current_A=current,
        static_voltage_at_model_soc_V=predicted,
        first_voltage_residual_V=predicted-actual,
        static_voltage_at_displayed_soc_V=ocv(float(first['displayed_SOC_percent']))-resistance(float(first['displayed_SOC_percent']))*current,
        static_voltage_at_hpcm2_soc_V=ocv(float(first['HPCM2_SOC_percent']))-resistance(float(first['HPCM2_SOC_percent']))*current))

with (OUT / 'initial_coordinate_comparison.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

with (OUT / 'rest_bias_soc_equivalent.csv').open('w', newline='') as f:
    w=csv.writer(f); w.writerow(['test','start_s','end_s','model_SOC_percent','model_minus_measured_V','local_dOCV_dSOC_V_per_percent','equivalent_SOC_points_local_only'])
    for test in ('61905060', '61905061'):
        path=ROOT/'runs'/('ANL'+test+'_20261013')/'battery_rest_diagnosis'/'diagnosis.json'
        diag=json.loads(path.read_text())
        for seg in diag['rest_intervals']:
            if not seg.get('model_SOC_first_last_percent'): continue
            s=sum(seg['model_SOC_first_last_percent'])/2
            slope=(ocv(s+0.01)-ocv(s-0.01))/0.02
            w.writerow([test,seg['start_s'],seg['end_s'],s,seg['voltage_bias_V'],slope,seg['voltage_bias_V']/slope])
