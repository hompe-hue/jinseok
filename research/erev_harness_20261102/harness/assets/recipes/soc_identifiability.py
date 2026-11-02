"""Separate residual signatures; no fitted battery parameters and no new solver runs."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE/'inputs'
if not SRC.exists():
    SRC = ROOT.parent/'feedback/research/public_validation_batch_20261016/actual_20261016'
GRID = np.arange(101.)
U = 322.397 + 1.29836*GRID - .0184756*GRID**2 + .000143235*GRID**3
R = .0806969 - .000281326*GRID + .00000166726*GRID**2

def voltage(q_ah, current, s0, capacity=180., rscale=1., uoffset=0.):
    soc = s0 - 100*q_ah/capacity
    assert np.all((soc >= 0) & (soc <= 100))
    return soc, np.interp(soc, GRID, U)+uoffset-rscale*np.interp(soc, GRID, R)*current

def main():
    summaries, groups, stops, perturbations, conditioning, hashes = [], [], [], [], [], {}
    for code in ['058', '059', '060', '066']:
        test = '61905'+code
        bp = SRC/code/('battery_PUBLIC_'+code+'.csv')
        rp = SRC/'references'/('ANL'+test+'_reference_native.csv')
        for f in [bp, rp]:
            hashes[str(f.relative_to(SRC))] = hashlib.sha256(f.read_bytes()).hexdigest()
        b = pd.read_csv(bp, skiprows=[1]); ref = pd.read_csv(rp)
        s0 = float(b.filter(like='In/SoC (').iloc[0,0]); end = float(b.Time.iloc[-1])
        rt = ref.iloc[:,0].to_numpy(float)
        # 1 s grid is common to archived model evaluation and avoids duration weighting bias.
        t = np.arange(end+1)
        current_native = ref.meter_current_A_discharge_positive.to_numpy(float)
        q_native = cumulative_trapezoid(current_native, rt, initial=0)/3600
        q = np.interp(t, rt, q_native)
        i = np.interp(t, rt, current_native)
        actual = np.interp(t, rt, ref.meter_voltage_V)
        speed = np.interp(t, rt, ref.speed_kmh)
        temp = np.interp(t, rt, ref.battery_temperature_C)
        soc, pred = voltage(q, i, s0)
        residual = pred-actual
        mask = t > 20
        early = mask & (t <= 20+(end-20)/4)
        late = t >= end-(end-20)/4
        summaries.append(dict(test=test, initial_model_SOC_percent=s0, measured_net_Ah_at_end=float(q[-1]),
            replay_final_model_SOC_percent=float(soc[-1]), residual_RMSE_V=float(np.sqrt(np.mean(residual[mask]**2))),
            residual_bias_V=float(np.mean(residual[mask])), early_quarter_bias_V=float(np.mean(residual[early])),
            late_quarter_bias_V=float(np.mean(residual[late])), early_to_late_bias_change_V=float(np.mean(residual[late])-np.mean(residual[early])),
            battery_temperature_min_C=float(temp.min()), battery_temperature_max_C=float(temp.max())))
        for name, pick in [('low_current_abs_lt3A', np.abs(i)<3), ('discharge_gt20A', i>20), ('charge_lt_minus20A', i<-20)]:
            m = mask & pick
            groups.append(dict(test=test, group=name, samples=int(m.sum()),
                residual_bias_V=float(np.mean(residual[m])) if m.any() else None,
                residual_median_V=float(np.median(residual[m])) if m.any() else None,
                residual_RMSE_V=float(np.sqrt(np.mean(residual[m]**2))) if m.any() else None))
        # Diagnostic stopped/low-current windows: these are NOT equilibrium OCV tests.
        good = mask & (np.abs(i)<3) & (np.abs(speed)<.5)
        starts = np.flatnonzero(good & ~np.r_[False,good[:-1]])
        ends = np.flatnonzero(good & ~np.r_[good[1:],False])
        for start, last in zip(starts, ends):
            if t[last]-t[start] < 10:
                continue
            m = (t >= max(t[start],t[last]-3)) & (t<=t[last])
            apparent_ocv = actual[m]+i[m]*np.interp(soc[m],GRID,R)
            in_range = (apparent_ocv>=U[0]) & (apparent_ocv<=U[-1])
            apparent_soc = np.interp(apparent_ocv[in_range],U,GRID)
            stops.append(dict(test=test, start_s=float(t[start]), end_s=float(t[last]), duration_s=float(t[last]-t[start]),
                tail_model_soc_percent=float(np.median(soc[m])), tail_apparent_soc_percent=float(np.median(apparent_soc)) if in_range.all() else None,
                apparent_minus_model_soc_percentage_points=float(np.median(apparent_soc-soc[m])) if in_range.all() else None,
                tail_residual_median_V=float(np.median(residual[m])),
                tail_voltage_drift_V_per_s=float((actual[last]-actual[max(start,last-3)])/min(3,last-start)),
                equilibrium_OCV_verified=False))
        # Symmetric perturbations, fixed measured current; diagnostic ranges, no optimization.
        specs = [('initial_SOC_1pp',dict(s0=s0-1),dict(s0=s0+1)),
                 ('capacity_10percent',dict(s0=s0,capacity=162),dict(s0=s0,capacity=198)),
                 ('R_10percent',dict(s0=s0,rscale=.9),dict(s0=s0,rscale=1.1)),
                 ('OCV_offset_1V',dict(s0=s0,uoffset=-1),dict(s0=s0,uoffset=1))]
        columns = []
        for name, minus_kw, plus_kw in specs:
            vm = voltage(q,i,**minus_kw)[1]; vp = voltage(q,i,**plus_kw)[1]
            delta = (vp-vm)/2
            columns.append(delta[mask])
            perturbations.append(dict(test=test, parameter=name,
                minus_voltage_RMSE_V=float(np.sqrt(np.mean((vm[mask]-actual[mask])**2))),
                base_voltage_RMSE_V=float(np.sqrt(np.mean(residual[mask]**2))),
                plus_voltage_RMSE_V=float(np.sqrt(np.mean((vp[mask]-actual[mask])**2))),
                central_voltage_response_RMS_V=float(np.sqrt(np.mean(delta[mask]**2))),
                initial_values_other_than_declared_parameter_unchanged=True, adopted=False))
        x = np.column_stack(columns)
        xn = x/np.linalg.norm(x,axis=0)
        sv = np.linalg.svd(xn,compute_uv=False)
        cosine = xn.T@xn
        conditioning.append(dict(test=test, parameter_order=[x[0] for x in specs],
            normalized_singular_values=sv.tolist(), normalized_design_condition_number=float(sv[0]/sv[-1]),
            initial_SOC_and_OCV_offset_cosine=float(cosine[0,3]),
            note='Local normalized response similarity; no statistical confidence interval or unique parameter identification'))
    for name, rows in [('residual_summary',summaries),('current_groups',groups),('stopped_low_current_windows',stops),('diagnostic_perturbations',perturbations)]:
        pd.DataFrame(rows).to_csv(HERE/(name+'.csv'),index=False)
    (HERE/'conditioning.json').write_text(json.dumps(conditioning,indent=2)+'\n')
    (HERE/'QA.json').write_text(json.dumps(dict(parameter_fitting=False, adopted_parameters_changed=False,
        new_CRUISE_runs=0, evaluated_on_common_1s_grid=True, existing_evaluation_windows_retained=True,
        source_hashes=hashes, stopped_windows_prove_equilibrium_OCV=False,
        parameter_ranges_are_measured_uncertainty=False),indent=2)+'\n')
    print(pd.DataFrame(summaries).round(6).to_string(index=False))
    print(pd.DataFrame(groups).round(6).to_string(index=False))
    print('Stopped low-current windows:',len(stops))
    print('SOC/OCV response cosine:',[(x['test'],x['initial_SOC_and_OCV_offset_cosine'],x['normalized_design_condition_number']) for x in conditioning])

if __name__=='__main__':
    main()
