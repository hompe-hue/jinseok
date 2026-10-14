"""Frozen C2 current-driven battery replay, not a CRUISE M vehicle run or refit."""
from pathlib import Path
import hashlib,json,os
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from nptdms import TdmsFile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT if (ROOT/'test_manifest.json').exists() else ROOT/'runs/C2_performance_extension_20261014'
MAPS=ROOT/'maps' if OUT==ROOT else ROOT/'runs/C2_battery_common_20261014/inputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hold(t,y,x):
    d=pd.DataFrame({'t':t,'y':y}).dropna().groupby('t').y.median()
    tt=d.index.to_numpy(); yy=d.to_numpy(); j=np.searchsorted(tt,x,side='right')-1; k=np.clip(j,0,len(tt)-1)
    ok=(j>=0)&(x-tt[k]>=0)&(x-tt[k]<=2)
    return np.where(ok,yy[k],np.nan)
def main():
    (OUT/'replay').mkdir(parents=True,exist_ok=True)
    ocv=np.loadtxt(MAPS/'C2_Cell_OCV_25C.dat',skiprows=2)
    r=np.loadtxt(MAPS/'C2_Cell_Resistance_25C.dat',skiprows=2)
    capacity=3*53.747104484472885
    reports=[]; binrows=[]
    for test in ['61905064','61905067']:
        path=OUT/'sources'/f'ANL{test}.tdms'
        if not path.exists():
            part=path.with_suffix('.tdms.part')
            assert test=='61905064' and part.stat().st_size==189260312
            assert sha(part)=='5680c75633dfcab2403269a3e313316f7d8c116a7c7fb845cd3a204a6098c11b'
            os.replace(part,path)
        with TdmsFile.open(path) as f:
            g=f.groups()[0];props=g.properties
            assert '2017 Chevrolet Bolt'==props['TestInfo_Vehicle_Name']
            start=int(props['Phase_1_Phase_Start_Fill_Index'])-1;stop=int(props['Phase_1_Phase_Stop_Fill_Index'])
            def a(n):return np.asarray(g[n][start:stop],dtype=float)
            native=a('Time_H0');ct=a('Time_3')
            d=pd.DataFrame({'t':native,'v':a('Batt_Volt_Hioki_U1'),'i':a('Batt_Curr_Hioki_I1'),'p':a('Batt_Power_Hioki_P1')}).dropna().groupby('t').median().sort_index().reset_index()
            for name,channel in [('CAN_HPCM2_SOC_percent','HVBatt_pack_SOC_HPCM2'),('temperature_C','HVBatt_cell_temp_1_CAN3')]:
                d[name]=hold(ct,a(channel),d.t.to_numpy())
            speed=hold(a('Time'),a('Dyno_Spd')*1.609344,d.t.to_numpy())
            d['speed_kmh']=speed;d.t-=d.t.iloc[0]
            vin=props['TestInfo_Vehicle_VIN'];declared=float(props['Phase_1_Phase_Length_s'])
        t=d.t.to_numpy();i=d.i.to_numpy();v=d.v.to_numpy();valid=np.isfinite(v)&(v>=200)&(v<=450)&(abs(i)<=1000)
        # Same first low-load V/I anchor concept as warm C2; no CAN SOC fitting.
        anchor=d[(d.t<=5)&valid&(d.i.abs()<3)]
        assert len(anchor)>=10
        va=float(anchor.v.median());ia=float(anchor.i.median())
        s0=brentq(lambda s:96*np.interp(s,ocv[:,0],ocv[:,1])-ia*32*np.interp(s/100,r[:,0],r[:,1])-va,0,100)
        dt=np.diff(t);good=(dt>0)&(dt<=2)&valid[:-1]&valid[1:]
        q=np.r_[0,np.cumsum(np.where(good,(i[:-1]+i[1:])*.5*dt/3600,0))]
        soc=s0-q/capacity*100
        inmap=(soc>=0)&(soc<=100)
        vv=96*np.interp(np.clip(soc,0,100),ocv[:,0],ocv[:,1])-i*32*np.interp(np.clip(soc/100,0,1),r[:,0],r[:,1])
        # Stop evaluation before first invalid meter interval. Do not bridge outages.
        firstbad=np.flatnonzero(~good);trusted=np.ones(len(d),bool)
        if len(firstbad):trusted[firstbad[0]+1:]=False
        evaluate=valid&trusted&inmap&(t>=20)
        d['net_Ah_since_phase_start']=q;d['C2_model_SOC_percent_unclipped']=soc;d['C2_voltage_replay_V']=np.where(evaluate,vv,np.nan)
        d['C2_model_in_SOC_map']=inmap;d['evaluated']=evaluate
        d.to_csv(OUT/'replay'/f'ANL{test}_frozen_C2_replay.csv',index=False)
        for lo,hi in [(0,10),(10,20),(20,40),(40,60),(60,80),(80,100)]:
            m=evaluate&(soc>=lo)&(soc<hi)
            if not m.any():continue
            e=vv[m]-v[m]
            binrows.append(dict(test=test,bin_basis='C2 charge-integrated model SOC, not CAN',SOC_lower_percent=lo,SOC_upper_percent=hi,n=int(m.sum()),voltage_RMSE_V=float(np.sqrt(np.mean(e*e))),voltage_bias_V=float(e.mean()),CAN_SOC_min=float(d.loc[m,'CAN_HPCM2_SOC_percent'].min()),CAN_SOC_max=float(d.loc[m,'CAN_HPCM2_SOC_percent'].max()),temperature_min_C=float(d.loc[m,'temperature_C'].min()),temperature_max_C=float(d.loc[m,'temperature_C'].max())))
        e=vv[evaluate]-v[evaluate]
        crosses={}
        for level in [40,30,20,10,0]:
            k=np.flatnonzero(trusted&(soc<=level))
            crosses[str(level)]=dict(time_s=float(t[k[0]]),CAN_HPCM2_SOC_percent=float(d.CAN_HPCM2_SOC_percent.iloc[k[0]]),voltage_V=float(v[k[0]]),power_kW=float(d.p.iloc[k[0]])) if len(k) else None
        low=d[valid&d.CAN_HPCM2_SOC_percent.lt(20)&d.p.gt(0)]
        reports.append(dict(test=test,source_sha256=sha(path),bytes=path.stat().st_size,VIN=vin,native_rows=stop-start,unique_meter_rows=len(d),phase_declared_s=declared,meter_span_s=float(t[-1]),anchor_first_5s_lowload_median_V=va,anchor_median_A=ia,anchor_rows=len(anchor),initial_C2_SOC_percent=s0,capacity_Ah=capacity,valid_net_Ah=float(q[-1]),C2_final_SOC_unclipped_percent=float(soc[-1]),evaluated_rows=int(evaluate.sum()),voltage_RMSE_V=float(np.sqrt(np.mean(e*e))),voltage_bias_V=float(e.mean()),SOC_crossings=crosses,real_low_CAN_SOC_discharge_power_p95_kW=float(low.p.quantile(.95)),real_low_CAN_SOC_discharge_power_max_kW=float(low.p.max()),SOC_CAN_model_are_not_equated=True,current_driven_not_vehicle_simulation=True,thermal_model='Frozen static25C C2; measured temperature varies; thermal causality not identified',no_parameters_fitted=True,BMS_policy_identified=False))
    pd.DataFrame(binrows).to_csv(OUT/'replay/SOC_binned_voltage_metrics.csv',index=False)
    (OUT/'replay/summary.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    manifest=json.loads((OUT/'sources/source_manifest.json').read_text())
    for x in manifest:
        p=OUT/'sources'/x['name']
        if p.exists():x.update(bytes=p.stat().st_size,sha256=sha(p),integrity_verified=True);x.pop('error',None)
        if x['name']=='ANL61905064.tdms':x['prior_793593_hash_is_selected_CSV_not_this_raw_TDMS']=True
    (OUT/'sources/source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(reports,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
