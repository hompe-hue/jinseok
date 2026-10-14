"""Fixed-demand screening of the single common battery candidate.
Actual C2 terminal power for five warm runs; native ANL power for two depletion
runs. Not a new CRUISE M vehicle/controller execution.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs/unified_BEV_model_20261014';C2=ROOT/'runs/C2_battery_common_20261014'
def main():
    cfg=json.loads((OUT/'development_screen.json').read_text());u=np.loadtxt(OUT/'Unified_Candidate_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(OUT/'Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2);capacity=cfg['capacity_Ah'];result=[]
    for test in cfg['train_tests']+cfg['rechecks']:
        ref=pd.read_csv(OUT/f'candidate_replay_{test}.csv');nt=ref.time_s.to_numpy();vref=ref.reference_voltage_V.to_numpy()
        if test in ['61905064','61905067']:
            source=ROOT/f'runs/C2_performance_extension_20261014/replay/ANL{test}_frozen_C2_replay.csv';d=pd.read_csv(source)
            t=np.arange(0,np.floor(nt[-1])+1);power=np.interp(t,d.t,d.p);boundary='Native ANL measured power demand; no vehicle simulation'
        else:
            opts=list((C2/'actual_results'/test/'received').glob('battery*.csv'));assert len(opts)==1;source=opts[0];d=pd.read_csv(source,skiprows=[1]);t=d.Time.to_numpy()
            get=lambda name:d[[k for k in d if k.startswith('In/'+name+' (')][0]].to_numpy()
            power=-get('Current')*get('Voltage')/1000;boundary='Frozen actual C2 terminal power; changed candidate/controller not rerun'
        s0=float(ref.model_SOC_percent.iloc[0])
        def current(tt,s):
            U=96*np.interp(s,u[:,0],u[:,1]);R=32*np.interp(s/100,r[:,0],r[:,1]);P=np.interp(tt,t,power)*1000;disc=U*U-4*R*P
            if disc<0:raise ValueError('Demand exceeds static voltage-root feasibility')
            return 2*P/(U+np.sqrt(disc))
        sol=solve_ivp(lambda tt,ss:[-current(tt,ss[0])/capacity/3600*100],(t[0],t[-1]),[s0],t_eval=t,max_step=.5,rtol=1e-8,atol=1e-9);assert sol.success
        s=sol.y[0];i=np.array([current(tt,ss) for tt,ss in zip(t,s)]);v=96*np.interp(s,u[:,0],u[:,1])-i*32*np.interp(s/100,r[:,0],r[:,1]);e=v-np.interp(t,nt,vref);mask=t>20
        z=dict(test=test,boundary=boundary,voltage_RMSE_V=float(np.sqrt(np.mean(e[mask]**2))),voltage_bias_V=float(e[mask].mean()),final_model_SOC_percent=float(s[-1]),SOC_in_map=bool(s.min()>=0 and s.max()<=100),voltage_screen_thresholds_met=bool(np.sqrt(np.mean(e[mask]**2))<=2 and abs(e[mask].mean())<=1),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),no_CRUISE_run=True,no_BMS_discharge_map_enforced_in_screen=True)
        result.append(z);pd.DataFrame(dict(time_s=t,power_kW=power,candidate_voltage_V=v,reference_voltage_V=np.interp(t,nt,vref),model_SOC_percent=s)).to_csv(OUT/f'candidate_fixed_power_{test}.csv',index=False)
    (OUT/'fixed_power_screen.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');pd.DataFrame(result).to_csv(OUT/'fixed_power_screen_metrics.csv',index=False);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
