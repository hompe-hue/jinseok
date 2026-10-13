import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs'/'battery_current_replay_20261013'
OUT.mkdir(parents=True,exist_ok=True)
ocv=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
res=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
def voltage(s,i):
    return 96*np.interp(s,ocv[:,0],ocv[:,1])-32*np.interp(s/100,res[:,0],res[:,1])*i
def metric(error):
    return dict(RMSE_V=float(np.sqrt(np.mean(error**2))),mean_bias_V=float(np.mean(error)),max_abs_V=float(np.max(np.abs(error))))

summary=[]
for test in ['61905060','61905061']:
    inp=ROOT/'independent_tests_20261013'/('ANL'+test)
    run=ROOT/'runs'/('ANL'+test+'_20261013')
    ref=pd.read_csv(inp/'reference_native.csv')
    meta=json.loads((inp/'checkpoint.json').read_text())
    t=ref.phase_time_s.to_numpy(); i=ref.meter_current_A_discharge_positive.to_numpy()
    assert np.all(np.diff(t)>0) and np.max(np.diff(t))<0.2
    assert np.all(np.isfinite(ref[['phase_time_s','meter_voltage_V','meter_current_A_discharge_positive']]))
    q=cumulative_trapezoid(i,t,initial=0)/3600
    s=meta['initial_SOC_model_percent']-100*q/168
    assert s.min()>0 and s.max()<100
    v=voltage(s,i)
    aligned=pd.read_csv(run/'aligned_diagnostics.csv')
    tm=aligned.time_s.to_numpy(); im=aligned.model_discharge_current_A.to_numpy()
    sm=meta['initial_SOC_model_percent']-100*cumulative_trapezoid(im,tm,initial=0)/(3600*168)
    vm=voltage(sm,im)
    # Compare on the already exported common integer-second grid; no endpoint extrapolation.
    valid=(tm>=t[0])&(tm<=t[-1])
    tc=tm[valid]; a=aligned.loc[valid].copy()
    vr=np.interp(tc,t,v); sr=np.interp(tc,t,s)
    a['reference_current_replay_SOC_percent']=sr
    a['reference_current_replay_voltage_V']=vr
    a['model_current_replay_voltage_V']=vm[valid]
    a['reference_replay_minus_measured_V']=vr-a.reference_voltage_V
    a['model_replay_minus_export_V']=vm[valid]-a.model_voltage_V
    a.to_csv(OUT/('ANL'+test+'_replay_common_grid.csv'),index=False)
    pd.DataFrame(dict(time_s=t,reference_current_A=i,net_charge_removed_Ah=q,replay_SOC_percent=s,replay_voltage_V=v,measured_voltage_V=ref.meter_voltage_V)).to_csv(OUT/('ANL'+test+'_replay_native.csv'),index=False)
    d=dict(test=test,native_rows=len(t),common_rows=len(a),maximum_time_gap_s=float(np.max(np.diff(t))),
        initial_SOC_percent=meta['initial_SOC_model_percent'],capacity_Ah=168,
        end_replay_SOC_percent=float(s[-1]),net_removed_Ah=float(q[-1]),
        source_sha256=hashlib.sha256((inp/'reference_native.csv').read_bytes()).hexdigest(),
        exported_model_vs_measured=metric(a.model_voltage_V-a.reference_voltage_V),
        measured_current_replay_vs_measured=metric(a.reference_replay_minus_measured_V),
        model_current_replay_vs_export=metric(a.model_replay_minus_export_V))
    diag=json.loads((run/'battery_rest_diagnosis'/'diagnosis.json').read_text())
    d['existing_rest_intervals']=[]
    for seg in diag['rest_intervals']:
        sub=a[(a.time_s>=seg['start_s'])&(a.time_s<=seg['end_s'])]
        d['existing_rest_intervals'].append(dict(start_s=seg['start_s'],end_s=seg['end_s'],replay_bias_V=float(sub.reference_replay_minus_measured_V.mean()),export_bias_V=float((sub.model_voltage_V-sub.reference_voltage_V).mean())))
    summary.append(d)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
