"""Read ACT XML safely; never instantiate serialized project objects or edit the project."""
import base64,hashlib,json,sys,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from lxml import etree as E
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/project_audit_20261013'
OUT.mkdir(parents=True,exist_ok=True)
source=Path(sys.argv[1])
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    xml=z.read('project.xml')
r=E.fromstring(xml,E.XMLParser(resolve_entities=False,no_network=True))
# Index definitions only: later ref nodes repeat IDs and must not overwrite objects.
idx={x.get('id'):x for x in r.iter() if x.get('id') and x.tag!='ref'}
def scalar(x):
    if x.tag=='ref':return scalar(idx[x.get('id')])
    if x.tag=='str':return base64.b64decode(x.text or '').decode(errors='replace') if x.get('coding')=='base64' else x.text or ''
    if x.tag=='num':return json.loads(x.text)
    return x.tag
def fields(x):
    if x.tag=='ref':x=idx[x.get('id')]
    if x.tag=='object':x=x.find('dict')
    a=list(x);return {scalar(k):v for k,v in zip(a[::2],a[1::2]) if k.tag=='str'}
def amount(oid,key):
    return scalar(fields(fields(idx[oid])[key])['value'])
def columns(oid):
    out=[]
    for node in idx[oid].iter('object'):
        if node.get('type')!='act.tbl.NumArray':continue
        f=fields(node); a=f['data']
        if a.tag=='ref':a=idx[a.get('id')]
        data=np.frombuffer(base64.b64decode(a.text or ''),dtype=a.get('dtype')).copy()
        u=f['unit'];out.append((scalar(u[0]),data))
    return out
def export(oid,name):
    cols=columns(oid);pd.DataFrame({f'{k}_{unit}':a for k,(unit,a) in enumerate(cols)}).to_csv(OUT/name,index=False)
    return cols

checks=[]
for oid,name in [('48264','module1_OCV'),('48840','module2_OCV'),('48288','module1_Rcharge'),('48312','module1_Rdischarge'),('48864','module2_Rcharge'),('48888','module2_Rdischarge')]:
    cols=export(oid,name+'.csv');data=np.column_stack([cols[1][1],cols[2][1]])
    expected=np.loadtxt(ROOT/('inputs/battery/Bolt_Cell_OCV_25C.dat' if 'OCV' in name else 'inputs/battery/Bolt_Cell_Resistance_25C.dat'),skiprows=2)
    assert data.shape==expected.shape
    err=float(np.max(abs(data-expected)));assert err<1e-10
    checks.append({'table':name,'rows':len(data),'maximum_difference_from_stored_input':err,'temperature_C':float(cols[0][1][0]),'units':[u for u,a in cols]})
profile=export('37678','embedded_ANL61905061_profile.csv')
expected=pd.read_csv(ROOT/'independent_tests_20261013/ANL61905061/driver_1s.csv')
assert len(profile[0][1])==len(expected)
profile_err=float(np.max(abs(profile[1][1]-expected.speed_kmh.to_numpy())))
assert profile_err<1e-9
lines=(ROOT/'inputs/Bolt_EDU_Loss_400V_AVL_RegularMap.dat').read_text().splitlines()
q=np.array([float(v) for v in lines[5].split()]);w=np.array([float(v) for v in lines[8].split()]);loss=np.array([[float(v) for v in row.split()] for row in lines[11:]])
lookup=RegularGridInterpolator((q,w),loss,bounds_error=False,fill_value=np.nan)
motormaps=[]
for oid,label in [('50409','Q1'),('50496','Q4')]:
    cols=export(oid,'embedded_motor_loss_'+label+'.csv')
    rpm=cols[2][1];tq=cols[3][1];ploss=cols[4][1]
    pred=lookup(np.c_[tq,rpm*2*np.pi/60])/1000
    motormaps.append({'quadrant':label,'rows':len(rpm),'temperature_K':float(cols[0][1][0]),'voltage_V':float(cols[1][1][0]),'max_difference_from_stored_17x17_map_kW':float(np.nanmax(abs(ploss-pred))),'table_lookup_rows_outside_domain':int(np.isnan(pred).sum())})
# Original serializer IDs are explicitly preserved for this specific uploaded file.
report={'project_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'zip_CRC_passed':True,'ACT_version':r.get('version'),'XML_size_bytes':len(xml),'additional_DAT_filename_references':[scalar(x) for x in r.iter('str') if scalar(x).lower().endswith('.dat')],
 'module1_initial_SOC_percent':amount('48260','initial_charge'),'module2_initial_SOC_percent':amount('48836','initial_charge'),
 'module1_temperature_C':amount('48452','temperature'),'module2_temperature_C':amount('49028','temperature'),
 'aux_kW':amount('67108','power'),'final_drive_ratio':amount('37448','transmission_ratio'),'final_drive_efficiency':amount('37458','efficiency'),
 'saved_end_time_s':amount('76198','end_time'),
 'battery_tables':checks,'profile_rows':len(profile[0][1]),'profile_end_s':float(profile[0][1][-1]),'profile_max_speed_difference_kmh':profile_err,'motor_tables':motormaps,
 'scope':'Read-only saved state and embedded tables; not a CRUISE runtime validation or physical OCV/efficiency identification'}
(OUT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
