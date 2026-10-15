"""Development-only frozen-trajectory sensitivity. No project is changed here.
EDU subtraction is an effective overlap correction, not physical motor-loss identification.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1];U=ROOT/'runs/unified_BEV_model_20261014';OUT=U/'diagnostic_067_end9500_20261015/actual'
def col(d,n):return d[[k for k in d if k.startswith('In/'+n+' (')][0]].to_numpy(float)
def main():
    u=np.loadtxt(U/'diagnostic_067_end9500_20261015/Unified_Candidate_Cell_OCV_25C.dat',skiprows=2)
    r=np.loadtxt(U/'diagnostic_067_end9500_20261015/Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2)
    cfg=json.loads((U/'development_screen.json').read_text());cap=cfg['capacity_Ah']
    nodes=pd.read_csv(ROOT/'runs/C2_battery_common_20261014/inputs/C1_EDU_Q1_loss_nodes.csv');q4=pd.read_csv(ROOT/'runs/C2_battery_common_20261014/inputs/C1_EDU_Q4_loss_nodes.csv')
    zero=nodes[nodes.torque_Nm==0].sort_values('rpm');edge=q4.torque_Nm.max()
    beta=np.repeat([0,.05,.1,.12,.14,.15,.16,.17],5);rg=np.tile([1,1.05,1.1,1.15,1.2],8);results=[]
    for test in ['61905060','61905061','61905066','61905058','61905059','61905067']:
        folder=ROOT/f'runs/C2_battery_common_20261014/actual_results/{test}/received';source_boundary='Existing C2 shaft/control trajectory, not rerun C3'
        if test=='61905058':folder=Path('/workspace/scratch/a5204a7b57f4/private/END9500_analysis_20261015/058');source_boundary='Actual C3 common-limit058 trajectory'
        if test=='61905067':folder=OUT;source_boundary='Actual C3 diagnostic0-9500s trajectory; no tail prediction'
        b=pd.read_csv(next(folder.glob('battery*.csv')),skiprows=[1]);v=pd.read_csv(next(folder.glob('velocity*.csv')),skiprows=[1]);t=b.Time.to_numpy();assert np.all(np.diff(t)==1)
        if test=='61905067':ref=pd.read_csv(U/'diagnostic_067_end9500_20261015/ANL61905067_reference_native.csv')
        else:ref=pd.read_csv(ROOT/f'runs/C2_battery_common_20261014/references/ANL{test}_reference_native.csv')
        nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'].to_numpy();rv=np.interp(t,nt,ref.meter_voltage_V)
        w=col(v,'E-Motor Speed');q=col(v,'E-Motor Torque');shaft=col(v,'E-Motor Power Mech.');vol=col(b,'Voltage');p=-col(b,'Current')*vol/1000;em=col(v,'E-Motor Current')*vol/1000
        multi=np.where(q>=0,1,np.where(q<=edge,0,1-q/edge));basis=np.interp(w,zero.rpm,zero.original_loss_kW)*np.clip(w/250,0,1)*multi;basis[(abs(em)<1e-8)&(abs(shaft)<1e-8)]=0
        pp=p[:,None]-basis[:,None]*beta[None,:]
        # Preserve the vehicle terminal regen cap even in this frozen sensitivity.
        # Voltage-based charge acceptance and changed braking/driver dynamics are NOT rerun.
        pp=np.maximum(pp,-40)
        rest=(nt<=5)&(abs(ref.meter_current_A_discharge_positive.to_numpy())<3);assert rest.any()
        v0=float(np.median(ref.meter_voltage_V[rest]));i0=float(np.median(ref.meter_current_A_discharge_positive[rest]))
        s=np.array([brentq(lambda s:96*np.interp(s,u[:,0],u[:,1])-i0*32*np.interp(s/100,r[:,0],r[:,1])*g-v0,0,100) for g in rg]);S=np.empty_like(pp);S[0]=s
        def rate(ss,Power):
            Uv=96*np.interp(ss,u[:,0],u[:,1]);R=32*np.interp(ss/100,r[:,0],r[:,1])*rg;disc=Uv**2-4*R*Power*1000;assert np.all(disc>0)
            return -100*2*Power*1000/(Uv+np.sqrt(disc))/cap/3600
        for k in range(len(t)-1):
            p0=pp[k];p1=pp[k+1];pm=(p0+p1)/2;a=rate(s,p0);bb=rate(s+a/2,pm);c=rate(s+bb/2,pm);d=rate(s+c,p1);s=s+(a+2*bb+2*c+d)/6;S[k+1]=s
        VU=96*np.interp(S,u[:,0],u[:,1]);R=32*np.interp(S/100,r[:,0],r[:,1])*rg;I=2*pp*1000/(VU+np.sqrt(VU**2-4*R*pp*1000));VV=VU-I*R;mask=t>20;err=VV[mask]-rv[mask,None]
        rt=np.r_[20,nt[(nt>20)&(nt<t[-1])],t[-1]];refE=float(np.trapezoid(np.interp(rt,nt,ref.meter_power_kW_discharge_positive),rt)/3600)
        energy=100*(np.trapezoid(pp[t>=20],t[t>=20],axis=0)/3600/refE-1);rms=np.sqrt(np.mean(err**2,axis=0));bias=np.mean(err,axis=0)
        for k in range(len(beta)):
            results.append(dict(test=test,delta_beta=float(beta[k]),R_scale=float(rg[k]),energy_error_percent=float(energy[k]),voltage_RMSE_V=float(rms[k]),voltage_bias_V=float(bias[k]),final_SOC_percent=float(S[-1,k]),frozen_screen_gates_pass=bool(abs(energy[k])<=5 and rms[k]<=2 and abs(bias[k])<=1 and S[:,k].min()>=0 and S[:,k].max()<=100),boundary=source_boundary))
    d=pd.DataFrame(results);d.to_csv(OUT/'common_residual_sensitivity.csv',index=False)
    candidates=[]
    for (db,rr),g in d.groupby(['delta_beta','R_scale']):
        if g.frozen_screen_gates_pass.all():candidates.append(dict(delta_beta=float(db),R_scale=float(rr),all_six_frozen_gates_pass=True,full067_forecast_or_validation=False))
    report=dict(status='MOTORING_ONLY_SENSITIVITY_NO_PROJECT_CHANGED',capacity_and_OCV_unchanged=True,Q4_regeneration_nodes_unchanged=True,new_CRUISE_runs=0,grid_size=len(beta),feasible_frozen_candidates=candidates,physical_loss_overlap_identified=False,limitations=['Changed motor control/braking and voltage-charge acceptance not rerun','067 ends9500; no full-length completion predicted','This grid does not identify whether TargetABC mechanical resistance or EDU/aux split causes the real residual'])
    (OUT/'common_residual_sensitivity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
