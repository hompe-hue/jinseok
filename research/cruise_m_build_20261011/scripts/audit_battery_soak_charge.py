"""Inspect newly acquired soak/full-charge ANL data; never fit OCV/R or call charge Ah capacity."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from nptdms import TdmsFile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs/core_evidence_20261013'
manifest=json.loads((OUT/'new_battery_source_manifest.json').read_text())
records=[]; rests=[]
ocv=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
res=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
for m in manifest:
 test=m['test'];p=OUT/f'sources/ANL{test}.tdms';assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
 g=TdmsFile.read(p).groups()[0];n=len(g['Time_H0']);tt=g['Time_H0'][:]
 names=['Batt_Volt_Hioki_U1','Batt_Curr_Hioki_I1','Batt_Power_Hioki_P1','Dyno_Spd_Front']
 d=pd.DataFrame({'meter_time_s':tt,**{k:g[k][:] for k in names}}).drop_duplicates('meter_time_s',keep='last').sort_values('meter_time_s')
 tt=d.meter_time_s.to_numpy();v=d.Batt_Volt_Hioki_U1.to_numpy();i=d.Batt_Curr_Hioki_I1.to_numpy();power=d.Batt_Power_Hioki_P1.to_numpy();speed=d.Dyno_Spd_Front.to_numpy()*1.609344
 assert np.all(np.diff(tt)>0)
 available={c.name for c in g.channels()}
 cannames=[k for k in ['HVBatt_SOC_displayed_CAN3','HVBatt_pack_SOC_HPCM2','HVBatt_cell_temp_1_CAN3'] if k in available]
 if cannames:
  can=pd.DataFrame({'t':g['Time_3'][:],**{k:g[k][:] for k in cannames}}).drop_duplicates('t',keep='last').sort_values('t')
  # Mask outside coverage instead of endpoint extrapolation.
  cover=(tt>=can.t.min())&(tt<=can.t.max())
  for k in cannames:d[k]=np.where(cover,np.interp(tt,can.t,can[k]),np.nan)
 valid=(v>250)&(v<450)&np.isfinite(i)&np.isfinite(power)
 stationary=abs(speed)<.1; low=valid&stationary&(abs(i)<3)
 median=float(np.median(np.diff(tt))); edges=np.flatnonzero(np.diff(np.r_[False,low,False]));ts=[];all_durations=[]
 for a,b in zip(edges[::2],edges[1::2]):
  duration=float(tt[b-1]-tt[a]);all_durations.append(duration)
  if duration<60:continue
  interval={'test':test,'start_s':float(tt[a]),'end_s':float(tt[b-1]),'duration_s':duration,'voltage_start_V':float(v[a]),'voltage_end_V':float(v[b-1]),'voltage_change_V':float(v[b-1]-v[a]),'current_abs_max_A':float(abs(i[a:b]).max()),'current_mean_A':float(i[a:b].mean()),'current_min_A':float(i[a:b].min()),'current_max_A':float(i[a:b].max())}
  for k in cannames:
   x=d[k].to_numpy()[a:b];finite=x[np.isfinite(x)];interval[k+'_range']=[float(finite.min()),float(finite.max())] if finite.size else None
  rests.append(interval);ts.append(interval)
 r={'test':test,'source':m,'rows':len(tt),'meter_sampling_median_s':median,'valid_HV_rows':int(valid.sum()),'invalid_HV_rows':int((~valid).sum()),'observed_duration_s':float(tt[-1]-tt[0]),'max_valid_VI_vs_meter_kW':float(np.max(abs(v[valid]*i[valid]/1000-power[valid]))),'available_CAN_channels':cannames,'rest_intervals_ge60s':len(ts),'rest_intervals_ge300s':sum(x['duration_s']>=300 for x in ts),'longest_valid_low_current_rest_s':max(all_durations,default=0),'rest_caution':'Speed<0.1km/h, |I|<3A,250<V<450V; stationary low load is not proven equilibrium OCV. Off-bus voltage excluded, CAN values may be stale when bus off.'}
 if test in ['61905065','61905068']:
  a=int(str(g.properties['Phase_1_Phase_Start_Fill_Index']).strip().split(',')[0])-1
  b=int(str(g.properties['Phase_1_Phase_Stop_Fill_Index']).strip().split(',')[0])-1
  # Original fill indices are 1 based. Include start and final endpoint samples.
  rawt=g['Time_H0'][:];rawi=g['Batt_Curr_Hioki_I1'][:];rawp=g['Batt_Power_Hioki_P1'][:];rawv=g['Batt_Volt_Hioki_U1'][:]
  ah=float(np.trapezoid(rawi[a:b+1],rawt[a:b+1])/3600);kwh=float(np.trapezoid(rawp[a:b+1],rawt[a:b+1])/3600)
  dt=np.diff(rawt[a:b+1]);vv=(rawv[a:b+1]>250)&(rawv[a:b+1]<450);pair=vv[:-1]&vv[1:]&(dt>0)&(dt<2.1*median)
  active_ah=-float(np.sum((rawi[a:b]+rawi[a+1:b+1])/2*dt*pair)/3600)
  active_kwh=-float(np.sum((rawp[a:b]+rawp[a+1:b+1])/2*dt*pair)/3600)
  off=abs(v)<1
  r['reconciliation']={'active_HV_pair_injected_Ah':active_ah,'active_HV_pair_injected_kWh':active_kwh,'off_bus_current_median_A':float(np.median(i[off])) if off.any() else None,'active_Ah_minus_published_summary_Ah':active_ah+float(g.properties['Phase_1_Elec_Ahr_Ahr']),'active_kWh_minus_published_summary_kWh':active_kwh+float(g.properties['Phase_1_Elec_Whr_Whr'])/1000,'status':'Raw phase and active-HV integrals do not reproduce published summary; off-bus current is nonzero. Offset/processing hypothesis remains unverified; no correction applied.'}
  r['full_charge']={'phase_start_index_zero_based':a,'phase_stop_index_zero_based_inclusive':b,'net_injected_Ah':-ah,'net_injected_kWh':-kwh,'summary_injected_Ah':-float(g.properties['Phase_1_Elec_Ahr_Ahr']),'summary_injected_kWh':-float(g.properties['Phase_1_Elec_Whr_Whr'])/1000,'difference_from168Ah_percent':(-ah/168-1)*100,'interpretation':'Operational replenishment amount after depletion; charging efficiency, reserve/clipping, ending criterion and auxiliary boundaries prevent equating it to physical rated/discharge capacity.'}
  if 'HVBatt_SOC_displayed_CAN3' in cannames:
   soc=d.HVBatt_SOC_displayed_CAN3.to_numpy();mask=valid&np.isfinite(soc)
   # Explicit CAN-coordinate hypothesis with no initial offset/parameter fitting.
   predicted=96*np.interp(soc,ocv[:,0],ocv[:,1])-i*96/3*np.interp(soc/100,res[:,0],res[:,1])
   err=predicted[mask]-v[mask]
   r['direct_displayed_SOC_charge_voltage_hypothesis']={'rows':int(mask.sum()),'SOC_range_percent':[float(soc[mask].min()),float(soc[mask].max())],'temperature_range_C':[float(d.HVBatt_cell_temp_1_CAN3[mask].min()),float(d.HVBatt_cell_temp_1_CAN3[mask].max())],'RMSE_V':float(np.sqrt(np.mean(err*err))),'bias_V':float(err.mean()),'max_abs_V':float(abs(err).max()),'caution':'Unchanged25C OCV/R with displayed CAN SOC assumed equal to source coordinate. No parameter fit or state inversion. Charging data with nonzero current; this tests hypothesis, not equilibrium OCV or discharge validation.'}
   bins=[]
   for lo,hi in [(0,5),(5,20),(20,60),(60,90),(90,100)]:
    mm=mask&(soc>=lo)&(soc<hi);ee=predicted[mm]-v[mm]
    bins.append({'SOC_lo_percent':lo,'SOC_hi_exclusive_percent':hi,'rows':int(mm.sum()),'RMSE_V':float(np.sqrt(np.mean(ee*ee))) if ee.size else None,'bias_V':float(ee.mean()) if ee.size else None})
   r['charge_voltage_SOC_bins']=bins
   d['voltage_from_displayed_SOC_hypothesis_V']=predicted
  else:r['charge_voltage_validation']='No CAN SOC/temperature channels: no invented SOC trajectory from nominal capacity.'
 d['valid_HV']=valid;d['stationary_low_current']=low
 d.to_csv(OUT/f'ANL{test}_battery_evidence.csv',index=False)
 r['channel_metadata']={k:dict(g[k].properties) for k in names+cannames}
 records.append(r)
(OUT/'battery_soak_charge_summary.json').write_text(json.dumps(records,indent=2,default=str)+'\n')
pd.DataFrame(rests).to_csv(OUT/'valid_rest_intervals.csv',index=False)
print(json.dumps([{k:v for k,v in r.items() if k!='channel_metadata'} for r in records],indent=2))
