"""One common effective battery candidate across warm and full-depletion data.
Development screen only. No CRUISE M run, physical parameter identification,
vehicle energy/acceleration/range PASS, or blind-validation claim.
"""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import minimize,LinearConstraint,brentq
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/unified_BEV_model_20261014';OUT.mkdir(parents=True,exist_ok=True)
C2=ROOT/'runs/C2_battery_common_20261014'
EXT=ROOT/'runs/C2_performance_extension_20261014'
TRAIN=['61905060','61905061','61905066','61905064']
CHECK=['61905058','61905059','61905067']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    u=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
    r=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
    knots=np.array([0,5,10,20,40,50,60,70,85,93,100.])
    basis=np.stack([np.interp(u[:,0],knots,np.eye(len(knots))[j]) for j in range(len(knots))],axis=1)
    all_data={};source=[]
    for test in TRAIN+CHECK:
        if test in ['61905064','61905067']:
            path=EXT/'replay'/f'ANL{test}_frozen_C2_replay.csv';d=pd.read_csv(path)
            t=d.t.to_numpy();i=d.i.to_numpy();v=d.v.to_numpy()
        else:
            path=C2/'references'/f'ANL{test}_reference_native.csv';d=pd.read_csv(path)
            t=d['time_s' if 'time_s' in d else 'phase_time_s'].to_numpy();i=d.meter_current_A_discharge_positive.to_numpy();v=d.meter_voltage_V.to_numpy()
        valid=np.isfinite(t)&np.isfinite(i)&np.isfinite(v)&(v>=200)&(v<=450)&(abs(i)<=1000)
        dt=np.diff(t);interval=valid[:-1]&valid[1:]&(dt>0)&(dt<=2)
        bad=np.flatnonzero(~interval);stop=bad[0]+1 if len(bad) else len(d)
        t=t[:stop];i=i[:stop];v=v[:stop]
        q=cumulative_trapezoid(i,t,initial=0)/3600
        anchor=(t<=5)&(abs(i)<3);assert anchor.sum()>=10
        ii=float(np.median(i[anchor]));vv=float(np.median(v[anchor]))
        # Fit samples from every5s; evaluate all trusted native samples afterwards.
        train_index=np.searchsorted(t,np.arange(25,t[-1],5));train_index=np.unique(np.clip(train_index,0,len(t)-1))
        all_data[test]=dict(t=t,i=i,v=v,q=q,ii=ii,vv=vv,fitidx=train_index)
        source.append(dict(test=test,sha256=sha(path),path=str(path.relative_to(ROOT)),trusted_rows=len(t),role='FIT' if test in TRAIN else 'RECHECK_ALREADY_REVIEWED'))
    def maps(x):return 96*u[:,1]+basis@x[:len(knots)],32*r[:,1]*x[-2]
    def initial(x,d):
        uu,rr=maps(x)
        return brentq(lambda s:np.interp(s,u[:,0],uu)-d['ii']*np.interp(s/100,r[:,0],rr)-d['vv'],0,100)
    def replay(x,d,index=None):
        uu,rr=maps(x);s0=initial(x,d)
        q=d['q'] if index is None else d['q'][index];i=d['i'] if index is None else d['i'][index]
        s=s0-q/x[-1]*100
        pred=np.interp(s,u[:,0],uu)-i*np.interp(s/100,r[:,0],rr)
        return pred,s,s0
    def objective(x):
        total=0
        try:
            for test in TRAIN:
                d=all_data[test];pred,s,s0=replay(x,d,d['fitidx']);e=pred-d['v'][d['fitidx']]
                # Equal per-test mean squared error; long tests do not overwhelm warm tests.
                total+=float(np.mean(e*e)+2*np.mean(e)**2+100*np.mean(np.minimum(s,0)**2)+100*np.mean(np.maximum(s-100,0)**2))
            # Weak, fixed prior on smooth correction and large changes. No check-set selection.
            delta=x[:len(knots)]
            total=total/len(TRAIN)+.01*np.mean((delta/10)**2)+.05*np.mean((np.diff(delta,2)/5)**2)+.02*((x[-2]-1)/.5)**2
            return total
        except ValueError:return 1e9
    lower=np.array([-70,-35,-20]+[-12]*8+[.5,150.])
    upper=np.array([8,12,12]+[12]*8+[2.,210.])
    constraint=LinearConstraint(np.column_stack([np.diff(basis,axis=0),np.zeros((100,2))]),1e-4-np.diff(96*u[:,1]),np.inf)
    attempts=[]
    # Initial settings are fixed before optimizer results, not chosen from CHECK outcomes.
    for capacity in [180.,195.]:
        x0=np.r_[[-35,-10,-4,0,0,0,-4.8,.871641728606408,1.70967005183054,-1.9839731528798132,0],1.0325148990054311,capacity]
        fit=minimize(objective,x0,method='SLSQP',bounds=list(zip(lower,upper)),constraints=[constraint],options={'maxiter':400,'ftol':1e-9})
        attempts.append((fit,float(objective(fit.x))))
        print(json.dumps(dict(initial_capacity_Ah=capacity,success=bool(fit.success),training_objective=float(objective(fit.x)),message=str(fit.message))),flush=True)
    acceptable=[z for z in attempts if z[0].success]
    fit,val=min(acceptable or attempts,key=lambda z:z[1]);x=fit.x;uu,rr=maps(x)
    metrics=[]
    for test,d in all_data.items():
        pred,s,s0=replay(x,d);mask=d['t']>20;e=pred[mask]-d['v'][mask]
        metrics.append(dict(test=test,role='FIT' if test in TRAIN else 'RECHECK_ALREADY_REVIEWED',initial_model_SOC_percent=s0,final_model_SOC_percent=float(s[-1]),voltage_RMSE_V=float(np.sqrt(np.mean(e*e))),voltage_bias_V=float(e.mean()),SOC_range_in_map=bool(s.min()>=0 and s.max()<=100),voltage_screen_thresholds_met=bool(np.sqrt(np.mean(e*e))<=2 and abs(e.mean())<=1)))
        pd.DataFrame(dict(time_s=d['t'],reference_voltage_V=d['v'],candidate_voltage_V=pred,model_SOC_percent=s,measured_current_A=d['i'],net_Ah=d['q'])).to_csv(OUT/f'candidate_replay_{test}.csv',index=False)
    pd.DataFrame(metrics).to_csv(OUT/'development_screen_metrics.csv',index=False)
    np.savetxt(OUT/'Unified_Candidate_Cell_OCV_25C.dat',np.column_stack([u[:,0],uu/96]),header='SoC Voltage\n% V',comments='')
    np.savetxt(OUT/'Unified_Candidate_Cell_Resistance_25C.dat',np.column_stack([r[:,0],rr/32]),header='SoC Resistance\n- Ohm',comments='')
    result=dict(status='DEVELOPMENT_SCREEN_ONLY_NOT_ADOPTED',one_common_parameter_set=True,train_tests=TRAIN,rechecks=CHECK,rechecks_previously_seen=True,no_blind_validation_claim=True,initialization_rule='common first5s |I|<3A median V/I inverse, no manual per-test SOC offset',optimizer_success=bool(fit.success),training_objective=val,training_mean_bias_penalty_weight=2,development_objective_changed_after_first_recheck=True,first_MSE_only_result_preserved='first_MSE_only_development_screen.json',capacity_Ah=float(x[-1]),cell_capacity_Ah=float(x[-1]/3),R_gain=float(x[-2]),OCV_pack_correction_knots_percent=knots.tolist(),OCV_pack_corrections_V=x[:len(knots)].tolist(),monotonic_OCV=bool(np.all(np.diff(uu)>0)),fit_regularization_and_bounds_are_development_assumptions=True,capacity_not_physically_identified=True,BMS_not_modified_or_identified=True,CRUISE_project_created=False,CRUISE_solver_run=False,vehicle_energy_and_performance_not_checked=True,metrics=metrics,sources=source)
    (OUT/'development_screen.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
