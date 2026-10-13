"""Compare received Dis80 exports with frozen 45kW run and original ANL reference."""
import hashlib,json,sys,shutil
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/ANL61905060_DIS80_20261013';OUT.mkdir(parents=True,exist_ok=True)
upload=Path(sys.argv[1]);baseline=ROOT/'runs/ANL61905060_20261013'
source={};new={};old={}
for k in ['velocity','battery','generator']:
    p=upload/f'{k}_ANL61905060DIS80.csv';q=OUT/p.name
    if q.exists():assert q.read_bytes()==p.read_bytes()
    else:shutil.copy2(p,q)
    source[k]={'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    new[k]=pd.read_csv(q,skiprows=[1]);old[k]=pd.read_csv(baseline/f'{k}_ANL61905060(1).csv',skiprows=[1])
def col(d,n):
    keys=[k for k in d.columns if k=='Time' and n=='Time' or k.startswith('In/'+n+' (')]
    assert len(keys)==1,(n,keys)
    return d[keys[0]].to_numpy(dtype=float)
t=col(new['velocity'],'Time');assert np.all(np.diff(t)>0)
for runs in [new,old]:
    for k,d in runs.items():
        assert np.array_equal(col(d,'Time'),t)
        assert np.isfinite(d.to_numpy(dtype=float)).all()
refpath=ROOT/'independent_tests_20261013/ANL61905060/reference_native.csv';ref=pd.read_csv(refpath)
nt=ref.phase_time_s.to_numpy();assert np.all(np.diff(nt)>0) and np.isfinite(ref.to_numpy(dtype=float)).all()
assert t[0]>=nt[0] and t[-1]<=nt[-1]
cp=json.loads((ROOT/'independent_tests_20261013/ANL61905060/checkpoint.json').read_text())
assert hashlib.sha256(refpath.read_bytes()).hexdigest()==cp['sha256']['reference_native.csv']
driver=pd.read_csv(ROOT/'independent_tests_20261013/ANL61905060/driver_1s.csv')
def integral(x,tt=t,lo=20,hi=3150):
    assert tt[0]<=lo<hi<=tt[-1]
    z=np.r_[lo,tt[(tt>lo)&(tt<hi)],hi]
    return float(np.trapezoid(np.interp(z,tt,x),z)/3600)
def metric(e):return dict(RMSE=float(np.sqrt(np.mean(e*e))),bias=float(np.mean(e)),MAE=float(np.mean(abs(e))),max_abs=float(abs(e).max()))
def stats(x):return dict(first=float(x[0]),last=float(x[-1]),min=float(x.min()),max=float(x.max()))
vr=np.interp(t,nt,ref.meter_voltage_V);ir=np.interp(t,nt,ref.meter_current_A_discharge_positive);rp=np.interp(t,nt,ref.meter_power_kW_discharge_positive)
actualref=np.interp(t,nt,ref.speed_kmh);mask=t>20
refenergy=integral(ref.meter_power_kW_discharge_positive.to_numpy(),nt)
def evaluate(runs,label):
    v=col(runs['battery'],'Voltage');i=-col(runs['battery'],'Current');p=v*i/1000
    actual=col(runs['velocity'],'Actual Velocity');desired=col(runs['velocity'],'Desired Velocity');err=actual-desired
    motor=col(runs['velocity'],'E-Motor Current')*v/1000;aux=col(runs['velocity'],'E-Consumer Current')*v/1000
    energy=integral(p);gross=integral(np.maximum(p,0));recovered=-integral(np.minimum(p,0))
    voltage=metric((v-vr)[mask]);current=metric((i-ir)[mask]);enerr=(energy/refenergy-1)*100
    gen={n:stats(col(runs['generator'],n)) for n in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Desired Engine Speed','Fuel Massflow','Power Generator','Power ICE']}
    off=all(max(abs(d['min']),abs(d['max']))<1e-8 for d in gen.values())
    d=dict(label=label,rows=len(t),export_window_s=[float(t[0]),float(t[-1])],energy_window_s=[20,3150],VI_metric_window_s=[21,3150],
        initial_SOC_percent=float(col(runs['battery'],'SoC')[0]),profile_error_max_kmh=float(abs(desired-actualref).max()),
        desired_matches_other_run_max_kmh=float(abs(desired-col(old['velocity'],'Desired Velocity')).max()),
        initial_SOC_matches=abs(col(runs['battery'],'SoC')[0]-cp['initial_SOC_model_percent'])<1e-5,
        tracking=metric(err),tracking_max_error_time_s=float(t[np.argmax(abs(err))]),
        actual_distance_km=integral(actual,lo=0),desired_distance_km=integral(desired,lo=0),reported_distance_km=float(col(runs['velocity'],'Distance')[-1]),
        distance_error_percent=(integral(actual,lo=0)/integral(desired,lo=0)-1)*100,
        voltage=voltage,current=current,model_net_kWh=energy,reference_net_kWh=refenergy,energy_error_percent=enerr,
        model_gross_discharge_kWh=gross,model_gross_recovered_kWh=recovered,
        power_kW=stats(p),SOC_percent=stats(col(runs['battery'],'SoC')),aux_HV_kW=stats(aux),
        battery_power_minus_VI_max_abs_kW=float(abs(p+col(runs['battery'],'Power')).max()),
        battery_minus_motorDC_minus_aux_max_abs_kW=float(abs(p-motor-aux).max()),
        motor_mech_net_kWh=integral(col(runs['velocity'],'E-Motor Power Mech.')),motor_DC_net_kWh=integral(motor),aux_HV_net_kWh=integral(aux),
        samples_near45kW=int((abs(p-45)<.25).sum()),samples_near80kW=int((abs(p-80)<.25).sum()),
        measured_above45_speed_deficit_gt1kmh=int(((rp>45)&(err<-1)).sum()),
        generator_off=off,generator=gen,
        proposed_targets=dict(voltage_RMSE_met=voltage['RMSE']<=2,voltage_bias_met=abs(voltage['bias'])<=1,energy_met=abs(enerr)<=5))
    aligned=pd.DataFrame(dict(time_s=t,actual_kmh=actual,desired_kmh=desired,tracking_error_kmh=err,model_voltage_V=v,reference_voltage_V=vr,model_discharge_current_A=i,reference_discharge_current_A=ir,model_DC_kW=p,reference_meter_DC_kW=rp,motor_DC_kW=motor,aux_HV_kW=aux))
    return d,aligned
a,oa=evaluate(old,'45kW baseline');b,na=evaluate(new,'DIS80 received diagnostic')
checks=dict(baseline_energy_matches_previous=abs(a['model_net_kWh']-11.286364301456787)<1e-9,
    initial_SOC_matches=b['initial_SOC_matches'],profile_matches=b['profile_error_max_kmh']<1e-5,
    generator_off=b['generator_off'],aux_0p4kW=abs(b['aux_HV_kW']['min']-.4)<1e-5 and abs(b['aux_HV_kW']['max']-.4)<1e-5,
    VI_identity=b['battery_power_minus_VI_max_abs_kW']<1e-8,DC_identity=b['battery_minus_motorDC_minus_aux_max_abs_kW']<1e-5)
assert all(checks.values()),checks
delta={k:b[k]-a[k] for k in ['model_net_kWh','energy_error_percent','model_gross_discharge_kWh','model_gross_recovered_kWh','motor_mech_net_kWh','motor_DC_net_kWh','aux_HV_net_kWh']}
delta['tracking_RMSE_kmh']=b['tracking']['RMSE']-a['tracking']['RMSE'];delta['voltage_RMSE_V']=b['voltage']['RMSE']-a['voltage']['RMSE']
subset=(rp>45)&(oa.tracking_error_kmh.to_numpy()<-1)
events=pd.DataFrame(dict(time_s=t[subset],reference_DC_kW=rp[subset],baseline_speed_error_kmh=oa.tracking_error_kmh.to_numpy()[subset],dis80_speed_error_kmh=na.tracking_error_kmh.to_numpy()[subset],baseline_DC_kW=oa.model_DC_kW.to_numpy()[subset],dis80_DC_kW=na.model_DC_kW.to_numpy()[subset]))
events.to_csv(OUT/'original_limited_events.csv',index=False)
na['baseline_DC_kW']=oa.model_DC_kW;na['baseline_speed_error_kmh']=oa.tracking_error_kmh;na.to_csv(OUT/'aligned_comparison.csv',index=False)
report=dict(new_source_files=source,reference_sha256=hashlib.sha256(refpath.read_bytes()).hexdigest(),baseline=a,diagnostic=b,delta_DIS80_minus_baseline=delta,checks=checks,
    unexported_tail_s=float(nt[-1]-t[-1]),temperature_confirmation='No battery/environment temperature channels in CSV; not independently confirmed.',
    settings_confirmation='User-reported Dis80 change; export has no BMS commanded/allowed power trace and no current project. Changed output cannot prove all other saved parameters stayed identical.',
    scope='Same-test single-setting diagnostic, not independently identified Bolt BMS map or final held-out validation; existing research proposal thresholds are not certification criteria.')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item())+'\n')
summary=pd.DataFrame([{'run':d['label'],'tracking_RMSE_kmh':d['tracking']['RMSE'],'voltage_RMSE_V':d['voltage']['RMSE'],'voltage_bias_V':d['voltage']['bias'],'DC_net_kWh':d['model_net_kWh'],'reference_kWh':d['reference_net_kWh'],'energy_error_percent':d['energy_error_percent'],'peak_discharge_kW':d['power_kW']['max']} for d in [a,b]])
summary.to_csv(OUT/'comparison_metrics.csv',index=False)
print(summary.to_string(index=False));print(json.dumps(delta,indent=2));print('Checks',checks)
