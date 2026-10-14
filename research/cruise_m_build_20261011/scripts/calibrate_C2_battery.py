"""C2 common warm effective-battery feasibility. Training only 060/061/066.
No independent-validation claim; no 058/059 outcomes read.
"""
import json, argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.optimize import minimize, LinearConstraint, brentq
ROOT=Path(__file__).resolve().parents[1]; C1=ROOT/'runs/final_candidate_C1_20261014'; OUT=ROOT/'runs/C2_battery_common_20261014'
def metrics(e): return dict(bias_V=float(e.mean()),RMSE_V=float(np.sqrt(np.mean(e**2))))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--exports',type=Path,required=True);a=ap.parse_args()
 u=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2); r=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
 knots=np.array([0,50,60,70,85,93,100]); B=np.stack([np.interp(u[:,0],knots,np.eye(7)[j]) for j in [2,3,4,5]],axis=1)
 data={}
 for test in ['61905060','61905061','61905066']:
  ref=pd.read_csv(C1/f'references/ANL{test}_reference_native.csv'); b=pd.read_csv(a.exports/f'battery_C1_CAL_{test}.csv',skiprows=[1]);t=b.Time.to_numpy();nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'].to_numpy()
  ir=np.interp(t,nt,ref.meter_current_A_discharge_positive);vr=np.interp(t,nt,ref.meter_voltage_V);ah=np.interp(t,nt,cumulative_trapezoid(ref.meter_current_A_discharge_positive,nt,initial=0))/3600
  get=lambda n:b[[c for c in b if c.startswith('In/'+n+' (')][0]].to_numpy()
  data[test]=(t,ir,vr,ah,float(ref.meter_current_A_discharge_positive.iloc[0]),float(ref.meter_voltage_V.iloc[0]),-get('Current')*get('Voltage')/1000)
 def maps(x):return 96*u[:,1]+B@x[:4],32*r[:,1]*x[4]
 def initial(x,d):
  uu,rr=maps(x);return brentq(lambda s:np.interp(s,u[:,0],uu)-d[4]*np.interp(s/100,r[:,0],rr)-d[5],0,100)
 def replay(x,d):
  uu,rr=maps(x);s=initial(x,d)-d[3]/(168*x[5])*100;return np.interp(s,u[:,0],uu)-d[1]*np.interp(s/100,r[:,0],rr)
 def objective(x):
  val=sum(np.mean((replay(x,d)-d[2])[d[0]>20]**2) for d in data.values())/3
  return val+.03*(np.sum((x[:4]/4.8)**2)+(x[4]-1)**2+((x[5]-1)/.05)**2)/6
 constraint=LinearConstraint(np.column_stack([np.diff(B,axis=0),np.zeros((100,2))]),1e-5-np.diff(96*u[:,1]),np.inf)
 x0=np.array([-4.8,-.9465037712521921,0,0,1.13749552839391,1])
 # Fixed optimizer settings; no fresh-holdout-based selection.
 fit=minimize(objective,x0,method='SLSQP',bounds=[(-4.8,4.8)]*4+[(.5,2),(.95,1.05)],constraints=[constraint],options={'ftol':1e-10,'maxiter':500})
 x=fit.x;uu,rr=maps(x);results={}
 for test,d in data.items():
  t,ir,vr,ah,ii,vv,power=d;start=initial(x,d)
  def current(tt,s):
   U=np.interp(s,u[:,0],uu);R=np.interp(s/100,r[:,0],rr);P=np.interp(tt,t,power)*1000;disc=U*U-4*R*P
   if disc<0:raise ValueError('Frozen demand exceeds voltage-limited power')
   return 2*P/(U+np.sqrt(disc))
  sol=solve_ivp(lambda tt,ss:[-current(tt,ss[0])/(168*x[5])*100/3600],(t[0],t[-1]),[start],t_eval=t,max_step=.5,rtol=1e-8,atol=1e-9)
  assert sol.success
  s=sol.y[0];ic=np.array([current(tt,ss) for tt,ss in zip(t,s)]);vp=np.interp(s,u[:,0],uu)-ic*np.interp(s/100,r[:,0],rr);mask=t>20
  results[test]={'initial_SOC_percent':start,'measured_current_training':metrics((replay(x,d)-vr)[mask]),'frozen_C1_power_screen':metrics((vp-vr)[mask]),'screen_is_CRUISE':False}
  pd.DataFrame(dict(time_s=t,reference_voltage_V=vr,C2_measured_current_voltage_V=replay(x,d),C2_frozen_power_voltage_V=vp,C2_frozen_power_SOC_percent=s)).to_csv(OUT/f'C2_training_{test}.csv',index=False)
 gate=bool(fit.success and np.all(np.diff(uu)>0) and all(abs(z['frozen_C1_power_screen']['bias_V'])<=1 and z['frozen_C1_power_screen']['RMSE_V']<=2 for z in results.values()))
 result={'status':'FEASIBLE_SCREEN_PENDING_ACTUAL_CRUISE' if gate else 'SCREEN_FAILED','optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'objective':float(fit.fun),'regularization_V2':.03,'OCV_pack_corrections_V':dict(zip(['60','70','85','93'],map(float,x[:4]))),'R_gain':float(x[4]),'capacity_gain':float(x[5]),'cell_capacity_Ah':float(56*x[5]),'pack_capacity_Ah':float(168*x[5]),'minimum_OCV_pack_increment_V':float(np.min(np.diff(uu))),'screen_gate_met':gate,'training':results,'independent_validation_complete':False,'fresh_holdout_outcomes_read':False,'scope':'Warm effective vehicle battery calibration, not unique physical cell identification;066 is training for C2. C1 FAIL preserved.'}
 (OUT/'feasibility.json').write_text(json.dumps(result,indent=2)+'\n')
 np.savetxt(OUT/'C2_Cell_OCV_25C.dat',np.column_stack([u[:,0],uu/96]),header='SoC Voltage\n% V',comments='')
 np.savetxt(OUT/'C2_Cell_Resistance_25C.dat',np.column_stack([r[:,0],rr/32]),header='SoC Resistance\n- Ohm',comments='')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
