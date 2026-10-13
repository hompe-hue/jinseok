"""Offline source-context scenarios; no fitting or CRUISE input changes."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/battery_capacity_scope_gate_20261013'
OUT.mkdir(parents=True,exist_ok=True)
o=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
r=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
rows=[]
for test in ['61905060','61905061']:
    base=ROOT/'independent_tests_20261013'/('ANL'+test)
    d=pd.read_csv(base/'reference_native.csv'); m=json.loads((base/'checkpoint.json').read_text())
    t=d.phase_time_s.to_numpy();i=d.meter_current_A_discharge_positive.to_numpy()
    q=cumulative_trapezoid(i,t,initial=0)/3600
    tc=np.arange(int(np.floor(t[-1]))+1,dtype=float)
    actual=np.interp(tc,t,d.meter_voltage_V)
    baseline=None
    outputs={}
    for capacity in [168.,167.7,180.]:
        s=m['initial_SOC_model_percent']-100*q/capacity
        assert s.min()>=0 and s.max()<=100
        v=96*np.interp(s,o[:,0],o[:,1])-32*np.interp(s/100,r[:,0],r[:,1])*i
        outputs[capacity]=v
        if capacity==168:baseline=v
        err=np.interp(tc,t,v)-actual
        rows.append(dict(test=test,capacity_Ah=capacity,cell_capacity_Ah=capacity/3,RMSE_V=np.sqrt(np.mean(err**2)),mean_bias_V=err.mean(),terminal_SOC_percent=s[-1],terminal_voltage_difference_from_168Ah_V=v[-1]-baseline[-1],mean_voltage_difference_from_168Ah_V=np.mean(v-baseline),maximum_voltage_difference_from_168Ah_V=np.max(v-baseline),minimum_voltage_difference_from_168Ah_V=np.min(v-baseline)))
    df=pd.DataFrame({'time_s':t,'measured_voltage_V':d.meter_voltage_V})
    for capacity,v in outputs.items():df[f'replay_voltage_{capacity:g}Ah_V']=v
    df.to_csv(OUT/('ANL'+test+'_capacity_scenarios.csv'),index=False)
pd.DataFrame(rows).to_csv(OUT/'capacity_comparison.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
