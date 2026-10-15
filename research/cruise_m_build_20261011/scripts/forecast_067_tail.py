"""Forecast only: actual0-9500 frozen power plus a transparent quasi-static tail.
The unused measured-speed tail is an input scenario, not measured CRUISE power.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1];U=ROOT/'runs/unified_BEV_model_20261014';D=U/'diagnostic_067_end9500_20261015';OUT=D/'actual'
def col(d,n):return d[[k for k in d if k.startswith('In/'+n+' (')][0]].to_numpy(float)
def main():
    b=pd.read_csv(OUT/'battery_END9500.csv',skiprows=[1]);v=pd.read_csv(OUT/'velocity_END9500.csv',skiprows=[1]);driver=pd.read_csv(D/'ANL61905067_driver_1s.csv');ref=pd.read_csv(D/'ANL61905067_reference_native.csv')
    u=np.loadtxt(D/'Unified_Candidate_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(D/'Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2)
    q1=pd.read_csv(ROOT/'runs/C2_battery_common_20261014/inputs/C1_EDU_Q1_loss_nodes.csv');q4=pd.read_csv(ROOT/'runs/C2_battery_common_20261014/inputs/C1_EDU_Q4_loss_nodes.csv');zero=q1[q1.torque_Nm==0].sort_values('rpm');edge=q4.torque_Nm.max();f=[]
    for nodes in [q1,q4]:
        g=nodes.pivot(index='torque_Nm',columns='rpm',values='C1_loss_kW').sort_index().sort_index(axis=1);f.append(RegularGridInterpolator((g.index.to_numpy(),g.columns.to_numpy()),g.to_numpy(),bounds_error=False,fill_value=None))
    end=10122.190356254578;t=np.r_[np.arange(0,np.floor(end)+1),end];speed=np.interp(t,driver.time_s,driver.speed_kmh);rpm=speed/3.6/.3135*7.05*60/(2*np.pi);F=126.329494+.557775*speed+.033456276*speed**2
    rest=(ref.time_s<=5)&(abs(ref.meter_current_A_discharge_positive)<3);v0=float(ref.meter_voltage_V[rest].median());i0=float(ref.meter_current_A_discharge_positive[rest].median());rows=[]
    for meff in [0,1757.6704,1857.6704]:
        force=F+meff*np.gradient(speed/3.6,t);shaft=force*speed/3.6/1000;q=force*.3135/7.05
        zero_loss=f[0](np.c_[np.zeros(len(t)),rpm]);edge_loss=f[1](np.c_[np.repeat(edge,len(t)),rpm])
        loss=np.where(q>=0,f[0](np.c_[np.maximum(q,0),rpm]),np.where(q<=edge,f[1](np.c_[np.minimum(q,edge),rpm]),zero_loss+q/edge*(edge_loss-zero_loss)))
        P=shaft+loss+.4;basis=np.interp(rpm,zero.rpm,zero.original_loss_kW)*np.clip(rpm/250,0,1)*np.where(q>=0,1,np.where(q<=edge,0,1-q/edge));P[speed<.01]=.4;basis[speed<.01]=0
        prefix=t<=9500;P[prefix]=np.interp(t[prefix],b.Time,-col(b,'Current')*col(b,'Voltage')/1000);w=col(v,'E-Motor Speed');qt=col(v,'E-Motor Torque');bb=np.interp(w,zero.rpm,zero.original_loss_kW)*np.clip(w/250,0,1)*np.where(qt>=0,1,np.where(qt<=edge,0,1-qt/edge));bb[(abs(col(v,'E-Motor Current'))<1e-8)&(abs(col(v,'E-Motor Power Mech.'))<1e-8)]=0;basis[prefix]=np.interp(t[prefix],v.Time,bb)
        for db,rg in [(0,1),(.17,1.1)]:
            power=np.maximum(P-db*basis,-40);s=brentq(lambda s:96*np.interp(s,u[:,0],u[:,1])-i0*32*np.interp(s/100,r[:,0],r[:,1])*rg-v0,0,100);S=[s]
            def rate(s,p):
                Uv=96*np.interp(s,u[:,0],u[:,1]);R=32*np.interp(s/100,r[:,0],r[:,1])*rg;I=2*p*1000/(Uv+np.sqrt(Uv**2-4*R*p*1000));return -100*I/169.3568460332183/3600
            for k in range(len(t)-1):
                dt=t[k+1]-t[k];p0=power[k];p1=power[k+1];pm=(p0+p1)/2;a=rate(s,p0);b1=rate(s+a*dt/2,pm);c=rate(s+b1*dt/2,pm);d=rate(s+c*dt,p1);s+=dt*(a+2*b1+2*c+d)/6;S.append(s)
            ss=np.array(S);cross=np.flatnonzero(ss<=0)
            rows.append(dict(tail_effective_mass_kg=meff,delta_beta=db,R_scale=rg,SOC_at9500_percent=float(np.interp(9500,t,ss)),minimum_SOC_percent=float(ss.min()),final_SOC_percent=float(ss[-1]),first_SOC0_s=None if not len(cross) else float(t[cross[0]]),no_coupled_CRUISE_run=True))
            if meff==1757.6704:pd.DataFrame(dict(time_s=t,forecast_DC_kW=power,forecast_SOC_percent=ss,power_origin=np.where(prefix,'actual_prefix_frozen_revised','quasistatic_tail'))).to_csv(OUT/f'tail_forecast_beta{db:.2f}_R{rg:.2f}.csv',index=False)
    report=dict(status='FORECAST_NOT_VALIDATION',selected_delta_beta=.17,selected_R_scale=1.1,capacity_and_OCV_unchanged=True,Q4_regeneration_nodes_unchanged=True,rows=rows,tail_assumptions=['TargetABC driving resistance, flat road, current tire radius/gear','EDU table and lowtorque bridge, auxiliary0.4kW, terminal regen40kW','Actual power known only0-9500; later driver speed is measured ANL input, not predicted vehicle response','No vehicle/driver or battery BMS loop rerun; no OEM BMS identification'],original_SOC_negative_is_diagnostic_forecast_not_permitted_final_operation=True)
    (OUT/'tail_forecast.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
