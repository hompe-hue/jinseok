"""Prepare a continuous held-out mission without fitting any vehicle parameters."""
from pathlib import Path
import re,json,hashlib
import numpy as np
import pandas as pd
from nptdms import TdmsFile
from scipy.optimize import brentq
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[1]
src=OUT/'sources/ANL61905066.tdms'
assert src.stat().st_size==143149242
g=TdmsFile.read(src).groups()[0]
meta=json.loads((OUT/'phase_metadata_audit.json').read_text())
a=meta['selected_continuous_span']['start_index'];b=meta['selected_continuous_span']['stop_exclusive']
origin=float(g['Time_H0'][a]);tt=g['Time_H0'][a:b]-origin
assert np.all(np.diff(tt)>0)
required={'Time_H0':'s','Dyno_Spd_Front':'mph','Batt_Volt_Hioki_U1':'V','Batt_Curr_Hioki_I1':'A','Batt_Power_Hioki_P1':'kW','DCDC_Out_Power_Hioki_P3':'W','HVBatt_cell_temp_1_CAN3':'C'}
assert all(g[n].properties['unit_string']==u for n,u in required.items())
assert np.max(np.abs(g['Time'][a:b]-g['Time_H0'][a:b]))<1e-9
assert np.max(np.abs(g['Time_3'][a:b]-g['Time_H0'][a:b]))<1e-9
ref=pd.DataFrame({'time_s':tt,'speed_kmh':g['Dyno_Spd_Front'][a:b]*1.609344,
    'meter_voltage_V':g['Batt_Volt_Hioki_U1'][a:b],
    'meter_current_A_discharge_positive':g['Batt_Curr_Hioki_I1'][a:b],
    'meter_power_kW_discharge_positive':g['Batt_Power_Hioki_P1'][a:b],
    'LV_DCDC_output_W':g['DCDC_Out_Power_Hioki_P3'][a:b],
    'battery_temperature_C':g['HVBatt_cell_temp_1_CAN3'][a:b],
    'SOC_displayed_CAN_percent':g['HVBatt_SOC_displayed_CAN3'][a:b],
    'SOC_internal_CAN_percent':g['HVBatt_pack_SOC_HPCM2'][a:b]})
assert np.isfinite(ref.to_numpy()).all()
assert ref.meter_voltage_V.between(250,450).all()
duration=float(tt[-1]);times=np.r_[np.arange(0,np.floor(duration)+1),duration]
speed=np.interp(times,tt,ref.speed_kmh)
driver=pd.DataFrame({'time_s':times,'speed_kmh':speed})
(OUT/'inputs').mkdir(exist_ok=True);(OUT/'references').mkdir(exist_ok=True)
ref.to_csv(OUT/'references/ANL61905066_reference_native.csv',index=False)
driver.to_csv(OUT/'inputs/ANL61905066_driver_1s.csv',index=False)
headers=['Time Velocity Gear "Shift Time" "Start Switch" "Min. Velocity" "Max. Velocity"','s km/h - s - km/h km/h']
dat=OUT/'inputs/ANL61905066_BoltEV_Continuous.dat'
lines=[' '.join([f'{t:.15g}',f'{v:.15g}','1','0','0' if k==len(times)-1 else '1',f'{v:.15g}',f'{v:.15g}']) for k,(t,v) in enumerate(zip(times,speed))]
dat.write_bytes(('\r\n'.join(headers+lines)+'\r\n').encode('ascii'))
x=np.loadtxt(dat,skiprows=2)
assert x.shape==(len(times),7) and np.max(abs(x[:,0]-times))<1e-9 and np.max(abs(x[:,1]-speed))<1e-9
assert np.array_equal(x[:,1],x[:,5]) and np.array_equal(x[:,1],x[:,6])
native_distance=float(np.trapezoid(ref.speed_kmh,tt)/3600)
driver_distance=float(np.trapezoid(speed,times)/3600)
assert abs(driver_distance/native_distance-1)<1e-4
phase_rows=[]
for ph in meta['phases']:
    lo=ph['primary_start'];hi=ph['primary_stop_exclusive']
    ids=list(range(lo,hi));t0=float(g['Time_H0'][lo]-origin);t1=float(g['Time_H0'][hi-1]-origin)
    phase_rows.append({'phase':ph['phase'],'start_s':t0,'end_s':t1,'primary_rows':hi-lo,
        'metadata_duration_s':ph['metadata_duration_s'],'primary_duration_s':t1-t0,
        'additional_metadata_segments':len(ph['start_indices'])-1,
        'summary_energy_kWh':float(g.properties[f"Phase_{ph['phase']}_Elec_Whr_Whr"])/1000,
        'environment_temperature_C':float(g.properties[f"Phase_{ph['phase']}_Cell_Temp_C"])})
