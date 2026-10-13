"""Screen separate discharge data without fitting OCV, R, RC or capacity."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from nptdms import TdmsFile

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[2]
OUT=ROOT/'runs/battery_identification_feasibility_20261013'
OUT.mkdir(parents=True,exist_ok=True)

def hold(clock,value,t):
    v=pd.DataFrame({'t':clock,'v':value}).dropna().groupby('t').v.median()
    x=v.index.to_numpy(); y=v.to_numpy(); j=np.searchsorted(x,t,side='right')-1
    ok=(j>=0)&(j<len(x))
    k=np.clip(j,0,len(x)-1); ok &= (t-x[k]>=0)&(t-x[k]<=2)
    return np.where(ok,y[k],np.nan)

def load(test):
    if test=='61905064':
        path=WORK/'map_original/datakit/Bolt_CRUISE_M_DataKit/data/ANL_61905064_selected_native_rows.csv'
        allrows=pd.read_csv(path)
        old=json.loads((ROOT.parent/'validation_fix_20261006/results/battery_data_quality.json').read_text())
        info=next(x for x in old if x['test']==test)
        d=allrows.iloc[info['phase_start_row_zero_based']:info['phase_stop_row_exclusive']].copy()
        x=pd.DataFrame(dict(t=d.meter_clock_s,v=d.meter_pack_voltage_V,i=d.meter_pack_current_A_discharge_positive,p=d.meter_pack_power_kW_discharge_positive,speed=d.dyno_speed_mph*1.609344))
        can_t=d.CAN_clock_s.to_numpy()
        fields={'display':d.displayed_SOC_percent.to_numpy(),'hpcm2':d.internal_SOC_HPCM2_percent.to_numpy(),'temperature':d.battery_temperature_CAN_degC.to_numpy()}
    else:
        path=WORK/'source_work/ANL61905067_Raw_Source/61905067_Analysis.tdms'
        g=TdmsFile.read(path).groups()[0]; props=g.properties
        start=int(props['Phase_1_Phase_Start_Fill_Index'])-1; stop=int(props['Phase_1_Phase_Stop_Fill_Index'])
        def a(n): return np.asarray(g[n][:][start:stop],dtype=float)
        x=pd.DataFrame(dict(t=a('Time_H0'),v=a('Batt_Volt_Hioki_U1'),i=a('Batt_Curr_Hioki_I1'),p=a('Batt_Power_Hioki_P1'),speed=a('Dyno_Spd')*1.609344))
        can_t=a('Time_3')
        fields={'display':a('HVBatt_SOC_displayed_CAN3'),'hpcm2':a('HVBatt_pack_SOC_HPCM2'),'temperature':a('HVBatt_cell_temp_1_CAN3')}
    count=len(x); x=x.dropna().groupby('t').median().sort_index().reset_index()
    for name,y in fields.items(): x[name]=hold(can_t,y,x.t.to_numpy())
    x['t']=x.t-x.t.iloc[0]
    return x,path,count

reports=[]; rests=[]; pulses=[]; bins=[]
for test in ['61905064','61905067']:
    d,path,count=load(test)
    t=d.t.to_numpy(); dt=np.diff(t)
    valid=d.v.between(200,450)&d.i.abs().le(1000)
    keep=(dt>0)&(dt<=2)&valid.to_numpy()[:-1]&valid.to_numpy()[1:]
    q=np.sum((d.i.to_numpy()[:-1]+d.i.to_numpy()[1:])[keep]*.5*dt[keep])/3600
    mask=valid & d.i.abs().lt(3) & d.speed.abs().lt(.1)
    starts=np.flatnonzero(mask & (~mask.shift(1,fill_value=False) | d.t.diff().gt(2)))
    ends=np.flatnonzero(mask & (~mask.shift(-1,fill_value=False) | d.t.diff().shift(-1).gt(2)))
    for st,en in zip(starts,ends):
        if t[en]-t[st]>=10:
            rests.append(dict(test=test,start_s=t[st],end_s=t[en],duration_s=t[en]-t[st],initial_V=d.v.iloc[st],last_V=d.v.iloc[en],voltage_change_V=d.v.iloc[en]-d.v.iloc[st],SOC_HPCM2=d.hpcm2.iloc[st]))
    # Conservative operational steps: 0.5 s plateaus immediately before/after,
    # current SD < 2 A, |deltaI| >=10 A, all samples voltage-valid, no >0.2s gaps.
    last=-100.
    for k in np.flatnonzero(np.abs(np.diff(d.i.to_numpy(),prepend=d.i.iloc[0]))>=10):
        tk=t[k]
        if tk-last<2:continue
        a=d[(d.t>=tk-.6)&(d.t<tk-.1)]; b=d[(d.t>=tk+.1)&(d.t<tk+.6)]
        if len(a)<3 or len(b)<3:continue
        full=d[(d.t>=tk-.6)&(d.t<tk+.6)]
        if not full.v.between(200,450).all() or full.t.diff().max()>.2:continue
        if a.i.std()>2 or b.i.std()>2:continue
        di=b.i.mean()-a.i.mean()
        if abs(di)<10:continue
        rr=-(b.v.mean()-a.v.mean())/di
        pulses.append(dict(test=test,time_s=tk,delta_current_A=di,delta_voltage_V=b.v.mean()-a.v.mean(),apparent_short_window_R_ohm=rr,SOC_HPCM2=full.hpcm2.median(),temperature_C=full.temperature.median()))
        last=tk
    for lo,hi in [(5,10),(10,20),(20,40),(40,60),(60,80)]:
        z=d[valid & d.hpcm2.ge(lo)&d.hpcm2.lt(hi)]
        if len(z):bins.append(dict(test=test,SOC_HPCM2_lower=lo,SOC_HPCM2_upper=hi,rows=len(z),current_mean_A=z.i.mean(),current_SD_A=z.i.std(),current_p05_A=z.i.quantile(.05),current_p95_A=z.i.quantile(.95),temperature_min_C=z.temperature.min(),temperature_max_C=z.temperature.max()))
    rr=[z for z in rests if z['test']==test]; pp=[z for z in pulses if z['test']==test]
    reports.append(dict(test=test,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),native_phase_rows=count,unique_meter_rows=len(d),invalid_voltage_rows=int((~valid).sum()),valid_integrated_s=float(dt[keep].sum()),meter_span_s=float(t[-1]),valid_net_Ah=q,
        temperature_range_C=[float(d.loc[valid,'temperature'].min()),float(d.loc[valid,'temperature'].max())],SOC_HPCM2_range=[float(d.loc[valid,'hpcm2'].min()),float(d.loc[valid,'hpcm2'].max())],rest_windows_ge10s=len(rr),longest_screened_rest_s=max([z['duration_s'] for z in rr],default=0),rest_windows_ge300s=sum(z['duration_s']>=300 for z in rr),screened_step_candidates=len(pp),
        full_OCV_R_RC_identification_supported=False,reason='No established equilibrium OCV anchor or controlled HPPC sequence; steady-speed depletion confounds SOC, temperature and voltage history. Apparent short-window R is diagnostic only.'))
    if test=='61905067':d.to_csv(OUT/'ANL61905067_phase_meter_CAN_aligned.csv',index=False)
for name,data in [('rest_windows',rests),('short_window_step_candidates',pulses),('SOC_bin_excitation',bins)]:
    pd.DataFrame(data).to_csv(OUT/(name+'.csv'),index=False)
encoded=json.dumps(reports,indent=2,allow_nan=False,default=lambda x:x.item())
(OUT/'summary.json').write_text(encoded)
print(encoded)
