"""Build one CRUISE implementation-check copy of the common battery candidate.
Correct confirmed two-module BMS signal wiring; retain diagnostic control maps.
This warm060 run is not a final low-SOC/performance validation.
"""
import base64,copy,hashlib,json,os,zipfile
from pathlib import Path
import numpy as np
from lxml import etree as E
from audit_dis80_semantic import SavedProject,ROOT
OUT=ROOT/'runs/unified_BEV_model_20261014/implementation_060'
U=OUT.parent;C2=ROOT/'runs/C2_battery_common_20261014'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=C2/'projects/C2_CAL_61905060.proj';assert sha(source)=='49921958c91e386bf66d997c7abf3b907c499a22f86f3507482c6c5136a8ea25'
    OUT.mkdir(parents=True,exist_ok=True);cfg=json.loads((U/'development_screen.json').read_text())
    ocv=np.loadtxt(U/'Unified_Candidate_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(U/'Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2)
    s0=next(x for x in cfg['metrics'] if x['test']=='61905060')['initial_model_SOC_percent']
    p=SavedProject(source);before=SavedProject(source);modified=[]
    def array(oid,values):
        x=p.resolve(p.fields(p.index[oid])['data']);a=np.asarray(values,dtype=x.get('dtype'));assert np.isfinite(a).all()
        x.set('dim',' '.join(map(str,a.shape)));x.text=base64.b64encode(a.tobytes()).decode();modified.append(x.get('id'))
    def amount(n,key,value):
        x=p.resolve(p.fields(n)[key]);p.fields(x)['value'].text=repr(float(value));modified.append(x.get('id'))
    for typ,values in [('IdleVoltage',ocv[:,1]),('OhmicResistanceCharge',r[:,1]),('OhmicResistanceDischarge',r[:,1])]:
        for n in p.nodes('cruise.props.commons_battery.'+typ):
            aa=p.arrays_under(n);assert len(aa)==3 and len(aa[2][2])==len(values);array(aa[2][0],values)
    for n in p.nodes('cruise.props.battery.General'):amount(p.resolve(p.fields(n)['maximum_charge']),'const',cfg['cell_capacity_Ah'])
    for n in p.nodes('cruise.props.battery.InitialConditions'):amount(n,'initial_charge',s0)
    wiring=[]
    for n in p.nodes('act.topo.Connection'):
        f=p.fields(n)
        if not all(k in f for k in ['role1','port1','role2','port2']):continue
        q={k:p.decode(f[k]) for k in ['role1','port1','role2','port2']}
        if q['role1']=='HV Battery' and q['role2']=='BMS ECM':
            if q['port2']=='SoC Module 2' and q['port1']=='State of charge.4':
                f['port1'].text='State of charge.5';wiring.append(dict(connection_id=n.get('id'),before=q,after_port1='State of charge.5'))
            elif q['port2']=='Power Module 2' and q['port1']=='Power loss':
                f['port1'].text='Power.5';wiring.append(dict(connection_id=n.get('id'),before=q,after_port1='Power.5'))
    assert len(wiring)==3,wiring # Power2 in both models; SOC2 was wrong in one model.
    assert sum(x['after_port1']=='Power.5' for x in wiring)==2
    assert sum(x['after_port1']=='State of charge.5' for x in wiring)==1
    name='C3_IMPL_61905060'
    p.fields(p.index['82936'])['name'].text=name
    for n in p.nodes('cruise.props.tasks.profile.General'):
        if p.decode(p.fields(n)['name'])=='C2_CAL_61905060':p.fields(n)['name'].text=name
    for d in p.root.iter('dict'):
        xs=list(d)
        for k,v in zip(xs[::2],xs[1::2]):
            if k.tag=='str' and k.text=='ANL61905060' and p.resolve(v).get('id')=='40659':k.text=name
    dest=OUT/(name+'.proj');tmp=dest.with_suffix('.proj.part')
    with zipfile.ZipFile(source) as zin,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():zout.writestr(copy.copy(info),E.tostring(p.root,encoding='utf-8',xml_declaration=True) if info.filename=='project.xml' else zin.read(info.filename))
    with tmp.open('rb') as f:os.fsync(f.fileno())
    with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
    os.replace(tmp,dest);fd=os.open(dest.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    after=SavedProject(dest);assert before.index.keys()==after.index.keys()
    assert [x.get('id') for x in before.root.iter('ref')]==[x.get('id') for x in after.root.iter('ref')]
    # Every non-battery numeric array, including profile, EDU, BMS maps, is unchanged.
    for oid,node in before.index.items():
        if node.tag=='numpy_array' and node.text!=after.index[oid].text:assert oid in modified
    for n in after.nodes('cruise.props.battery.InitialConditions'):assert abs(after.amount(n,'initial_charge')-s0)<1e-10
    for n in after.nodes('cruise.props.battery.General'):assert abs(after.amount(after.resolve(after.fields(n)['maximum_charge']),'const')-cfg['cell_capacity_Ah'])<1e-10
    for typ,values in [('IdleVoltage',ocv[:,1]),('OhmicResistanceCharge',r[:,1]),('OhmicResistanceDischarge',r[:,1])]:
        for n in after.nodes('cruise.props.commons_battery.'+typ):assert np.array_equal(after.arrays_under(n)[2][2],values)
    for row in wiring:assert after.fields(after.index[row['connection_id']])['port1'].text==row['after_port1']
    with zipfile.ZipFile(source) as zin,zipfile.ZipFile(dest) as zout:
        assert all(zin.read(n)==zout.read(n) for n in zin.namelist() if n!='project.xml')
    ref=C2/'references/ANL61905060_reference_native.csv';copyfile=OUT/'ANL61905060_reference_native.csv';copyfile.write_bytes(ref.read_bytes());assert sha(ref)==sha(copyfile)
    for src in [U/'Unified_Candidate_Cell_OCV_25C.dat',U/'Unified_Candidate_Cell_Resistance_25C.dat',U/'development_screen.json',U/'fixed_power_screen.json']: (OUT/src.name).write_bytes(src.read_bytes())
    manifest=dict(status='IMPLEMENTATION_CHECK_ONLY_PENDING_USER_CRUISE',candidate='C3 common battery development candidate, not final adoption',project=dest.name,project_sha256=sha(dest),bytes=dest.stat().st_size,source_C2_sha256=sha(source),test='61905060',role='training implementation check',model='REEV_MBE',case='Cycle Run / C3_IMPL_61905060',initial_model_SOC_percent=s0,cell_capacity_Ah=cfg['cell_capacity_Ah'],pack_capacity_Ah=cfg['capacity_Ah'],end_time_s=after.amount(after.index['79182'],'end_time'),mass_kg=1757.6704,battery_temperature_C=24.5,diagnostic_SOC_power_maps_unchanged=True,controller_denominator_floor_V=350,denominator_floor_is_not_BMS_cutoff=True,low_SOC_limiting_policy_still_unvalidated=True,not_for_EPA_range_or_lowSOC_final_validation=True,wiring_fixes=wiring,reference_sha256=sha(ref),CRC_XML_readback_passed=True,CRUISE_load_tested=False,CRUISE_solver_tested=False,gates=dict(energy_error_abs_percent_max=5,voltage_RMSE_V_max=2,voltage_bias_abs_V_max=1,speed_RMSE_kmh_max=1,distance_error_abs_percent_max=.5,integrated_DC_balance_abs_percent_max=1))
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
