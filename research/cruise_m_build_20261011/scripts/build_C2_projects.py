"""Build separate C2 saved-project copies; no original mutation or CRUISE run.

Keep IDs/links intact, find changed data by type, owner and table contents.
Actual CRUISE loading/solver and result export remain untested here.
"""
import base64,hashlib,json,sys,zipfile,os,copy
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from lxml import etree as E
from audit_dis80_semantic import SavedProject,ROOT

OUT=ROOT/'runs/C2_battery_common_20261014'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    source=Path(sys.argv[1]);cfg=json.loads((OUT/'parameters.json').read_text())
    assert cfg['candidate_screen_gate_met'] and sha(source)==cfg['source_project_sha256']
    cfg['status']='C2_PARAMETERS_FIXED_PENDING_CRUISE_CONFIRMATION'
    cfg['adoption_authorization']='Userauthorized autonomous completion of model calibration and validation preparation;C2 actual confirmation remains pending.'
    (OUT/'parameters.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
    (OUT/'projects').mkdir(exist_ok=True);(OUT/'inputs').mkdir(exist_ok=True)
    ocv=np.loadtxt(OUT/'inputs/C2_Cell_OCV_25C.dat',skiprows=2)
    resistance=np.loadtxt(OUT/'inputs/C2_Cell_Resistance_25C.dat',skiprows=2)
    assert np.all(np.diff(ocv[:,1])>0) and np.all(resistance[:,1]>0)
    prep=json.loads((ROOT/'runs/validation_closure_20261014/066_preparation.json').read_text())
    cases=[]
    for test,role in [('61905060','CAL'),('61905061','CAL'),('61905066','CAL'),('61905058','HOLD'),('61905059','HOLD')]:
        if test in ['61905058','61905059']:
            cp=next(x for x in json.loads((OUT/'fresh_holdout_input_QA.json').read_text()) if x['test']==test)
            driverpath=OUT/f'inputs/ANL{test}_driver_1s.csv';driver=pd.read_csv(driverpath);duration=cp['duration_s']
            vv=cp['initial_voltage_V'];ii=cp['initial_current_A'];temp=cp['initial_battery_temperature_C'];ambient=cp['initial_environment_temperature_C']
        elif test!='61905066':
            base=ROOT/f'independent_tests_20261013/ANL{test}'
            driverpath=base/'driver_1s.csv';driver=pd.read_csv(driverpath)
            cp=json.loads((base/'checkpoint.json').read_text());duration=cp['duration_s']
            vv=cp['initial_voltage_V'];ii=cp['initial_current_A'];temp=cp['initial_battery_temperature_C'];ambient=cp['test_cell_temperature_C']
        else:
            base=ROOT/'runs/validation_closure_20261014';driverpath=base/'inputs/ANL61905066_driver_1s.csv';driver=pd.read_csv(driverpath)
            duration=prep['continuous_duration_s'];vv=prep['initial_voltage_V'];ii=prep['initial_current_A'];temp=prep['initial_battery_temperature_C'];ambient=prep['initial_environment_temperature_C']
        initial=brentq(lambda s:96*np.interp(s,ocv[:,0],ocv[:,1])-ii*32*np.interp(s/100,resistance[:,0],resistance[:,1])-vv,0,100)
        p=SavedProject(source);modified=[]
        def set_array(oid,data):
            n=p.index[oid];assert n.tag=='numpy_array'
            a=np.asarray(data,dtype=n.get('dtype'));assert np.isfinite(a).all()
            n.set('dim',' '.join(map(str,a.shape)));n.text=base64.b64encode(a.tobytes()).decode()
            modified.append(oid)
        def set_amount(n,key,value):
            amount=p.resolve(p.fields(n)[key]);p.fields(amount)['value'].text=repr(float(value));modified.append(amount.get('id'))
        for typ,values in [('IdleVoltage',ocv[:,1]),('OhmicResistanceCharge',resistance[:,1]),('OhmicResistanceDischarge',resistance[:,1])]:
            nodes=p.nodes('cruise.props.commons_battery.'+typ);assert len(nodes)==2
            for n in nodes:
                aa=p.arrays_under(n);assert len(aa)==3 and len(aa[2][2])==len(values)
                data_node=p.resolve(p.fields(p.index[aa[2][0]])['data']);set_array(data_node.get('id'),values)
        for n in p.nodes('cruise.props.electric_machine.PowerLoss'):
            aa=p.arrays_under(n)
            if len(aa)!=5 or not len(aa[1][2]) or not np.all(aa[1][2]==400):continue
            label='Q1' if aa[3][2].min()>=0 else 'Q4';d=pd.read_csv(OUT/f'inputs/C1_EDU_{label}_loss_nodes.csv')
            assert np.max(abs(d.rpm-aa[2][2]))<1e-9 and np.max(abs(d.torque_Nm-aa[3][2]))<1e-9
            assert np.all(d.C1_loss_kW>0)
            q=p.resolve(p.fields(p.index[aa[4][0]])['data']);set_array(q.get('id'),d.C1_loss_kW.to_numpy())
        for general in p.nodes('cruise.props.battery.General'):
            selection=p.resolve(p.fields(general)['maximum_charge'])
            assert p.decode(p.fields(selection)['active'])=='const'
            set_amount(selection,'const',56*cfg['capacity_gain'])
        initials=p.nodes('cruise.props.battery.InitialConditions');assert len(initials)==2
        for n in initials:
            set_amount(n,'initial_charge',initial)
            owner=next(x for x in n.iterancestors('object') if x.get('type')=='act.topo.Element')
            temps=[x for x in owner.iter('object') if x.get('type')=='cruise.props.solid_wall.DefinedTemperature'];assert len(temps)==1
            set_amount(temps[0],'temperature',temp)
        # Replace the unique active060-shaped profile, not a label/order guess.
        original_driver=pd.read_csv(ROOT/'independent_tests_20261013/ANL61905060/driver_1s.csv');profiles=[]
        for n in p.nodes('cruise.props.tasks.profile.VelocityProfileTime'):
            aa=p.arrays_under(n)
            if len(aa)==7 and len(aa[0][2])==len(original_driver) and np.max(abs(aa[1][2]-original_driver.speed_kmh))<1e-9:profiles.append((n,aa))
        assert len(profiles)==1
        profile,aa=profiles[0];n=len(driver);t=driver.time_s.to_numpy();speed=driver.speed_kmh.to_numpy()
        columns=[t,speed,np.ones(n),np.zeros(n),np.r_[np.ones(n-1),0],speed,speed]
        for (oid,unit,a),values in zip(aa,columns):
            node=p.resolve(p.fields(p.index[oid])['data']);set_array(node.get('id'),values)
        fname=f'C2_{role}_{test}.dat';hdr='Time Velocity Gear "Shift Time" "Start Switch" "Min. Velocity" "Max. Velocity"\r\ns km/h - s - km/h km/h\r\n'
        lines=[f'{tt:.12f}\t{ss:.12f}\t1\t0\t{int(on)}\t{ss:.12f}\t{ss:.12f}' for tt,ss,on in zip(t,speed,columns[4])]
        (OUT/'inputs'/fname).write_bytes((hdr+'\r\n'.join(lines)+'\r\n').encode())
        owner=next(x for x in profile.iterancestors('object') if x.get('type')=='act.topo.Element')
        # Name property is a profile display field; keep topology UUID and refs.
        names=[x for x in owner.iter('object') if x.get('type')=='cruise.props.tasks.profile.General']
        assert len(names)==1;name=p.fields(names[0])['name'];assert name.tag=='str' and name.get('coding') is None
        name.text=f'C2_{role}_{test}'
        ends=[n for n in p.nodes('cruise.props.tasks.tasks_settings.EndTimeSelection') if p.decode(p.fields(n)['active'])=='end_time' and abs(p.amount(n,'end_time')-3150.896995)<1e-5]
        assert len(ends)==1;set_amount(ends[0],'end_time',duration)
        # Primary environment belongs to the same task element as the profile.
        task=next(x for x in owner.iterancestors('object') if x.get('type')=='act.topo.Element')
        envs=[x for x in task.iter('object') if x.get('type')=='cruise.props.tasks.environment.AmbientTemperatureHumidity'];assert len(envs)==1
        ef=p.fields(envs[0]);based=p.decode(ef['based_on'])['items'][0];assert based=='distance'
        ea=p.arrays_under(ef['distance_based']);assert len(ea)==3 and len(ea[1][2])==1
        node=p.resolve(p.fields(p.index[ea[1][0]])['data']);set_array(node.get('id'),[ambient])
        destination=OUT/'projects'/f'C2_{role}_{test}.proj'
        temporary=destination.with_suffix('.proj.part')
        with zipfile.ZipFile(source) as zin,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():zout.writestr(copy.copy(item),E.tostring(p.root,encoding='utf-8',xml_declaration=True) if item.filename=='project.xml' else zin.read(item.filename))
        assert temporary.stat().st_size>100000
        with temporary.open('rb') as f:os.fsync(f.fileno())
        with zipfile.ZipFile(temporary) as z:assert z.testzip() is None
        os.replace(temporary,destination)
        directory_fd=os.open(destination.parent,os.O_DIRECTORY)
        try:os.fsync(directory_fd)
        finally:os.close(directory_fd)
        # Inspect the written project and verify all expected embedded values.
        check=SavedProject(destination)
        assert all(abs(check.amount(x,'initial_charge')-initial)<1e-10 for x in check.nodes('cruise.props.battery.InitialConditions'))
        for typ,values in [('IdleVoltage',ocv[:,1]),('OhmicResistanceCharge',resistance[:,1]),('OhmicResistanceDischarge',resistance[:,1])]:
            for x in check.nodes('cruise.props.commons_battery.'+typ):assert np.max(abs(check.arrays_under(x)[2][2]-values))<1e-12
        for general in check.nodes('cruise.props.battery.General'):
            selection=check.resolve(check.fields(general)['maximum_charge'])
            assert abs(check.amount(selection,'const')-56*cfg['capacity_gain'])<1e-10
        read_profile=check.index[profile.get('id')];readcols=check.arrays_under(read_profile);assert len(readcols)==7
        assert all(np.array_equal(a[2],v) for a,v in zip(readcols,columns))
        for x in check.nodes('cruise.props.electric_machine.PowerLoss'):
            ma=check.arrays_under(x)
            if len(ma)!=5 or not len(ma[1][2]) or not np.all(ma[1][2]==400):continue
            label='Q1' if ma[3][2].min()>=0 else 'Q4';expected=pd.read_csv(OUT/f'inputs/C1_EDU_{label}_loss_nodes.csv').C1_loss_kW.to_numpy()
            assert np.max(abs(ma[4][2]-expected))<1e-12
        assert np.array_equal(check.arrays_under(check.nodes('cruise.props.general_map.GeneralCharacteristic')[2])[1][2],[0,0,24,80,80,80,80])
        assert check.amount(check.nodes('cruise.props.basic_electric_components.PowerConsumerGeneral')[0],'power')==.4
        assert abs(check.amount(check.index[ends[0].get('id')],'end_time')-duration)<1e-9
        # Require unchanged object definitions and references; topology remains intact.
        before=SavedProject(source)
        assert before.index.keys()==check.index.keys()
        assert [x.get('id') for x in before.root.iter('ref')]==[x.get('id') for x in check.root.iter('ref')]
        with zipfile.ZipFile(source) as original_zip,zipfile.ZipFile(destination) as result_zip:
            for member in original_zip.namelist():
                if member!='project.xml':assert original_zip.read(member)==result_zip.read(member)
        cases.append(dict(test=test,role=role,project=destination.name,project_sha256=sha(destination),input_profile=fname,input_profile_sha256=sha(OUT/'inputs'/fname),
          initial_SOC_percent=initial,battery_temperature_C=temp,environment_temperature_C=ambient,end_time_s=duration,rows=n,
          modified_amount_or_array_ids=modified,zip_XML_readback_passed=True,CRUISE_load_tested=False,CRUISE_solver_tested=False,
          note='Embeddedprofiles/mapsincluded;separateDATnotrequiredtoopen.C2CAL060/061/066;freshHOLD058/059onlyafterCALconfirmation.'))
    pd.DataFrame([{k:v for k,v in c.items() if k!='modified_amount_or_array_ids'} for c in cases]).to_csv(OUT/'RUNS.csv',index=False)
    contract={'candidate':'C2','066_is_training':True,'fresh_holdouts':['61905058','61905059'],'parameters_frozen_before_fresh_holdout_model_comparison':True,'model_validation_complete':False,'calibration_confirmation_passed':False,
      'source_project_sha256':sha(source),'parameter_json_sha256':sha(OUT/'parameters.json'),'cases':cases,
      'map_sha256':{p.name:sha(p) for p in (OUT/'inputs').glob('*') if 'CAL' not in p.name and 'HOLD' not in p.name},
      'gates':{'energy_error_abs_percent_max':5,'voltage_RMSE_V_max':2,'voltage_bias_abs_V_max':1,'integrated_DC_balance_abs_percent_max':1,'speed_RMSE_kmh_max':1,'distance_error_abs_percent_max':.5},
      'gates_are_research_proposals_not_certification':True,'rule':'RunC2CAL060/061/066first;ifallpass,runfreshHOLD058/059.066isC2training;C1independentFAILpreserved.',
      'physical_component_identification':False,'scope':'Candidateparametersfixed;actualCRUISErunsandholdoutevaluationpending.'}
    contract['reference_sha256']={p.name:sha(p) for p in (OUT/'references').glob('*.csv')}
    contract['fit_at_boundary']=cfg['OCV_bound_active']
    (OUT/'candidate_contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':cases,'contract':'candidate_contract.json'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
