from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
run=root/'runs/ANL61905054_regen_20261013'
r=list(csv.DictReader((run/'empirical_aligned_diagnostics.csv').open()))
get=lambda k:np.array([float(x[k]) for x in r])
t=get('time_s');vm=get('model_voltage_V');vr=get('reference_voltage_V');im=get('model_discharge_current_A');ir=get('reference_discharge_current_A');pm=get('model_discharge_power_kW')
n=list(csv.DictReader((root/'empirical_alignment_20261013/ANL_61905054_phase1/ANL_61905054_Phase1_reference_native.csv').open()))
nt=np.array([float(x['phase_time_s']) for x in n]);npower=np.array([float(x['meter_pack_power_kW_discharge_positive']) for x in n])
cum=lambda y,x:np.r_[0,np.cumsum(np.diff(x)*(y[1:]+y[:-1])/2/3600)]
ne=cum(npower,nt);me=cum(pm,t)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(2,2,figsize=(12,7.6),layout='constrained')
for a in ax.ravel():a.grid(True,alpha=.2);a.set_xlabel('Time (s)');a.set_xlim(0,1144);a.axvspan(0,20,color='#aaaaaa',alpha=.22)
ax[0,0].plot(t,vr,label='Measured',color='#1f2937',linewidth=1);ax[0,0].plot(t,vm,label='Model',color='#1974c7',linewidth=.9,alpha=.85);ax[0,0].set(title='Terminal voltage',ylabel='Voltage (V)');ax[0,0].legend(loc='lower left')
ax[0,1].plot(t,ir,label='Measured',color='#1f2937',linewidth=.8);ax[0,1].plot(t,im,label='Model',color='#1974c7',linewidth=.8,alpha=.85);ax[0,1].set(title='Battery current (discharge positive)',ylabel='Current (A)');ax[0,1].legend()
ax[1,0].plot(t,me,label='Model: 2.2310 kWh',color='#1974c7');ax[1,0].plot(nt[nt<=1144],ne[nt<=1144],label='Measured: 2.1549 kWh',color='#1f2937');ax[1,0].set(title='Cumulative net DC energy',ylabel='Energy (kWh)');ax[1,0].legend()
ax[1,1].plot(t,vm-vr,color='#1974c7',linewidth=.8);ax[1,1].axhline(0,color='#555555',linewidth=.8);ax[1,1].set(title='Voltage residual: model - measured',ylabel='Voltage error (V)');ax[1,1].text(.02,.97,'t > 20 s: RMSE 0.663 V; bias -0.038 V',transform=ax[1,1].transAxes,va='top')
fig.suptitle('2017 Chevrolet Bolt EV | ANL 61905054 | Conditional replay',fontsize=15)
fig.supxlabel('Shaded 0-20 s: initialization. Diagnostic charge cap and approximate auxiliary load; independent validation pending.',fontsize=9)
fig.savefig(run/'comparison.png',dpi=180)
