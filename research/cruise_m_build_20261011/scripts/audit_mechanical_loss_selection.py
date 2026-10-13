"""Read-only saved selections and kinematic/ABC diagnostics; no runtime or fit."""
import base64, hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/mechanical_loss_selection_20261013'; OUT.mkdir(exist_ok=True)
source=Path(sys.argv[1])
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    r=E.fromstring(z.read('project.xml'),E.XMLParser(resolve_entities=False,no_network=True))
# Index definitions only: later ref nodes repeat IDs and must not overwrite objects.
idx={x.get('id'):x for x in r.iter() if x.get('id') and x.tag!='ref'}
def fields(x):
    if x.tag=='ref': x=idx[x.get('id')]
    if x.tag=='object': x=x.find('dict')
    a=list(x); return {decode(k):v for k,v in zip(a[::2],a[1::2]) if k.tag=='str'}
def decode(x,seen=()):
    if x.tag=='ref':
        key=x.get('id')
        return {'cycle_ref':key} if key in seen else decode(idx[key],seen+(key,))
    if x.tag=='str': return base64.b64decode(x.text or '').decode() if x.get('coding')=='base64' else x.text or ''
    if x.tag=='num': return json.loads(x.text)
    if x.tag in ('true','false'): return x.tag=='true'
    if x.tag in ('compose','tuple','list'): return [decode(v,seen) for v in x]
    if x.tag in ('dict','object'):
        f=fields(x)
        if 'value' in f: return {k:decode(v,seen) for k,v in f.items() if k in ('value','unit')}
        return {'object_type':x.get('type'),'id':x.get('id')}
    return {'tag':x.tag}
ids=['37448','37450','37453','37458','40511','40515','40532','40534',
     '36261','36297','36300','36433','36508','36525',
     '32107','32775','33026','40872','32114','32782','33033','40879',
     '32105','32773','33024','40870','34209','34309','40665','51365','50176']
snapshot=[dict(id=i,type=idx[i].get('type'),fields={k:decode(v) for k,v in fields(idx[i]).items()}) for i in ids]
(OUT/'saved_selection_snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
def value(i,k): return decode(fields(idx[i])[k])['value']
ratio=value('37448','transmission_ratio'); radius=value('32114','dynamic_rolling_radius')/1000
A=value('36433','constant_part');B=value('36433','linear_part');C=value('36433','square_part')
mass=value('36297','curb_weight')+decode(fields(idx['36508'])['absolute'])['value']
records=[]
for test in ('61905060','61905061'):
    folder=ROOT/f'runs/ANL{test}_20261013'; suffix='(1)' if test=='61905060' else ''
    path=folder/f'velocity_ANL{test}{suffix}.csv'
    d=pd.read_csv(path,skiprows=[1]); refpath=ROOT/f'independent_tests_20261013/ANL{test}/reference_native.csv'
    ref=pd.read_csv(refpath)
    def col(name): return d[[c for c in d if c.startswith('In/'+name+' (')][0]].to_numpy()
    t=d.Time.to_numpy();v=col('Actual Velocity');rpm=col('E-Motor Speed')
    predicted=v/3.6/radius*ratio*60/(2*np.pi)
    keep=(t>=20)&(t<=ref.phase_time_s.max()); refkeep=(ref.phase_time_s>=t[keep][0])&(ref.phase_time_s<=t[keep][-1])
    def work(v,t): return float(np.trapezoid((A+B*v+C*v*v)*v/3.6/1000,t)/3600)
    wm=work(v[keep],t[keep]); wr=work(ref.speed_kmh[refkeep].to_numpy(),ref.phase_time_s[refkeep].to_numpy())
    # Same integer-second grid isolates kinematic tracking from integration resolution.
    vr=np.interp(t,ref.phase_time_s,ref.speed_kmh); wrgrid=work(vr[keep],t[keep])
    record=dict(test=test,start_s=float(t[keep][0]),end_s=float(t[keep][-1]),
        kinematic_rpm_RMSE=float(np.sqrt(np.mean((rpm-predicted)**2))),kinematic_rpm_max_abs=float(abs(rpm-predicted).max()),
        ABC_work_model_kWh=wm,ABC_work_measured_speed_native_kWh=wr,ABC_work_measured_speed_same_grid_kWh=wrgrid,
        ABC_work_tracking_difference_same_grid_kWh=wm-wrgrid,
        model_translational_kinetic_endpoint_change_kWh=float(.5*mass*((v[keep][-1]/3.6)**2-(v[keep][0]/3.6)**2)/3.6e6),
        input_sha256={path.name:hashlib.sha256(path.read_bytes()).hexdigest(),'reference_native.csv':hashlib.sha256(refpath.read_bytes()).hexdigest()})
    records.append(record)
    pd.DataFrame(dict(time_s=t,actual_kmh=v,motor_rpm=rpm,kinematic_predicted_rpm=predicted,rpm_residual=rpm-predicted,model_ABC_kW=(A+B*v+C*v*v)*v/3.6/1000)).to_csv(OUT/f'ANL{test}_kinematic_ABC.csv',index=False)
report=dict(project_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),saved_effective_translation_mass_kg=mass,
    final_drive_ratio=ratio,final_drive_efficiency=value('37458','efficiency'),differential_loss_selection=decode(fields(idx['40534'])['transmission_loss']),
    differential_inactive_base_efficiency=value('40532','base_efficiency'),wheel_radius_m=radius,ABC=[A,B,C],diagnostics=records,
    scope='Saved selections plus sampled kinematics and assumed ABC work only; not measured dyno-load equivalence, full power balance or physical loss validation')
(OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
