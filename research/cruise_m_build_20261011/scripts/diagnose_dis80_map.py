"""Recheck sampled map application and descriptive boundary energy on the DIS80 run."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs/ANL61905060_DIS80_20261013'
v=pd.read_csv(OUT/'velocity_ANL61905060DIS80.csv',skiprows=[1]);b=pd.read_csv(OUT/'battery_ANL61905060DIS80.csv',skiprows=[1])
def c(d,n):return d[[k for k in d if k.startswith('In/'+n+' (')][0]].to_numpy()
n=c(v,'E-Motor Speed');q=c(v,'E-Motor Torque');shaft=c(v,'E-Motor Power Mech.');loss=c(v,'E-Motor Current')*c(b,'Voltage')/1000-shaft
maps={}
for name in ['Q1','Q4']:
    d=pd.read_csv(ROOT/f'runs/project_audit_20261013/embedded_motor_loss_{name}.csv');d.columns=['temp','voltage','rpm','torque','loss']
    z=d.pivot(index='torque',columns='rpm',values='loss').sort_index().sort_index(axis=1)
    maps[name]=(z.index.to_numpy(),z.columns.to_numpy(),RegularGridInterpolator((z.index,z.columns),z.to_numpy(),bounds_error=False,fill_value=np.nan),d)
qa,na,f1,d1=maps['Q1'];q4,n4,f4,d4=maps['Q4'];pred=f1(np.c_[q,abs(n)])
drive=(shaft>.01)&(q>=qa.min())&(q<=qa.max())&(abs(n)>=na.min())&(abs(n)<=na.max());regen=shaft<-.01
inside=regen&(q>=q4.min())&(q<=q4.max())&(abs(n)>=n4.min())&(abs(n)<=n4.max());pred[inside]=f4(np.c_[q[inside],abs(n[inside])])
bridge=regen&(q>q4.max())&(q<0)&(abs(n)>=n4.min())&(abs(n)<=n4.max())
zero=d1.loc[d1.torque==0].sort_values('rpm');edge=d4.loc[d4.torque==q4.max()].sort_values('rpm');alpha=q[bridge]/q4.max()
pred[bridge]=(1-alpha)*np.interp(abs(n[bridge]),zero.rpm,zero.loss)+alpha*np.interp(abs(n[bridge]),edge.rpm,edge.loss)
res={}
for name,mask in [('Q1_interior',drive),('Q4_interior',inside),('low_torque_bridge',bridge)]:
    e=pred[mask]-loss[mask];res[name]={'rows':int(mask.sum()),'RMSE_kW':float(np.sqrt(np.mean(e*e))),'max_abs_kW':float(abs(e).max())};assert abs(e).max()<1e-9
res['uncovered_regenerative_rows']=int((regen&~inside&~bridge).sum());res['scope']='Observed map application, not independent physical EDU validation'
d=json.loads((OUT/'verification.json').read_text());old=json.loads((ROOT/'runs/ANL61905060_20261013/energy_diagnosis/mechanical_electrical_decomposition.json').read_text())
mechref=old['native_motor_mechanical_CAN']['net_kWh'];res['energy_accounting']={}
for label,x in [('baseline',d['baseline']),('dis80',d['diagnostic'])]:
    total=x['model_net_kWh']-x['reference_net_kWh'];mech=x['motor_mech_net_kWh']-mechref
    res['energy_accounting'][label]={'total_difference_kWh':total,'model_minus_CAN_mechanical_candidate_kWh':mech,'remaining_boundary_difference_kWh':total-mech,'model_EDU_DC_minus_output_kWh':x['motor_DC_net_kWh']-x['motor_mech_net_kWh'],'caution':'CAN rotor/EDU equivalent shaft boundary not independently aligned; descriptive accounting, not measured loss decomposition.'}
(OUT/'map_and_energy_diagnostics.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
