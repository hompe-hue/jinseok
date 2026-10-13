"""Unfitted bridge check using extracted embedded maps and existing CSV outputs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'runs/regen_zero_torque_bridge_20261013'
OUT.mkdir(exist_ok=True)
maps = {}
for name in ('Q1','Q4'):
    d = pd.read_csv(ROOT/f'runs/project_audit_20261013/embedded_motor_loss_{name}.csv')
    d.columns = ['temperature','voltage','rpm','torque','loss']
    q = 0 if name == 'Q1' else d.torque.max()
    maps[name] = d.loc[d.torque == q].sort_values('rpm')
edge = maps['Q4']; zero = maps['Q1']; summaries = []
for test in ('61905060','61905061'):
    d = pd.read_csv(ROOT/f'runs/project_map_boundary_audit_20261013/ANL{test}_boundary_samples.csv')
    d = d.loc[d.Q4_outside & d.regen].copy()
    assert d.rpm.between(edge.rpm.min(),edge.rpm.max()).all()
    alpha = d.torque_Nm / edge.torque.iloc[0]
    assert alpha.between(0,1).all()
    d['bridge_loss_kW'] = (1-alpha)*np.interp(d.rpm,zero.rpm,zero.loss)+alpha*np.interp(d.rpm,edge.rpm,edge.loss)
    d['bridge_error_kW'] = d.bridge_loss_kW-d.observed_model_loss_kW
    maxerr = float(abs(d.bridge_error_kW).max())
    assert maxerr < 1e-10
    d.to_csv(OUT/f'ANL{test}_bridge_comparison.csv',index=False)
    summaries.append(dict(test=test,samples=len(d),RMSE_kW=float(np.sqrt(np.mean(d.bridge_error_kW**2))),max_abs_error_kW=maxerr,
        regenerative_shaft_samples_with_positive_motor_DC=int(((d.shaft_kW+d.observed_model_loss_kW)>0).sum()),
        fitted_parameters=0,new_simulations=0,project_changed=False))
zero.to_csv(OUT/'Q1_zero_torque_nodes.csv',index=False)
edge.to_csv(OUT/'Q4_edge_nodes.csv',index=False)
(OUT/'two_test_summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
print(json.dumps(summaries,indent=2))
