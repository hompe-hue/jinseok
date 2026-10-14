"""Evaluate one genuine C3 warm060 implementation export, not final adoption."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
BASE=Path(__file__).resolve().parents[1]
OUT=BASE if (BASE/'manifest.json').exists() else BASE/'runs/unified_BEV_model_20261014/implementation_060'
def col(d,n):
    ks=[k for k in d if (k=='Time' and n=='Time') or k.startswith('In/'+n+' (')];assert len(ks)==1,(n,ks)
    return d[ks[0]].to_numpy(dtype=float)
def integral(t,x,a,b):
    tt=np.r_[a,t[(t>a)&(t<b)],b];return float(np.trapezoid(np.interp(tt,t,x),tt)/3600)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--exports',type=Path,required=True);a=ap.parse_args();cfg=json.loads((OUT/'manifest.json').read_text());files={}
    for key in ['battery','velocity','generator']:
        opts=list(a.exports.glob(key+'*.csv'));assert len(opts)==1,(key,opts);files[key]=opts[0]
    data={k:pd.read_csv(p,skiprows=[1]) for k,p in files.items()};t=col(data['battery'],'Time')
    assert t[0]==0 and np.all(np.diff(t)>0)
    assert all(np.array_equal(t,col(d,'Time')) and np.isfinite(d.to_numpy(dtype=float)).all() for d in data.values())
    assert np.floor(cfg['end_time_s'])<=t[-1]<=cfg['end_time_s']+1e-6
    assert abs(col(data['battery'],'SoC')[0]-cfg['initial_model_SOC_percent'])<1e-4,'Wrong C3 initial SOC'
    refpath=OUT/'ANL61905060_reference_native.csv';assert hashlib.sha256(refpath.read_bytes()).hexdigest()==cfg['reference_sha256']
    ref=pd.read_csv(refpath);nt=ref.phase_time_s.to_numpy();V=col(data['battery'],'Voltage');I=-col(data['battery'],'Current');P=V*I/1000
    actual=col(data['velocity'],'Actual Velocity');desired=col(data['velocity'],'Desired Velocity');assert np.max(abs(desired-np.interp(t,nt,ref.speed_kmh)))<.001,'Wrong profile'
    motor=V*col(data['velocity'],'E-Motor Current')/1000;aux=V*col(data['velocity'],'E-Consumer Current')/1000;assert np.max(abs(aux-.4))<1e-5
    modelE=integral(t,P,20,t[-1]);refE=integral(nt,ref.meter_power_kW_discharge_positive,20,t[-1]);energy=100*(modelE/refE-1)
    e=(V-np.interp(t,nt,ref.meter_voltage_V))[t>20];rmse=float(np.sqrt(np.mean(e*e)));bias=float(e.mean());speed=float(np.sqrt(np.mean((actual-desired)**2)))
    distance=100*(integral(t,actual,0,t[-1])/integral(nt,ref.speed_kmh,0,t[-1])-1);balance=100*abs(integral(t,P-motor-aux,20,t[-1]))/abs(modelE)
    gen={n:float(np.max(abs(col(data['generator'],n)))) for n in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Desired Engine Speed','Fuel Massflow','Power Generator','Power ICE']}
    checks=dict(energy=abs(energy)<=5,voltage_RMSE=rmse<=2,voltage_bias=abs(bias)<=1,speed_RMSE=speed<=1,distance=abs(distance)<=.5,DC_balance=balance<=1,generator_OFF=all(x<1e-8 for x in gen.values()))
    result=dict(candidate='C3',test='61905060',role='implementation/training check',energy_error_percent=energy,voltage_RMSE_V=rmse,voltage_bias_V=bias,speed_RMSE_kmh=speed,distance_error_percent=distance,integrated_DC_balance_percent=balance,checks=checks,all_implementation_metrics_pass=all(checks.values()),final_BEV_model_adopted=False,independent_validation=False,low_SOC_BMS_validated=False,expected_project_sha256=cfg['project_sha256'],CSV_sha256={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in files.items()},actual_runtime_provenance='Retain user saved project and solver log; expected hash alone does not prove run provenance')
    (a.exports/'C3_060_implementation_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