pd.DataFrame(phase_rows).to_csv(OUT/'references/phase_windows.csv',index=False)
ocv=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
res=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
v0=float(ref.meter_voltage_V.iloc[0]);i0=float(ref.meter_current_A_discharge_positive.iloc[0])
soc0=brentq(lambda s:96*np.interp(s,ocv[:,0],ocv[:,1])-i0*32*np.interp(s/100,res[:,0],res[:,1])-v0,0,100)
record={'test':'61905066','status':'DATA_READY_MODEL_NOT_FROZEN_CRUISE_NOT_RUN','continuous_duration_s':duration,
    'native_rows':len(ref),'driver_rows':len(driver),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
    'source_url':'https://anl.app.box.com/index.php?rm=box_download_shared_file&shared_name=rpx3ss7ceabzrhgd9k644vka67rx9ce2&file_id=f_1620743305926',
    'source_bytes':src.stat().st_size,'profile_format_sample':'empirical_alignment_20261013/ANL_61905054_phase1/sources/profile_format_sample.dat',
    'profile_columns':headers,'native_distance_km':native_distance,'driver_distance_km':driver_distance,
    'resampling_distance_difference_percent':100*(driver_distance/native_distance-1),
    'initial_SOC_provisional_percent':soc0,'initial_voltage_V':v0,'initial_current_A':i0,
    'initial_battery_temperature_C':float(ref.battery_temperature_C.iloc[0]),
    'observed_battery_temperature_range_C':[float(ref.battery_temperature_C.min()),float(ref.battery_temperature_C.max())],
    'initial_environment_temperature_C':phase_rows[0]['environment_temperature_C'],
    'auxiliary_kW_rule':'Keep previous0.4kW; no fitting to066. Actual final model tobe frozen separately.',
    'grade_rule':'Digital Drive_trace_grade iszero; analogue Grade_Output has small offset, not physical roadgrade.',
    'initialization_rule':'Invert only first low-load V/I using final frozen OCV/R; no manualSOCoffset; no reinitialization betweenphases.',
    'initial_SOC_caution':'Provisional value uses oldOCV/R. Recompute via same rule if calibrated maps change beforefreeze. NotCAN SOCidentification.',
    'sampling_caution':'Main mergedTime andTime3 matchTimeH0. Instrument-localHioki_Time_H0 has38nonpositiveintervals and isnot used toalign.',
    'phase_rule':'Primary longest contiguoussegment perphase; extra1-2sample metadata segments retained inaudit. Neverintegrateacrossseparatedsegments.',
    'evaluation_rule':'Primarycontinuous native-meter comparison20stoactualCSVendpoint; voltageexcludesfirst20s onlyonce; sevenprimarywindows diagnostic. Do notcomparecontinuous integral withsum ofroundedsummarynumbers.',
    'no_model_inputs_modified':True,'no_fit_on066':True,
    'required_before_run':['CurrentsavedDIS80projectorconfirmedfrozenvariant','BEVgeneratorOFF','Unchangedtrain-calibratedmapsandlimits','Input/projectSHA256manifest'],
    'sha256':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [dat,OUT/'inputs/ANL61905066_driver_1s.csv',OUT/'references/ANL61905066_reference_native.csv',OUT/'references/phase_windows.csv']}}
(OUT/'066_preparation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['status','continuous_duration_s','native_rows','driver_rows','initial_SOC_provisional_percent','initial_battery_temperature_C','initial_environment_temperature_C','native_distance_km','resampling_distance_difference_percent']},ensure_ascii=False,indent=2))
