"""Read-only residual review. Accounting identities are not causal estimates."""
from pathlib import Path
import base64, hashlib, json, zipfile
import numpy as np
import pandas as pd
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs/remaining_review_20261013'
OUT.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(ROOT/'runs/ANL61905060_DIS80_20261013/aligned_comparison.csv')
r = pd.read_csv(ROOT/'independent_tests_20261013/ANL61905060/reference_native.csv')
v = json.loads((ROOT/'runs/ANL61905060_DIS80_20261013/verification.json').read_text())['diagnostic']
t = d.time_s.to_numpy(); nt = r.phase_time_s.to_numpy()
def energy(y, time=t):
    z = np.r_[20, time[(time>20)&(time<3150)], 3150]
    return float(np.trapezoid(np.interp(z,time,y),z)/3600)
residual = v['model_net_kWh']-v['reference_net_kWh']
vm=d.model_voltage_V.to_numpy(); vr=d.reference_voltage_V.to_numpy()
im=d.model_discharge_current_A.to_numpy(); ir=d.reference_discharge_current_A.to_numpy()
# Exact VI decomposition with reference current as the voltage-term baseline.
pv=(vm-vr)*ir/1000; pi=vr*(im-ir)/1000; px=(vm-vr)*(im-ir)/1000
identity=(vm*im-vr*ir)/1000-pv-pi-px
assert np.max(np.abs(identity))<1e-10
lv=energy(r.LV_DCDC_output_W.to_numpy()/1000,nt)
aux=v['aux_HV_net_kWh']; auxbound=max(0,aux-lv)
rp=r.meter_power_kW_discharge_positive.to_numpy()
refgross=energy(np.maximum(rp,0),nt); refrec=-energy(np.minimum(rp,0),nt)
modelgross=v['model_gross_discharge_kWh']; modelrec=v['model_gross_recovered_kWh']
assert abs((modelgross-refgross)+(refrec-modelrec)-residual)<1e-9

project=ROOT/'runs/project_audit_20261013/Bolt_Model_Check.proj'
with zipfile.ZipFile(project) as z:
    root=E.fromstring(z.read('project.xml'), E.XMLParser(resolve_entities=False,no_network=True))
# References repeat IDs; only definitions belong in the index.
idx={x.get('id'):x for x in root.iter() if x.get('id') and x.tag!='ref'}
def scalar(x):
    if x.tag=='ref': return scalar(idx[x.get('id')])
    if x.tag=='str': return base64.b64decode(x.text or '').decode() if x.get('coding')=='base64' else x.text or ''
    if x.tag=='num': return json.loads(x.text)
    if x.tag=='compose': return [scalar(y) for y in x]
    return x.tag
def fields(x):
    if x.tag=='ref': x=idx[x.get('id')]
    if x.tag=='object': x=x.find('dict')
    a=list(x); return {scalar(k):val for k,val in zip(a[::2],a[1::2]) if k.tag=='str'}
def array(oid):
    a=idx[oid]; return np.frombuffer(base64.b64decode(a.text or ''),dtype=a.get('dtype')).copy()
speed_axis=array('40769'); weights=array('40774')
settings={k:scalar(x) for k,x in fields(idx['40757']).items()}
approx={k:scalar(x) for k,x in fields(idx['40776']).items()}
assert np.array_equal(speed_axis,[10,20]) and np.array_equal(weights,[0,1])
assert approx['extrapolation']==['constant']
speed=d.actual_kmh.to_numpy(); predicted=np.interp(speed,speed_axis,weights)
below=speed<speed_axis[0]; above=speed>speed_axis[-1]
pd.DataFrame({'time_s':t,'actual_kmh':speed,'table_implied_weight':predicted,'outside_table_domain':below|above}).to_csv(OUT/'recup_domain_occupancy.csv',index=False)
connections=[]
for o in root.iter('object'):
    if o.get('type')!='act.topo.Connection': continue
    f=fields(o); a={k:scalar(x) for k,x in f.items() if k in ['role1','role2','port1','port2']}
    if a.get('role1')=='Recuperation Weight' or a.get('role2')=='Recuperation Weight':
        connections.append({'id':o.get('id'),**a})
report={
 'window_s':[20,3150], 'net_residual_kWh':residual,
 'auxiliary':{'model_HV_kWh':aux,'measured_LV_output_kWh':lv,'conditional_max_overestimate_kWh':auxbound,'fraction_of_net_residual_percent':100*auxbound/residual,'assumptions':'LV output measurement correct; converter losses and other HV accessory demand nonnegative; no alternative LV energy source. This is an energy bound, not an identified accessory correction.'},
 'VI_identity':{'max_pointwise_closure_error_kW':float(abs(identity).max()),'voltage_at_reference_current_kWh':energy(pv),'current_at_reference_voltage_kWh':energy(pi),'interaction_kWh':energy(px),'common_grid_VI_residual_kWh':energy(pv+pi+px),'native_meter_minus_common_grid_VI_kWh':v['reference_net_kWh']-energy(vr*ir/1000),'note':'Terms depend on chosen algebraic baseline; current and voltage are coupled. Integer-grid VI is not native meter power; do not treat terms as independently fixable causes.'},
 'gross_energy':{'reference_discharge_kWh':refgross,'model_discharge_kWh':modelgross,'discharge_excess_kWh':modelgross-refgross,'reference_recovered_kWh':refrec,'model_recovered_kWh':modelrec,'net_recovery_shortfall_kWh':refrec-modelrec,'recovery_shortfall_fraction_of_net_residual_percent':100*(refrec-modelrec)/residual},
 'charge_limit':{'reference_peak_charge_kW':float(-rp.min()),'model_peak_charge_kW':float(-d.model_DC_kW.min()),'reference_excess_above_40kW_kWh':energy(np.maximum(-rp-40,0),nt),'model_integer_samples_near_minus40_plusminus0p25':int((abs(d.model_DC_kW+40)<.25).sum()),'note':'Different sampling rates for peaks. Measured exceedance quantifies exposure only; not recoverable-energy prediction or an identified BMS map.'},
 'recup_weight':{'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest(),'element_id':'40754','settings':settings,'active_characteristic_axis_kmh':speed_axis.tolist(),'weights':weights.tolist(),'characteristic_approximation':approx,'below_domain_samples':int(below.sum()),'above_domain_samples':int(above.sum()),'in_domain_samples':int((~(below|above)).sum()),'table_implied_output_range':[float(predicted.min()),float(predicted.max())],'connections':connections,'interpretation':'Saved map uses constant extrapolation: 0 below10 and1 above20 km/h. Out-of-domain inputs are expected in this cycle and can explain extrapolation exposure. Exact warning count/fatality and current DIS80 output are not proved by this older snapshot or 1s samples; no weight trace in CSV.'},
 'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'runs/ANL61905060_DIS80_20261013/aligned_comparison.csv',ROOT/'independent_tests_20261013/ANL61905060/reference_native.csv',project]},
 'no_model_inputs_modified':True, 'no_new_simulation_requested':True
}
(OUT/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
