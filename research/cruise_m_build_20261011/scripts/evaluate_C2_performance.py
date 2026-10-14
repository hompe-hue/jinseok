"""Evaluate actual exported CSVs; never synthesize CRUISE M results."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
BASE=Path(__file__).resolve().parents[1]
OUT=BASE if (BASE/'test_manifest.json').exists() else BASE/'runs/C2_performance_extension_20261014'
def col(d,n):
    matches=[k for k in d if (k=='Time' and n=='Time') or k.startswith('In/'+n+' (') or k==n]
    assert len(matches)==1,(n,matches)
    return d[matches[0]].to_numpy(dtype=float)
def read(p):
    d=pd.read_csv(p,skiprows=[1]);t=col(d,'Time')
    assert np.isfinite(d.to_numpy(dtype=float)).all() and t[0]==0 and np.all(np.diff(t)>0)
    return d
def crossing(t,v,target):
    k=np.flatnonzero(v>=target)
    if not len(k):return None
    j=k[0]
    return float(t[j]) if j==0 else float(t[j-1]+(target-v[j-1])*(t[j]-t[j-1])/(v[j]-v[j-1]))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',required=True,choices=['ACC','UDDS','HWFET']);ap.add_argument('--exports',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--initial-soc',type=float,required=True)
    a=ap.parse_args();paths={n:a.exports/(n+'.csv') for n in ['battery','velocity','generator']};data={k:read(v) for k,v in paths.items()}
    manifest=json.loads((OUT/'test_manifest.json').read_text())
    case=next(x for x in manifest['cases'] if x['mode']==a.mode and x['initial_SOC_percent']==a.initial_soc)
    t=col(data['battery'],'Time');assert all(np.array_equal(t,col(x,'Time')) for x in data.values())
    soc=col(data['battery'],'SoC');v=col(data['battery'],'Voltage');speed=col(data['velocity'],'Actual Velocity')
    assert abs(soc[0]-a.initial_soc)<1e-4,'Wrong initial SOC'
    gen={n:float(np.max(abs(col(data['generator'],n)))) for n in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Desired Engine Speed','Fuel Massflow','Power Generator','Power ICE']}
    assert all(x<1e-8 for x in gen.values()),'Generator/engine must be OFF'
    power=-v*col(data['battery'],'Current')/1000
    report=dict(mode=a.mode,initial_SOC_percent=a.initial_soc,generator_OFF=True,maximum_output_step_s=float(np.max(np.diff(t))),maximum_DC_power_kW=float(np.max(power)),CSV_sha256={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()},expected_project_sha256=case['sha256'],CRUISE_run_provenance='User export; retain project hash and solver log separately',certification_reproduction=False)
    if a.mode=='ACC':
        assert np.max(np.diff(t))<=.05+1e-9,'Acceleration needs <=0.05s export, preferably0.01s'
        # Timing from solver launch at0; no 1-foot rollout subtraction.
        assert speed[0]<.1
        t60=crossing(t,speed,96.56064);t100=crossing(t,speed,100)
        report.update(time_0_to_60mph_s=t60,time_0_to_100kmh_s=t100,GM_0_to_60mph_s=6.5,GM_difference_s=None if t60 is None else t60-6.5,comparison_is_contextual_not_acceptance_gate=True,requires_user_full_pedal_trace_confirmation=True)
    else:
        desired=col(data['velocity'],'Desired Velocity');err=desired-speed
        assert np.max(np.diff(t))<=1.05,'Range export must have <=1s nominal sampling'
        profile=pd.read_csv(OUT/'profiles'/f'EPA_{a.mode}_repeat60.csv')
        assert t[-1]<=profile.time_s.iloc[-1]+1e-6
        expected=np.interp(t,profile.time_s,profile.speed_kmh)
        assert np.max(abs(desired-expected))<.001,'Wrong EPA cycle/profile'
        # Research diagnostic only: persistently cannot follow >10km/h demand.
        mask=(desired>10)&(err>3.218688);start=None;failure=None
        for j,ok in enumerate(mask):
            if ok:
                if start is None:start=j
                if t[j]-t[start]>=10:failure=float(t[start]);break
            else:start=None
        ss=np.flatnonzero(soc<=20);s20=float(t[ss[0]]) if len(ss) else None
        candidates=[(x,n) for x,n in [(failure,'10s sustained speed shortfall diagnostic'),(s20,'C2 model SOC20 diagnostic-map floor')] if x is not None]
        if candidates:end,reason=min(candidates)
        else:end,reason=float(t[-1]),'export ended; range is right-censored lower bound'
        keep=t<end;tt=np.r_[t[keep],end];sv=np.interp(tt,t,speed);pp=np.interp(tt,t,power)
        dist=float(np.trapezoid(sv/3600,tt));energy=float(np.trapezoid(pp/3600,tt))
        official={'UDDS':255*1.609344,'HWFET':217*1.609344}[a.mode]
        report.update(endpoint_s=end,endpoint_reason=reason,model_window_distance_km=dist,range_is_censored=not candidates,net_DC_energy_kWh=energy,endpoint_SOC_percent=float(np.interp(end,t,soc)),tracking_RMSE_kmh=float(np.sqrt(np.mean((desired[t<=end]-speed[t<=end])**2))),EPA_cycle_adjusted_reference_km=official,illustrative_adjustment_factor=.7,illustrative_adjusted_model_window_distance_km=.7*dist,illustrative_difference_percent=100*(.7*dist/official-1),EPA_Bolt_vehicle_specific_adjustment_confirmed=False,whole_SOC_range_representativeness_unverified=True)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
