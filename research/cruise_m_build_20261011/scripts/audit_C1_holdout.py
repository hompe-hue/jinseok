"""Read-only C1 HOLD066 implementation/phase diagnostics and scientific exports."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'runs/final_candidate_C1_20261014'
OUT=BASE/'actual_results/61905066'
def col(d,n):return d[[x for x in d if x.startswith('In/'+n+' (')][0]].to_numpy()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--exports',type=Path,required=True);args=ap.parse_args()
    b=pd.read_csv(args.exports/'battery_C1_CAL_61905066.csv',skiprows=[1]);v=pd.read_csv(args.exports/'velocity_C1_CAL_61905066.csv',skiprows=[1]);t=b.Time.to_numpy();vol=col(b,'Voltage')
    maps={}
    for label in ['Q1','Q4']:
        d=pd.read_csv(BASE/f'inputs/C1_EDU_{label}_loss_nodes.csv');g=d.pivot(index='torque_Nm',columns='rpm',values='C1_loss_kW').sort_index().sort_index(axis=1)
        maps[label]=(g.index.to_numpy(),RegularGridInterpolator((g.index,g.columns),g.to_numpy(),bounds_error=False,fill_value=None))
    q=col(v,'E-Motor Torque');w=col(v,'E-Motor Speed');shaft=col(v,'E-Motor Power Mech.');dc=col(v,'E-Motor Current')*vol/1000;active=(abs(dc)>1e-8)|(abs(shaft)>1e-8)
    qp,fp=maps['Q1'];qn,fn=maps['Q4'];edge=qn.max();pred=np.where(q>=0,fp(np.c_[q,w]),fn(np.c_[q,w]));bridge=(q<0)&(q>edge);a=q[bridge]/edge
    pred[bridge]=(1-a)*fp(np.c_[np.zeros(bridge.sum()),w[bridge]])+a*fn(np.c_[np.full(bridge.sum(),edge),w[bridge]])
    err=(pred-(dc-shaft))[active];assert abs(err).max()<1e-10
    metrics=json.loads((OUT/'verification.json').read_text());replay=pd.read_csv(OUT/'battery_replay_aligned.csv')
    summary={'test':'61905066','motor_C1_lookup_max_abs_error_kW':float(abs(err).max()),'motor_active_samples':int(active.sum()),'bridge_samples':int((active&bridge).sum()),
      'gross_discharge_error_percent':100*(metrics['model_gross_discharge_kWh']/metrics['reference_gross_discharge_kWh']-1),
      'gross_recovered_error_percent':100*(metrics['model_gross_recovered_kWh']/metrics['reference_gross_recovered_kWh']-1),
      'parameters_changed':False,'scope':'C1applicationconfirmed;independentmeanvoltagebiascriterionfails'}
    (OUT/'runtime_consistency.json').write_text(json.dumps(summary,indent=2)+'\n')
    pd.json_normalize(metrics['phase_diagnostics']).to_csv(OUT/'phase_metrics.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True,gridspec_kw={'height_ratios':[1.2,1]})
    axes[0].plot(t,replay.reference_voltage_V,color='#60666c',ls='--',lw=1,label='ANL measured')
    axes[0].plot(t,vol,color='#3277B3',lw=1,label='C1 actual CRUISE M')
    axes[0].set_ylabel('Pack voltage [V]');axes[0].legend(frameon=False,ncol=2,loc='upper right')
    axes[1].plot(t,vol-replay.reference_voltage_V,color='#3277B3',lw=.8,label='C1 minus measured')
    axes[1].plot(t,replay.measured_current_replay_voltage_V-replay.reference_voltage_V,color='#D69A38',ls=':',lw=1,label='Measured-current replay minus measured')
    axes[1].axhline(0,color='#60666c',lw=.8);axes[1].set_ylabel('Voltage residual [V]');axes[1].set_xlabel('Time [s]');axes[1].legend(frameon=False,ncol=2,loc='lower left',fontsize=10)
    phase=pd.read_csv(BASE/'references/phase_windows.csv')
    for row in phase.to_dict('records'):
        mid=(row['start_s']+row['end_s'])/2;axes[1].text(mid,.92,f'P{int(row["phase"])}',transform=axes[1].get_xaxis_transform(),ha='center',fontsize=9,color='#555555')
        if row['phase']>1:
            for ax in axes:ax.axvline(row['start_s'],color='#d9d9d9',ls=':',lw=.7)
    for ax in axes:ax.set_xlim(0,t[-1]);ax.grid(axis='y',color='#e8e8e8',lw=.6)
    fig.suptitle('C1 vs ANL61905066: independent voltage comparison',x=.075,ha='left',fontsize=15)
    fig.text(.075,.025,'Fixed before comparison. No tuning on 066. Voltage mean bias -1.36 V misses the 1 V limit; overall energy error -2.36%.',fontsize=9,color='#444444')
    fig.tight_layout(rect=[0,.045,1,.94]);fig.savefig(OUT/'C1_HOLD066_voltage_diagnosis.png',dpi=180);fig.savefig(OUT/'C1_HOLD066_voltage_diagnosis.pdf');plt.close(fig)
    contract={'question':'How does C1 voltage error develop across independent066?','family':'line','variant':'two-panel actualvoltage/residuals','renderer':'matplotlib_scientific_export','source_grain':'7631actual1srows;nativepowerintegrationformetrics;referencealignedforplot',
      'palette':'BlueC1,goldmeasured-currentreplay,neutralmeasured;solid/dashed/dotted distinction','claim':'Whole-testmeanvoltagebiasfails;latebiaspersistswithmeasuredcurrent','parameters_changed':False,'QA':'Inspect exported PNG/PDF'}
    (OUT/'figure_contract.json').write_text(json.dumps(contract,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
