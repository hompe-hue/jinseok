"""Package known research records; never label archived files as newly executed runs."""
from pathlib import Path
import json,shutil
import pandas as pd
from research import Harness,sha,write

P=Path(__file__).resolve().parent
ROOT=P.parent
SRC=ROOT.parent/'feedback/research'
ACTUAL=SRC/'public_validation_batch_20261016/actual_20261016'

def copy(source,dest):
    dest=P/dest;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    return str(dest.relative_to(P))

def main():
    if (P/'registry.json').exists():raise SystemExit('Bootstrap is one-time; existing history will not be reset.')
    policy=dict(schema_version=1,current_policy_date_KST='2026-11-02',
        accuracy_limits=dict(energy_error_percent=5.,voltage_RMSE_V=2.,voltage_bias_V=1.,speed_RMSE_kmh=1.),
        integration_start_s=20,voltage_and_speed_metric_grid_s=1,
        exported_battery_current_sign=-1,model_adoption='HUMAN_DECISION_ONLY',
        diagnostic_ranges_are_measured_uncertainty=False,physical_cause_percent_identified=False,
        external_sending_or_publishing_enabled=False,CRUISE_execution='MANUAL_UNTIL_INTERFACE_VERIFIED')
    write(P/'policy.json',policy)
    history=pd.read_csv(ACTUAL/'four_case_metrics.csv').set_index('test')
    references={};initial={};ends={}
    for code in ['058','059','060','066']:
        record=history.loc[int('61905'+code)];initial[code]=float(record.SOC_initial_percent);ends[code]=float(record.end_s)
        references[code]=copy(ACTUAL/'references'/('ANL61905'+code+'_reference_native.csv'),
            'assets/offline_inputs/references/ANL61905'+code+'_reference_native.csv')
        copy(ACTUAL/code/('battery_PUBLIC_'+code+'.csv'),'assets/offline_inputs/'+code+'/battery_PUBLIC_'+code+'.csv')
    specs={}
    names=['R0_BASE','R1_ROAD_M10','R2_ROAD_P10','R3_AUX_M10','R4_AUX_P10','R5_REGENLOSS_M10','R6_REGENLOSS_P10']
    for name in names:
        model=ROOT/'steps/03_coupled_sensitivity/projects'/(name+'.proj')
        rel=copy(model,'assets/projects/'+model.name)
        specs[name]=dict(test='61905060',test_name='40마일 주행시험(1차)',kind='baseline' if name=='R0_BASE' else 'sensitivity',
            end_s=ends['060'],initial_SOC_percent=initial['060'],reference=references['060'],
            project=rel,project_sha256=sha(model),auxiliary_kW=.36 if name=='R3_AUX_M10' else .44 if name=='R4_AUX_P10' else .4,
            maximum_export_gap_s=1.001)
    for code in ['058','059','066']:
        model=SRC/'public_validation_batch_20261016'/('BEV_PUBLIC_'+code+'.proj')
        rel=copy(model,'assets/projects/'+model.name);name='PUBLIC_'+code
        specs[name]=dict(test='61905'+code,test_name=str(history.loc[int('61905'+code)].test_name),kind='baseline',
            end_s=ends[code],initial_SOC_percent=initial[code],reference=references[code],
            project=rel,project_sha256=sha(model),auxiliary_kW=.4,maximum_export_gap_s=1.001)
    for stride,gap in [('10',.101),('1',.011)]:
        name='SMCT_DENSE_SAVED'+stride;model=ROOT/'steps/07_output_sampling/projects'/(name+'.proj')
        rel=copy(model,'assets/projects/'+model.name)
        specs[name]=dict(test='61905066',test_name='휴지 없는SMCT 세밀 출력',kind='output_sampling',
            end_s=ends['066'],initial_SOC_percent=initial['066'],reference=references['066'],
            project=rel,project_sha256=sha(model),auxiliary_kW=.4,maximum_export_gap_s=gap,
            actual_dense_run_received=False)
    registry=dict(schema_version=1,runs=specs,pairs=[['ABC_common_scale','R1_ROAD_M10','R2_ROAD_P10'],
        ['auxiliary_scale','R3_AUX_M10','R4_AUX_P10'],['regen_Q4_node_loss_scale','R5_REGENLOSS_M10','R6_REGENLOSS_P10']],
        R0_user_confirmation=dict(date_KST='2026-11-02',text='제공한 R0를 수정 없이 실행했다는 사용자 확인을 수용. 같은 확인 반복 요청 금지.'))
    write(P/'registry.json',registry)
    recipes={}
    for key,rel in [('battery_replay','steps/04_public_battery_replay/analyze.py'),
        ('soc_identifiability','steps/05_battery_identifiability/analyze.py'),
        ('CAN_SOC_consistency','steps/05_battery_identifiability/check_can_soc.py'),
        ('timing_recovery','steps/06_timing_recovery/analyze.py'),
        ('energy_VI_accounting','steps/06_timing_recovery/decompose_energy.py')]:
        dest=copy(ROOT/rel,'assets/recipes/'+key+'.py');recipes[key]=dict(script=dest)
    stop=copy(ROOT/'steps/05_battery_identifiability/stopped_low_current_windows.csv','assets/stopped_windows.csv')
    recipes['timing_recovery']['stopped_windows']=stop
    write(P/'recipes.json',recipes)
    frozen={str(f.relative_to(P)):sha(f) for f in (P/'assets').rglob('*') if f.is_file()}
    frozen.update({n:sha(P/n) for n in ['registry.json','policy.json','recipes.json']})
    write(P/'assets_manifest.json',frozen)
    h=Harness(P)
    for run in names:
        directory=ROOT/'steps/03_coupled_sensitivity/exports'/run
        evidence=dict(association='Active conversation and attachment identifiers; archived historical import, not a new CRUISE execution')
        if run=='R0_BASE':evidence.update(user_unmodified_confirmation_date_KST='2026-11-02',
            earlier_result_writing_failure_reported=True,later_successful_final_log_received=False)
        h.ingest(run,{k:directory/(k+'.csv') for k in ['battery','velocity','generator']},
                 confirmed=run=='R0_BASE',origin='HISTORICAL_USER_EXPORT',evidence=evidence)
    for code in ['058','059','066']:
        h.ingest('PUBLIC_'+code,{k:ACTUAL/code/(k+'_PUBLIC_'+code+'.csv') for k in ['battery','velocity','generator']},
                 origin='ARCHIVED_PUBLIC_VALIDATION_EXPORT',evidence={'import_is_new_execution':False})
    print(json.dumps(dict(registered_runs=len(specs),historical_export_sets_imported=10,actual_dense_sets_received=0,
        new_CRUISE_runs=0,assets_verified=h.verify())))

if __name__=='__main__':main()
