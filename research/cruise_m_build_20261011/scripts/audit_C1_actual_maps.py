"""Confirm genuine CAL outputs apply C1 maps; export midterm comparison figure."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'runs/final_candidate_C1_20261014'
OUT=BASE/'actual_results'
def col(d,n):
    a=[x for x in d if x.startswith('In/'+n+' (')];assert len(a)==1
    return d[a[0]].to_numpy()
def main():
    p=argparse.ArgumentParser();p.add_argument('--exports',type=Path,required=True);args=p.parse_args()
    u=np.loadtxt(BASE/'inputs/C1_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(BASE/'inputs/C1_Cell_Resistance_25C.dat',skiprows=2)
    maps={}
    for q in ['Q1','Q4']:
        d=pd.read_csv(BASE/f'inputs/C1_EDU_{q}_loss_nodes.csv');g=d.pivot(index='torque_Nm',columns='rpm',values='C1_loss_kW').sort_index().sort_index(axis=1)
        maps[q]=(g.index.to_numpy(),RegularGridInterpolator((g.index,g.columns),g.to_numpy(),bounds_error=False,fill_value=None))
    records=[];series=[]
    for test in ['61905060','61905061']:
        b=pd.read_csv(args.exports/f'battery_C1_CAL_{test}.csv',skiprows=[1]);v=pd.read_csv(args.exports/f'velocity_C1_CAL_{test}.csv',skiprows=[1]);t=b.Time.to_numpy()
        vol=col(b,'Voltage');i=-col(b,'Current');s=col(b,'SoC')
        err=96*np.interp(s,u[:,0],u[:,1])-i*32*np.interp(s/100,r[:,0],r[:,1])-vol
        w=col(v,'E-Motor Speed');q=col(v,'E-Motor Torque');shaft=col(v,'E-Motor Power Mech.');dc=col(v,'E-Motor Current')*vol/1000;loss=dc-shaft
        active=(abs(shaft)>1e-8)|(abs(dc)>1e-8);qp,fp=maps['Q1'];qn,fn=maps['Q4'];edge=qn.max()
        predicted=np.where(q>=0,fp(np.c_[q,w]),fn(np.c_[q,w]));bridge=(q<0)&(q>edge);blend=q[bridge]/edge
        predicted[bridge]=(1-blend)*fp(np.c_[np.zeros(bridge.sum()),w[bridge]])+blend*fn(np.c_[np.full(bridge.sum(),edge),w[bridge]])
        me=(predicted-loss)[active];assert np.max(abs(me))<1e-10 and np.max(abs(err))<.05
        metrics=json.loads((OUT/test/'verification.json').read_text());ref=pd.read_csv(BASE/f'references/ANL{test}_reference_native.csv')
        vr=np.interp(t,ref.phase_time_s,ref.meter_voltage_V)
        records.append(dict(test=test,battery_static_C1_voltage_RMSE_V=float(np.sqrt(np.mean(err**2))),battery_static_C1_voltage_max_abs_V=float(np.max(abs(err))),motor_C1_lookup_max_abs_kW=float(np.max(abs(me))),motor_active_samples=int(active.sum()),regenerative_bridge_samples=int((bridge&active).sum()),
          largest_voltage_residual_time_s=float(t[np.argmax(abs(vol-vr))]),gross_recovered_error_percent=100*(metrics['model_gross_recovered_kWh']/metrics['reference_gross_recovered_kWh']-1),
          gross_discharge_error_percent=100*(metrics['model_gross_discharge_kWh']/metrics['reference_gross_discharge_kWh']-1),scope='ActualoutputstateC1map/formulaagreement;notindependentphysicalcomponentvalidation'))
        series.append((test,t,vol,vr,metrics))
        pd.DataFrame(dict(time_s=t,model_voltage_V=vol,reference_voltage_V_on_model_grid=vr,model_SOC_percent=s,model_shaft_kW=shaft,model_motor_DC_kW=dc,C1_loss_predicted_kW=predicted,model_loss_kW=loss,battery_formula_residual_V=err)).to_csv(OUT/test/'aligned_C1_state.csv',index=False)
    (OUT/'C1_runtime_consistency.json').write_text(json.dumps(records,indent=2)+'\n')
    figure_contract={'question':'Do actual CAL060/061 voltage traces reproduce ANL reference with C1?','takeaway':'Both pass proposed aggregate voltage thresholds; remain calibration confirmation, not independent validation.',
      'family':'line','variant':'two-panel measured/model comparison','renderer':'matplotlib_static_scientific_export','grain':'Actual1smodelclock;referenceinterpolatedforplotonly;nativepowerintegrationformetrics',
      'point_counts':[len(s[1]) for s in series],'palette':'BlueC1andneutralreference;solid/dashedline distinction','export':['C1_CAL_voltage_comparison.png','C1_CAL_voltage_comparison.pdf'],'QA':'Inspect exported PNG; same voltage scale across tests'}
    (OUT/'figure_contract.json').write_text(json.dumps(figure_contract,indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(12,7),sharey=True)
    ymin=min(np.minimum(s[2],s[3]).min() for s in series)-2;ymax=max(np.maximum(s[2],s[3]).max() for s in series)+2
    for ax,(test,t,vol,vr,m) in zip(axes,series):
        ax.plot(t,vr,color='#62676c',linewidth=1.1,linestyle='--',label='ANL measured')
        ax.plot(t,vol,color='#3277B3',linewidth=1.0,label='C1 actual CRUISE M')
        ax.set_title(f'ANL {test} | voltage RMSE {m["voltage"]["RMSE"]:.2f} V | mean error {m["voltage"]["bias"]:+.2f} V',loc='left',fontsize=12)
        ax.set_xlim(0,t[-1]);ax.set_ylim(ymin,ymax);ax.set_ylabel('Pack voltage [V]');ax.set_xlabel('Time [s]');ax.grid(axis='y',color='#e8e8e8',linewidth=.6)
    axes[0].legend(loc='lower left',ncol=2,frameon=False)
    fig.suptitle('Bolt BEV C1 calibration confirmation: actual voltage comparison',x=.075,ha='left',fontsize=15)
    fig.text(.075,.02,'Plot: 1 s aligned grid. Metrics exclude initial 20 s. CAL060/061 were used for fitting; independent ANL066 is pending.',fontsize=9,color='#444444')
    fig.tight_layout(rect=[0,.045,1,.94]);fig.savefig(OUT/'C1_CAL_voltage_comparison.png',dpi=180);fig.savefig(OUT/'C1_CAL_voltage_comparison.pdf');plt.close(fig)
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
