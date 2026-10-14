"""Check actual C2 calibration implementation and export scientific comparison."""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.integrate import cumulative_trapezoid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT if (ROOT/'candidate_contract.json').exists() else ROOT/'runs/C2_battery_common_20261014';OUT=BASE/'actual_results'
def col(d,n):return d[[c for c in d if c.startswith('In/'+n+' (')][0]].to_numpy()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--exports',type=Path,required=True);args=ap.parse_args()
 u=np.loadtxt(BASE/'inputs/C2_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(BASE/'inputs/C2_Cell_Resistance_25C.dat',skiprows=2);capacity=json.loads((BASE/'parameters.json').read_text())['battery_pack_capacity_Ah']
 maps={}
 for q in ['Q1','Q4']:
  d=pd.read_csv(BASE/f'inputs/C1_EDU_{q}_loss_nodes.csv');g=d.pivot(index='torque_Nm',columns='rpm',values='C1_loss_kW').sort_index().sort_index(axis=1);maps[q]=(g.index.to_numpy(),RegularGridInterpolator((g.index,g.columns),g.to_numpy(),bounds_error=False,fill_value=None))
 results=[];series=[]
 for test in ['61905060','61905061','61905066']:
  b=pd.read_csv(args.exports/f'battery_CAL{test[-2:]}.csv',skiprows=[1]);v=pd.read_csv(args.exports/f'velocity_CAL{test[-2:]}.csv',skiprows=[1]);t=b.Time.to_numpy();vol=col(b,'Voltage');i=-col(b,'Current');s=col(b,'SoC')
  err=96*np.interp(s,u[:,0],u[:,1])-i*32*np.interp(s/100,r[:,0],r[:,1])-vol
  replaySOC=s[0]-cumulative_trapezoid(i,t,initial=0)/3600/capacity*100
  w=col(v,'E-Motor Speed');q=col(v,'E-Motor Torque');shaft=col(v,'E-Motor Power Mech.');dc=col(v,'E-Motor Current')*vol/1000;loss=dc-shaft;active=(abs(shaft)>1e-8)|(abs(dc)>1e-8)
  qp,fp=maps['Q1'];qn,fn=maps['Q4'];edge=qn.max();pred=np.where(q>=0,fp(np.c_[q,w]),fn(np.c_[q,w]));bridge=(q<0)&(q>edge);a=q[bridge]/edge
  pred[bridge]=(1-a)*fp(np.c_[np.zeros(bridge.sum()),w[bridge]])+a*fn(np.c_[np.full(bridge.sum(),edge),w[bridge]])
  me=(pred-loss)[active];assert abs(me).max()<1e-10 and abs(err).max()<.05
  metrics=json.loads((OUT/test/'verification.json').read_text());ref=pd.read_csv(BASE/f'references/ANL{test}_reference_native.csv');nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'];vr=np.interp(t,nt,ref.meter_voltage_V)
  row=dict(test=test,C2_voltage_formula_max_abs_V=float(abs(err).max()),C1_EDU_loss_lookup_max_abs_kW=float(abs(me).max()),SOC_1s_current_integral_max_abs_pp=float(abs(replaySOC-s).max()),SOC_initial_percent=float(s[0]),SOC_end_percent=float(s[-1]),max_single_second_SOC_change_pp=float(abs(np.diff(s)).max()),gross_discharge_error_percent=100*(metrics['model_gross_discharge_kWh']/metrics['reference_gross_discharge_kWh']-1),gross_recovered_error_percent=100*(metrics['model_gross_recovered_kWh']/metrics['reference_gross_recovered_kWh']-1),scope='Actualmap/formulaagreement;coarse1sSOCintegraldiagnosticonly;notphysicalcellidentification')
  results.append(row);series.append((test,t,vol,vr,metrics))
  pd.DataFrame(dict(time_s=t,C2_voltage_V=vol,reference_voltage_V=vr,model_SOC_percent=s,battery_formula_residual_V=err,SOC_1s_replayed_percent=replaySOC)).to_csv(OUT/test/'aligned_C2_state.csv',index=False)
  if metrics['phase_diagnostics']:pd.json_normalize(metrics['phase_diagnostics']).to_csv(OUT/test/'phase_metrics.csv',index=False)
 (OUT/'C2_runtime_consistency.json').write_text(json.dumps(results,indent=2)+'\n')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(3,1,figsize=(12,9),sharey=True)
 for ax,(test,t,vol,vr,m) in zip(axes,series):
  ax.plot(t,vr,color='#62676c',lw=.9,ls='--',label='ANL measured');ax.plot(t,vol,color='#3277B3',lw=.8,label='C2 actual CRUISE M')
  ax.set_title(f'ANL {test} | voltage RMSE {m["voltage"]["RMSE"]:.2f} V | mean error {m["voltage"]["bias"]:+.2f} V | energy error {m["energy_error_percent"]:+.2f}%',loc='left',fontsize=11)
  ax.set_xlim(0,t[-1]);ax.set_ylabel('Pack voltage [V]');ax.set_xlabel('Time [s]');ax.grid(axis='y',color='#e8e8e8')
 axes[0].legend(frameon=False,ncol=2,loc='lower left')
 fig.suptitle('Bolt BEV C2: actual calibration confirmation',x=.075,ha='left',fontsize=15)
 fig.text(.075,.015,'All three tests are C2 training data. Initial 20 s excluded from voltage metrics. Fresh independent tests 058/059 pending.',fontsize=9)
 fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(OUT/'C2_CAL_actual_voltage_comparison.png',dpi=180);fig.savefig(OUT/'C2_CAL_actual_voltage_comparison.pdf');plt.close(fig)
 print(json.dumps(results,indent=2))
if __name__=='__main__':main()
