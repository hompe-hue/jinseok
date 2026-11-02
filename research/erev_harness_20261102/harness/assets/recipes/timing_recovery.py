"""Timing stress and post-stop voltage recovery; no time correction or RC fit adopted."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
SRC=P/'inputs'
if not SRC.exists():SRC=ROOT.parent/'feedback/research/public_validation_batch_20261016/actual_20261016'
grid=np.arange(101.)
ocv=322.397+1.29836*grid-.0184756*grid**2+.000143235*grid**3
res=.0806969-.000281326*grid+.00000166726*grid**2

def model(t,rt,current,s0):
    q=cumulative_trapezoid(current,rt,initial=0)/3600
    s=s0-100*np.interp(t,rt,q)/180
    assert np.all((s>=0)&(s<=100))
    return np.interp(s,grid,ocv)-np.interp(s,grid,res)*np.interp(t,rt,current)

def main():
    lag_rows=[];summary=[];episodes=[];hashes={}
    windows=P/'stopped_windows_input.csv'
    if not windows.exists():windows=ROOT/'steps/05_battery_identifiability/stopped_low_current_windows.csv'
    win=pd.read_csv(windows)
    for code in ['058','059','060','066']:
        test='61905'+code
        bp=SRC/code/('battery_PUBLIC_'+code+'.csv');rp=SRC/'references'/('ANL'+test+'_reference_native.csv')
        for f in [bp,rp]:hashes[str(f.relative_to(SRC))]=hashlib.sha256(f.read_bytes()).hexdigest()
        b=pd.read_csv(bp,skiprows=[1]);d=pd.read_csv(rp);rt=d.iloc[:,0].to_numpy(float)
        cur=d.meter_current_A_discharge_positive.to_numpy(float);vol=d.meter_voltage_V.to_numpy(float)
        s0=float(b.filter(like='In/SoC (').iloc[0,0]);end=float(b.Time.iloc[-1])
        # Common interior grid keeps samples fixed over all lag candidates.
        x=np.arange(21.,end-1.01,.1)
        di=np.interp(x+.5,rt,cur)-np.interp(x-.5,rt,cur)
        active=abs(di)>=10
        pred=model(x,rt,cur,s0)
        local=[]
        for lag in np.arange(-10,11)/10:
            v=np.interp(x+lag,rt,vol)
            dv=np.interp(x+lag+.5,rt,vol)-np.interp(x+lag-.5,rt,vol)
            corr=float(np.corrcoef(-di[active],dv[active])[0,1])
            row=dict(test=test,voltage_relative_lag_s=float(lag),
                fast_change_correlation=corr,fast_change_samples=int(active.sum()),
                full_interior_voltage_RMSE_V=float(np.sqrt(np.mean((pred-v)**2))),
                full_interior_voltage_bias_V=float(np.mean(pred-v)))
            lag_rows.append(row);local.append(row)
        baseline=next(x for x in local if x['voltage_relative_lag_s']==0)
        bestfast=max(local,key=lambda a:a['fast_change_correlation'])
        bestfull=min(local,key=lambda a:a['full_interior_voltage_RMSE_V'])
        summary.append(dict(test=test,zero_lag_fast_correlation=baseline['fast_change_correlation'],
            best_fast_lag_s=bestfast['voltage_relative_lag_s'],best_fast_correlation=bestfast['fast_change_correlation'],
            zero_lag_voltage_RMSE_V=baseline['full_interior_voltage_RMSE_V'],
            best_full_RMSE_lag_s=bestfull['voltage_relative_lag_s'],
            lowest_RMSE_in_plusminus1s_V=bestfull['full_interior_voltage_RMSE_V'],
            hardware_clock_offset_identified=False,lag_adopted=False))
        for _,w in win[win.test==int(test)].iterrows():
            start,endstop=float(w.start_s),float(w.end_s)
            t=np.arange(start,endstop+1)
            actual=np.interp(t,rt,vol);predstop=model(t,rt,cur,s0)
            early=(t>=start+1)&(t<=start+3);late=t>=endstop-3
            before=np.arange(max(0,start-10),start,.1);before_i=np.interp(before,rt,cur)
            # Fixed summaries only. Short stopped intervals are not OCV/HPPC tests.
            earlyv=float(np.median(actual[early]));latev=float(np.median(actual[late]))
            earlyp=float(np.median(predstop[early]));latep=float(np.median(predstop[late]))
            episodes.append(dict(test=test,start_s=start,end_s=endstop,duration_s=endstop-start,
                preceding10s_mean_current_A=float(np.mean(before_i)),
                preceding10s_high_discharge_samples=int(np.sum(before_i>20)),
                preceding10s_high_charge_samples=int(np.sum(before_i<-20)),
                measured_late_minus_early_V=latev-earlyv,
                Rint_late_minus_early_V=latep-earlyp,
                extra_recovery_change_V=(latev-earlyv)-(latep-earlyp),
                early_voltage_residual_V=earlyp-earlyv,late_voltage_residual_V=latep-latev,
                equilibrium_OCV_verified=False,unique_RC_parameters_identified=False))
    pd.DataFrame(lag_rows).to_csv(P/'lag_stress.csv',index=False)
    pd.DataFrame(summary).to_csv(P/'timing_summary.csv',index=False)
    pd.DataFrame(episodes).to_csv(P/'recovery_episodes.csv',index=False)
    (P/'QA.json').write_text(json.dumps(dict(source_hashes=hashes,
        lag_range_s=[-1,1],lag_step_s=.1,common_interior_mask=True,
        extrapolation_used=False,time_shift_adopted=False,parameter_fit=False,
        new_CRUISE_runs=0,hardware_clock_offset_identified=False),indent=2)+'\n')
    print(pd.DataFrame(summary).round(6).to_string(index=False))
    print(pd.DataFrame(episodes).groupby('test').extra_recovery_change_V.agg(['count','median','min','max']).round(6).to_string())

if __name__=='__main__':main()
