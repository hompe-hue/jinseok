"""Evaluate genuine common-limit exports; no frozen-demand result substitutes for this."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
def column(d,name):
    k=[k for k in d if (name=='Time' and k=='Time') or k.startswith('In/'+name+' (')];assert len(k)==1,(name,k)
    return d[k[0]].to_numpy(float)
def integral(t,y,a,b):
    tt=np.r_[a,t[(t>a)&(t<b)],b];return float(np.trapezoid(np.interp(tt,t,y),tt)/3600)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--test',choices=['61905060','61905058','61905059','61905066','61905067'],required=True);ap.add_argument('--exports',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.package/'manifest.json').read_text());case=next(c for c in manifest['projects'] if c['test']==a.test)
    files={}
    for name in ['battery','velocity','generator']:
        found=list(a.exports.glob(name+'*.csv'));assert len(found)==1,(name,found);files[name]=found[0]
    d={k:pd.read_csv(v,skiprows=[1]) for k,v in files.items()};t=column(d['battery'],'Time')
    assert t[0]==0 and np.all(np.diff(t)>0)
    assert all(np.array_equal(t,column(v,'Time')) and np.isfinite(v.to_numpy(float)).all() for v in d.values())
    assert t[-1]>=np.floor(case['end_time_s']) and t[-1]<=case['end_time_s']+1e-6
    assert abs(column(d['battery'],'SoC')[0]-case['initial_model_SOC_percent'])<1e-4
    ref=pd.read_csv(a.package/f'ANL{a.test}_reference_native.csv');nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'].to_numpy()
    driver=pd.read_csv(a.package/f'ANL{a.test}_driver_1s.csv')
    voltage=column(d['battery'],'Voltage');current=-column(d['battery'],'Current');power=voltage*current/1000
    actual=column(d['velocity'],'Actual Velocity');desired=column(d['velocity'],'Desired Velocity')
    assert np.max(abs(desired-np.interp(t,driver.time_s,driver.speed_kmh)))<.001,'Wrong profile'
    aux=voltage*column(d['velocity'],'E-Consumer Current')/1000;motor=voltage*column(d['velocity'],'E-Motor Current')/1000
    assert np.max(abs(aux-.4))<1e-5
    start=20;stop=min(float(t[-1]),float(nt[-1]));assert stop>start
    modelE=integral(t,power,start,stop);refE=integral(nt,ref.meter_power_kW_discharge_positive,start,stop)
    mask=(t>start)&(t<=stop);error=voltage[mask]-np.interp(t[mask],nt,ref.meter_voltage_V)
    values=dict(energy_error_percent=100*(modelE/refE-1),voltage_RMSE_V=float(np.sqrt(np.mean(error**2))),voltage_bias_V=float(error.mean()),speed_RMSE_kmh=float(np.sqrt(np.mean((actual-desired)**2))),distance_error_percent=100*(integral(t,actual,0,stop)/integral(nt,ref.speed_kmh,0,stop)-1),DC_balance_percent=100*abs(integral(t,power-motor-aux,start,stop))/abs(modelE))
    gen={n:float(np.max(abs(column(d['generator'],n)))) for n in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Desired Engine Speed','Fuel Massflow','Power Generator','Power ICE']}
    checks={k:abs(v)<=bound for (k,v),bound in zip(values.items(),[5,2,1,1,.5,1])};checks['generator_OFF']=all(v<1e-8 for v in gen.values())
    result=dict(test=a.test,status='ACTUAL_USER_EXPORT_EVALUATED',comparison_window_s=[start,stop],metrics=values,checks=checks,all_research_gates_pass=all(checks.values()),final_model_adopted=False,independent_validation=False,OEM_BMS_identified=False,lowSOC_pulse_power_validated=False,expected_project_sha256=case['sha256'],CSV_sha256={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in files.items()},SOC_min_percent=float(column(d['battery'],'SoC').min()),voltage_min_V=float(voltage.min()),voltage_max_V=float(voltage.max()),provenance='Export consistency is checked; retain actual saved project and solver log to establish runtime provenance.')
    (a.exports/f'C3_limits_{a.test}_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
