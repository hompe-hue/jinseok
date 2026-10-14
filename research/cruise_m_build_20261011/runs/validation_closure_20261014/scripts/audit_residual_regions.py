"""Partition existing-run residuals by model shaft state; no causal fitting."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
records=[]
for test in ['61905060','61905061']:
    if test.endswith('60'):
        folder=ROOT/'runs/ANL61905060_DIS80_20261013'
        d=pd.read_csv(folder/'aligned_comparison.csv').rename(columns={'model_DC_kW':'pm','reference_meter_DC_kW':'pr'})
        vel=folder/'velocity_ANL61905060DIS80.csv'
        metrics=json.loads((folder/'verification.json').read_text())['diagnostic']
        en_model,en_ref=metrics['model_net_kWh'],metrics['reference_net_kWh']
    else:
        folder=ROOT/'runs/ANL61905061_20261013'
        d=pd.read_csv(folder/'aligned_diagnostics.csv').rename(columns={'model_discharge_power_kW':'pm','reference_discharge_power_kW':'pr'})
        vel=folder/'velocity_ANL61905061.csv'
    v=pd.read_csv(vel,skiprows=[1])
    assert np.array_equal(v.Time,d.time_s)
    shaft=v[[c for c in v if c.startswith('In/E-Motor Power Mech.')][0]].to_numpy()
    take=d.time_s>=20;shaft=shaft[take];d=d.loc[take];t=d.time_s.to_numpy();dt=np.diff(t)
    delta=d.pm.to_numpy()-d.pr.to_numpy();mid_delta=(delta[1:]+delta[:-1])/2
    mid_shaft=(shaft[1:]+shaft[:-1])/2
    mid_speed=(d.actual_kmh.to_numpy()[1:]+d.actual_kmh.to_numpy()[:-1])/2
    common=float(np.sum(mid_delta*dt)/3600)
    en_model=float(np.trapezoid(d.pm,t)/3600)
    refpath=ROOT/f'independent_tests_20261013/ANL{test}/reference_native.csv'
    native=pd.read_csv(refpath);nt=native.phase_time_s.to_numpy()
    z=np.r_[20.,nt[(nt>20)&(nt<t[-1])],t[-1]]
    en_ref=float(np.trapezoid(np.interp(z,nt,native.meter_power_kW_discharge_positive),z)/3600)
    native_residual=en_model-en_ref
    cases=[]
    for threshold in [.5,1.,2.]:
        categories=np.where(mid_shaft>threshold,'positive_shaft',np.where(mid_shaft< -threshold,'negative_shaft',np.where(mid_speed<=1,'stationary','low_shaft_moving')))
        rows=[]
        for name in ['positive_shaft','negative_shaft','stationary','low_shaft_moving']:
            mask=categories==name
            rows.append({'test':test,'shaft_threshold_kW':threshold,'category':name,
                'duration_s':float(dt[mask].sum()),'signed_residual_kWh':float(np.sum(mid_delta[mask]*dt[mask])/3600),
                'positive_residual_kWh':float(np.sum(np.maximum(mid_delta[mask],0)*dt[mask])/3600),
                'negative_residual_kWh':float(np.sum(np.minimum(mid_delta[mask],0)*dt[mask])/3600)})
        assert abs(sum(x['signed_residual_kWh'] for x in rows)-common)<1e-12
        correction=sum(x['signed_residual_kWh'] for x in rows if x['category'] in ['negative_shaft','low_shaft_moving'])
        cases.append({'threshold_kW':threshold,'regions':rows,
            'algebraic_perfect_negative_and_low_shaft_residual_kWh':native_residual-correction,
            'algebraic_remaining_error_percent':100*(native_residual-correction)/en_ref,
            'scope':'Set existing negative/low-shaft signed residual tozero only; fixed-state accounting, not a controller/regen modification or CRUISE prediction.'})
    rec={'test':test,'energy_window_s':[20,float(t[-1])],'model_kWh':en_model,'reference_native_kWh':en_ref,
        'native_residual_kWh':native_residual,'common_grid_residual_kWh':common,
        'native_minus_common_grid_kWh':native_residual-common,'cases':cases,
        'required_reduction_to_upper5percent_kWh':max(0,en_model-1.05*en_ref),
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [vel,refpath]},
        'classification_caution':'Model shaft state, not independently measured driver braking state. Changes in controls may change the trajectory. No passive-loss or regen split parameter is identified.'}
    records.append(rec)
(OUT/'residual_regions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
pd.DataFrame([r for d in records for c in d['cases'] for r in c['regions']]).to_csv(OUT/'residual_regions.csv',index=False)
print(json.dumps([{'test':d['test'],'reduction_needed_kWh':d['required_reduction_to_upper5percent_kWh'],
    'region_1kW':d['cases'][1],'remaining_error_range_percent':[min(c['algebraic_remaining_error_percent'] for c in d['cases']),max(c['algebraic_remaining_error_percent'] for c in d['cases'])]} for d in records],ensure_ascii=False,indent=2))
