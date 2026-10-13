from pathlib import Path
import csv,json,sys,hashlib
import numpy as np
from nptdms import TdmsFile
root=Path(__file__).resolve().parents[1];run=root/'runs/ANL61905060_20261013';out=run/'energy_diagnosis';out.mkdir(exist_ok=True)
src=Path(sys.argv[1]);g=TdmsFile.read(src).groups()[0];s=int(g.properties['Phase_1_Phase_Start_Fill_Index'])-1;e=int(g.properties['Phase_1_Phase_Stop_Fill_Index'])
def c(n):return np.asarray(g[n][s:e],float)
nt=c('Time_H0');origin=nt[0];nt=nt-origin;ct=c('Time_3')-origin
ns=c('Motor_1_speed_DMCM1');nq=c('Motor_1_torque_DMCM1');nm=ns*nq*2*np.pi/60/1000;npower=c('Batt_Power_Hioki_P1');lv=c('DCDC_Out_Power_Hioki_P3')/1000
rows=list(csv.reader((run/'velocity_ANL61905060(1).csv').open()));h=rows[0];a=np.array(rows[2:],float)
def m(n):return a[:,next(i for i,k in enumerate(h) if k=='Time' and n=='Time' or k.startswith('In/'+n+' ('))]
t=m('Time');mm=m('E-Motor Power Mech.');ms=m('E-Motor Speed');mq=m('E-Motor Torque')
br=list(csv.reader((run/'battery_ANL61905060(1).csv').open()));ba=np.array(br[2:],float);bh=br[0]
def bc(n):return ba[:,next(i for i,k in enumerate(bh) if k.startswith('In/'+n+' ('))]
mv=bc('Voltage');mp=-bc('Current')*mv/1000;aux=m('E-Consumer Current')*mv/1000;mdc=m('E-Motor Current')*mv/1000
trap=getattr(np,'trapezoid',np.trapz)
def inte(tt,x,lo=20,hi=3150):
 assert np.all(np.isfinite(x)) and np.all(np.diff(tt)>0)
 z=np.r_[lo,tt[(tt>lo)&(tt<hi)],hi];return float(trap(np.interp(z,tt,x),z)/3600)
def sums(tt,p):return {'net_kWh':inte(tt,p),'positive_kWh':inte(tt,np.maximum(p,0)),'negative_recovery_kWh':-inte(tt,np.minimum(p,0))}
# CAN records are native held observations; retain last observation per duplicate timestamp.
uniq=np.r_[np.diff(ct)>0,True];ct=ct[uniq];nm=nm[uniq];ns=ns[uniq];nq=nq[uniq]
assert ct[0]<=20 and ct[-1]>=3150
r={'window_s':[20,3150],'tdms_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'native_motor_mechanical_CAN':sums(ct,nm),'model_motor_mechanical':sums(t,mm),'native_battery_DC':sums(nt,npower),'model_battery_DC':sums(t,mp),'model_motor_DC':sums(t,mdc),'model_aux_HV_kWh':inte(t,aux),'reference_LV_output_kWh':inte(nt,lv),'model_battery_minus_motorDC_minus_aux_max_kW':float(max(abs(mp-mdc-aux))),'model_mechanical_power_minus_speed_torque_max_kW':float(max(abs(mm-ms*mq*2*np.pi/60/1000))),'mechanical_CAN_caution':'Reported torque/speed product is a diagnostic CAN estimate, not independently calibrated shaft-power metrology. Its time clock is kept separate from meter clock; no lag fit. Negative torque at stationary speed contributes zero shaft power. Model output boundary must match before causal efficiency claim.','next':'Review effective motoring conversion and map boundary with current power-loss tables; no coefficient/aux retuning or 61905061 progression yet'}
lines=(root/'inputs/Bolt_EDU_Loss_400V_AVL_RegularMap.dat').read_text().splitlines()
qa=np.array(list(map(float,lines[5].split())));wa=np.array(list(map(float,lines[8].split())));loss=np.array([list(map(float,x.split())) for x in lines[11:]])
def maploss(speed,torque):
 w=np.abs(speed)*2*np.pi/60; q=torque
 wi=np.clip(np.searchsorted(wa,w)-1,0,len(wa)-2);qi=np.clip(np.searchsorted(qa,q)-1,0,len(qa)-2)
 wf=np.clip((w-wa[wi])/(wa[wi+1]-wa[wi]),0,1);qf=np.clip((q-qa[qi])/(qa[qi+1]-qa[qi]),0,1)
 return ((1-wf)*(1-qf)*loss[qi,wi]+wf*(1-qf)*loss[qi,wi+1]+(1-wf)*qf*loss[qi+1,wi]+wf*qf*loss[qi+1,wi+1])/1000
ml=maploss(ms,mq);nl=maploss(ns,nq)
r['imported_map_diagnostic']={'map_file':'inputs/Bolt_EDU_Loss_400V_AVL_RegularMap.dat','model_DC_minus_shaft_net_loss_kWh':inte(t,mdc-mm),'bilinear_map_loss_at_model_points_kWh':inte(t,ml),'model_DC_minus_shaft_vs_map_max_abs_kW':float(max(abs(mdc-mm-ml))),'model_DC_minus_shaft_vs_map_RMSE_kW':float(np.sqrt(np.mean((mdc-mm-ml)**2))),'bilinear_map_loss_at_native_CAN_points_kWh':inte(ct,nl),'reference_battery_minus_CANshaft_net_kWh':inte(nt,npower)-inte(ct,nm),'limitation':'A standalone bilinear evaluation assumes current interpolation and boundary. Reference residual includes HV accessories and CAN power uncertainty; do not label it measured EDU loss.'}
with (out/'mechanical_electrical_diagnostics.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['time_s','model_shaft_kW','CAN_shaft_estimate_kW','model_motorDC_kW','reference_batteryDC_kW','model_auxHV_kW','reference_LV_output_kW']);w.writerows(zip(t,mm,np.interp(t,ct,nm),mdc,np.interp(t,nt,npower),aux,np.interp(t,nt,lv)))
(out/'mechanical_electrical_decomposition.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False))
