"""Boundary-use diagnostics; alternative lookups are not AVL semantics or proposed changes."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/project_map_boundary_audit_20261013'
OUT.mkdir(parents=True,exist_ok=True)
maps={}
for name in ['Q1','Q4']:
    d=pd.read_csv(ROOT/'runs/project_audit_20261013'/('embedded_motor_loss_'+name+'.csv'))
    d.columns=['temperature','voltage','rpm','torque','loss']
    z=d.pivot(index='torque',columns='rpm',values='loss').sort_index().sort_index(axis=1)
    assert z.notna().all().all()
    q=z.index.to_numpy();w=z.columns.to_numpy()
    maps[name]=(q,w,RegularGridInterpolator((q,w),z.to_numpy(),bounds_error=False,fill_value=None))
results=[]
for test in ['61905060','61905061']:
    folder=ROOT/'runs'/('ANL'+test+'_20261013')
    suffix='(1)' if test=='61905060' else ''
    v=pd.read_csv(folder/('velocity_ANL'+test+suffix+'.csv'),skiprows=[1]);b=pd.read_csv(folder/('battery_ANL'+test+suffix+'.csv'),skiprows=[1])
    assert np.array_equal(v.Time,b.Time)
    def col(frame,prefix):return frame[[k for k in frame if k.startswith('In/'+prefix+' (')][0]].to_numpy()
    t=v.Time.to_numpy();w=col(v,'E-Motor Speed');q=col(v,'E-Motor Torque');shaft=col(v,'E-Motor Power Mech.')
    observed_loss=col(v,'E-Motor Current')*col(b,'Voltage')/1000-shaft
    qa,wa,f=maps['Q1'];drive=shaft>.01
    drive_pred=f(np.c_[q,abs(w)])
    qa,wa,f=maps['Q4'];regen=shaft<-.01
    inside=regen&(q>=qa.min())&(q<=qa.max())&(abs(w)>=wa.min())&(abs(w)<=wa.max())
    outside=regen&~inside
    linear=np.maximum(0,f(np.c_[q,abs(w)]))
    clamped=f(np.c_[np.clip(q,qa.min(),qa.max()),np.clip(abs(w),wa.min(),wa.max())])
    def errors(pred,mask):
        e=observed_loss[mask]-pred[mask]
        return dict(rows=int(mask.sum()),RMSE_kW=float(np.sqrt(np.mean(e**2))),max_abs_kW=float(np.max(abs(e))))
    record=dict(test=test,total_exported_rows=len(t),Q4_rpm_range=[float(wa.min()),float(wa.max())],Q4_torque_range=[float(qa.min()),float(qa.max())],
        drive_Q1=errors(drive_pred,drive),regen_inside_Q4=errors(linear,inside),regen_outside_Q4_rows=int(outside.sum()),regen_total_rows=int(regen.sum()),
        outside_low_abs_torque_rows=int((regen&(q>qa.max())).sum()),outside_low_speed_rows=int((regen&(abs(w)<wa.min())).sum()),
        regen_vs_simple_constant_boundary=errors(clamped,regen),regen_vs_simple_linear_boundary=errors(linear,regen),
        constant_alternative_minus_observed_regen_energy_kWh=float(np.trapezoid(np.where(regen,clamped-observed_loss,0),t)/3600),
        linear_alternative_minus_observed_regen_energy_kWh=float(np.trapezoid(np.where(regen,linear-observed_loss,0),t)/3600),
        interpretation='Exact interior agreement verifies in-domain lookup at sampled points. Exterior alternatives do not prove AVL extrapolation semantics and are not input-change recommendations.')
    results.append(record)
    pd.DataFrame(dict(time_s=t,rpm=w,torque_Nm=q,shaft_kW=shaft,observed_model_loss_kW=observed_loss,regen=regen,Q4_inside=inside,Q4_outside=outside,diagnostic_constant_boundary_kW=clamped,diagnostic_linear_boundary_kW=linear)).to_csv(OUT/('ANL'+test+'_boundary_samples.csv'),index=False)
(OUT/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
