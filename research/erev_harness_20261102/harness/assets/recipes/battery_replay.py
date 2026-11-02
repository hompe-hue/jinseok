"""Prescribed-current diagnostic of public Rint model; no parameter fitting or AVL runs."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / 'inputs'
if not SRC.exists():
    SRC = ROOT.parent / 'feedback/research/public_validation_batch_20261016/actual_20261016'

def sig(d, name):
    c = [c for c in d if c.startswith('In/' + name + ' (')]
    assert len(c) == 1
    return d[c[0]].to_numpy(float)

def replay(t, i, s0):
    # dSOC[%] = -I[A]dt[s] *100/(180[Ah]*3600).
    s = s0 - cumulative_trapezoid(i, t, initial=0) / 6480
    assert np.all((s >= 0) & (s <= 100))
    grid = np.arange(101.)
    ocv = 322.397 + 1.29836*grid - .0184756*grid**2 + .000143235*grid**3
    resistance = .0806969 - .000281326*grid + .00000166726*grid**2
    # Replicate 1%-SOC tabulation/linear interpolation of archived public input.
    return s, np.interp(s, grid, ocv) - np.interp(s, grid, resistance)*i

def main():
    rows, files = [], {}
    for code in ['058', '059', '060', '066']:
        bp = SRC/code/('battery_PUBLIC_'+code+'.csv')
        rp = SRC/'references'/('ANL61905'+code+'_reference_native.csv')
        for f in [bp, rp]:
            files[str(f.relative_to(SRC))] = hashlib.sha256(f.read_bytes()).hexdigest()
        b = pd.read_csv(bp, skiprows=[1]); ref = pd.read_csv(rp)
        t = b.Time.to_numpy(float); rt = ref.iloc[:, 0].to_numpy(float)
        assert t[0] == rt[0] == 0 and np.all(np.diff(rt) > 0)
        s0 = sig(b, 'SoC')[0]
        s, v = replay(t, -sig(b, 'Current'), s0)
        sr, vr = replay(rt, ref.meter_current_A_discharge_positive.to_numpy(float), s0)
        m = (t > 20) & (t <= t[-1])
        meas = np.interp(t, rt, ref.meter_voltage_V)
        actual_current_v = np.interp(t, rt, vr)
        model_u = sig(b, 'Voltage')
        rmse = lambda a: float(np.sqrt(np.mean(a[m]**2)))
        row = dict(test='61905'+code, evaluation_end_s=float(t[-1]),
            initial_model_SOC_percent=float(s0),
            model_current_SOC_reconstruction_max_abs_percentage_points=float(np.max(abs(s-sig(b, 'SoC')))),
            model_current_voltage_reconstruction_RMSE_V=rmse(v-model_u),
            original_model_vs_measurement_voltage_RMSE_V=rmse(model_u-meas),
            measured_current_replay_voltage_RMSE_V=rmse(actual_current_v-meas),
            measured_current_replay_voltage_bias_V=float(np.mean((actual_current_v-meas)[m])),
            measured_current_replay_final_model_SOC_percent=float(np.interp(t[-1], rt, sr)),
            original_final_model_SOC_percent=float(sig(b, 'SoC')[-1]))
        # Reproducing serialized model on exported I checks implementation and signs.
        # 1s exports omit internal solver samples, hence numerical tolerance.
        assert row['model_current_voltage_reconstruction_RMSE_V'] < .01
        assert row['model_current_SOC_reconstruction_max_abs_percentage_points'] < .02
        rows.append(row)
    pd.DataFrame(rows).to_csv(HERE/'replay_metrics.csv', index=False)
    (HERE/'QA.json').write_text(json.dumps(dict(public_capacity_Ah=180,
        unchanged_initial_SOC=True, OCV_R_parameters_fitted=False,
        model_current_reconstruction_pass=True, new_CRUISE_runs=0,
        independent_validation=False, true_battery_SOC_measured=False,
        temperature_model_identified=False, source_hashes=files), indent=2)+'\n')
    print(pd.DataFrame(rows).to_string(index=False))

if __name__ == '__main__':
    main()
