"""Local BEV research harness. Analyze and record; never run CRUISE or adopt parameters."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,sys,subprocess,tempfile,platform
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import scipy

HARNESS_DIR=Path(__file__).resolve().parent
VERSION='1.0.0'

class InvalidRun(ValueError):pass

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def utc():return datetime.now(timezone.utc).isoformat()
def environment():return dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__)

def signal(d,name):
    c=[c for c in d if c==name or c.startswith('In/'+name+' (')]
    if len(c)!=1:raise InvalidRun('Missing/ambiguous signal: '+name)
    v=d[c[0]].to_numpy(float)
    if not np.isfinite(v).all():raise InvalidRun('Nonfinite signal: '+name)
    return v

def table(path,required_units):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        rows=csv.reader(f);headers=next(rows);units=next(rows)
    if len(headers)!=len(units):raise InvalidRun('Signal/unit row lengths differ')
    if len(set(headers))!=len(headers):raise InvalidRun('Duplicate CSV headers')
    d=pd.read_csv(path,skiprows=[1],encoding='utf-8-sig')
    if len(d)<2:raise InvalidRun('Not enough samples')
    for name,expected in required_units.items():
        c=[c for c in headers if c==name or c.startswith('In/'+name+' (')]
        if len(c)!=1:raise InvalidRun('Missing/ambiguous signal: '+name)
        actual=units[headers.index(c[0])].strip()
        if actual not in expected:raise InvalidRun(f'Unit mismatch for {name}: {actual}; expected {expected}')
        signal(d,name)
    return d

def integral(t,y,start,end):
    if t[0]>start or t[-1]<end or np.any(np.diff(t)<=0):raise InvalidRun('Integration window incomplete/nonmonotonic')
    x=np.r_[start,t[(t>start)&(t<end)],end]
    return float(np.trapezoid(np.interp(x,t,y),x)/3600)

def log_review(path):
    if path is None:return {'status':'NOT_PROVIDED','final_success_verified':False}
    text=Path(path).read_text(encoding='utf-8',errors='replace')
    fatal='[fatal error]' in text.lower() or '[error]' in text.lower()
    return dict(status='REPORTED_FAILURE' if fatal else 'NO_FATAL_FOUND_SUCCESS_NOT_INFERRED',
        solver_loop_ended='Simulation ended.' in text,
        series_write_message='Series result writing successful.' in text,
        result_write_failure='Result writing failed.' in text,
        final_success_verified=False)

def metrics(spec,paths,reference):
    common={'Time':['s']}
    b=table(paths['battery'],dict(common,Current=['A'],Voltage=['V'],SoC=['%']))
    v=table(paths['velocity'],dict(common,**{'Actual Velocity':['km/h'],'Desired Velocity':['km/h'],
        'E-Motor Current':['A'],'E-Consumer Current':['A']}))
    g=table(paths['generator'],dict(common,Current=['A'],**{'Power Generator':['kW'],'Power ICE':['kW']}))
    t=signal(b,'Time');end=spec['end_s'];start=20.
    if t[0]!=0 or t[-1]<end or np.any(np.diff(t)<=0):raise InvalidRun('Need increasing full0–end timestamps')
    if not np.array_equal(t,signal(v,'Time')) or not np.array_equal(t,signal(g,'Time')):raise InvalidRun('Three CSV time grids differ')
    maxdt=float(np.max(np.diff(t)))
    if maxdt>spec['maximum_export_gap_s']+1e-8:raise InvalidRun('Output resolution too coarse or contains gaps')
    u=signal(b,'Voltage');i=-signal(b,'Current');soc=signal(b,'SoC')
    if abs(soc[0]-spec['initial_SOC_percent'])>1e-5:raise InvalidRun('Initial SOC differs from registered case')
    if np.any(u<=0) or np.any((soc<0)|(soc>100)):raise InvalidRun('Voltage/SOC outside numerical domain')
    ref=pd.read_csv(reference);rt=ref.iloc[:,0].to_numpy(float)
    if rt[0]>0 or rt[-1]<end or np.any(np.diff(rt)<=0):raise InvalidRun('Reference coverage invalid')
    for name in ['meter_power_kW_discharge_positive','meter_voltage_V','speed_kmh']:
        if not np.isfinite(ref[name].to_numpy(float)).all():raise InvalidRun('Reference nonfinite '+name)
    e=integral(t,u*i/1000,start,end)
    er=integral(rt,ref.meter_power_kW_discharge_positive.to_numpy(float),start,end)
    if er<=0 or e<=0:raise InvalidRun('Positive net driving energy required')
    # Voltage/speed metrics use fixed1s evaluation grid for resolution-independent comparison.
    grid=np.arange(end+1.);vg=grid>20
    ug=np.interp(grid,t,u);actual=np.interp(grid,t,signal(v,'Actual Velocity'))
    desired=np.interp(grid,t,signal(v,'Desired Velocity'))
    uv=ug-np.interp(grid,rt,ref.meter_voltage_V)
    speed=actual-desired
    rmse=lambda x:float(np.sqrt(np.mean(x*x)))
    off=all(np.max(abs(signal(g,n)))<1e-8 for n in ['Actual Engine Speed','Desired Engine Speed',
        'Power Generator','Power ICE','Current','Fuel Massflow','Cumulated Fuel Consumption'])
    aux=u*signal(v,'E-Consumer Current')/1000
    m=(t>=20)&(t<=end)
    balance=u*(i-signal(v,'E-Motor Current')-signal(v,'E-Consumer Current'))/1000
    profile=rmse(desired-np.interp(grid,rt,ref.speed_kmh))
    result=dict(battery_net_kWh=e,reference_net_kWh=er,energy_error_percent=100*(e/er-1),
        voltage_RMSE_V=rmse(uv[vg]),voltage_bias_V=float(uv[vg].mean()),
        speed_RMSE_kmh=rmse(speed),desired_vs_reference_RMSE_kmh=profile,
        SOC_initial_percent=float(soc[0]),SOC_final_percent=float(np.interp(end,t,soc)),
        generator_OFF=bool(off),auxiliary_mean_kW=float(aux[m].mean()),
        auxiliary_max_error_kW=float(np.max(abs(aux[m]-spec['auxiliary_kW']))),
        DC_balance_percent=100*abs(integral(t,balance,start,end))/e,
        DC_balance_absolute_energy_percent=100*integral(t,abs(balance),start,end)/e,
        median_export_dt_s=float(np.median(np.diff(t))),maximum_export_gap_s=maxdt,rows=len(t))
    protocol=dict(generator_OFF=bool(off),reference_profile_matches=profile<=.01,
        auxiliary_matches=result['auxiliary_max_error_kW']<=1e-4,
        DC_balance=result['DC_balance_absolute_energy_percent']<=1)
    if spec['kind']=='baseline' and spec['test']=='61905060':
        archived=table(Path(reference).parent.parent/'060/battery_PUBLIC_060.csv',dict(common,Current=['A'],Voltage=['V'],SoC=['%']))
        ae=integral(signal(archived,'Time'),signal(archived,'Voltage')*(-signal(archived,'Current'))/1000,start,end)
        result['baseline_energy_reproduction_difference_percent']=100*(e/ae-1)
        protocol['baseline_energy_reproduced']=abs(result['baseline_energy_reproduction_difference_percent'])<=.1
    if spec['kind']=='output_sampling':
        coarse=integral(grid,np.interp(grid,t,u)*np.interp(grid,t,i)/1000,start,end)
        archived=table(Path(reference).parent.parent/'066/battery_PUBLIC_066.csv',dict(common,Current=['A'],Voltage=['V'],SoC=['%']))
        ae=integral(signal(archived,'Time'),signal(archived,'Voltage')*(-signal(archived,'Current'))/1000,start,end)
        result.update(same_run_1s_decimated_energy_kWh=coarse,
            dense_minus_same_run_1s_kWh=e-coarse,dense_minus_same_run_1s_percent=100*(e/coarse-1),
            archived_1s_energy_kWh=ae,new_1s_minus_archived_1s_percent=100*(coarse/ae-1),
            output_integration_screen_pass=bool(abs(100*(e/coarse-1))<=.1),
            solver_timestep_convergence_verified=False,two_finest_output_levels_compared=False)
        protocol['archived_output_comparison_consistent']=abs(result['new_1s_minus_archived_1s_percent'])<=.1
    return result,protocol

class Harness:
    def __init__(self,root=HARNESS_DIR):
        self.root=Path(root);self.registry=read(self.root/'registry.json');self.policy=read(self.root/'policy.json')
    def verify(self):
        bad=[]
        for relative,expected in read(self.root/'assets_manifest.json').items():
            p=self.root/relative
            if not p.is_file() or sha(p)!=expected:bad.append(relative)
        for manifest in (self.root/'runs').glob('*/attempts/*/manifest.json'):
            for obj in read(manifest)['assets'].values():
                p=self.root/obj['path']
                if not p.is_file() or sha(p)!=obj['sha256']:bad.append(obj['path'])
        if bad:raise InvalidRun('Registered asset changed/missing: '+', '.join(bad))
        return True
    def index(self,run):
        p=self.root/'runs'/run/'index.json'
        return read(p) if p.exists() else None
    def ingest(self,run,files,project=None,log=None,confirmed=False,origin='user_supplied',evidence=None):
        self.verify()
        if run not in self.registry['runs']:raise InvalidRun('Unknown run identifier')
        assets={}
        for name,path in dict(files,**({'project':project} if project else {}),**({'log':log} if log else {})).items():
            path=Path(path)
            if not path.is_file():raise InvalidRun('Missing input: '+str(path))
            checksum=sha(path);dest=self.root/'data'/(checksum+path.suffix.lower())
            dest.parent.mkdir(exist_ok=True)
            if dest.exists():
                if sha(dest)!=checksum:raise InvalidRun('Immutable data object was modified')
            else:shutil.copyfile(path,dest)
            assets[name]=dict(path=str(dest.relative_to(self.root)),sha256=checksum,original_name=path.name)
        key=digest(dict(run=run,assets={n:x['sha256'] for n,x in assets.items()},confirmed=confirmed))[:20]
        manifest=self.root/'runs'/run/'attempts'/key/'manifest.json'
        if not manifest.exists():write(manifest,dict(run=run,attempt=key,received_at_UTC=utc(),
            origin=origin,assets=assets,user_confirmed_unmodified=bool(confirmed),evidence=evidence or {},
            CRUISE_launched_by_harness=False))
        old=self.index(run)
        if not old or old['attempt']!=key:write(self.root/'runs'/run/'index.json',dict(attempt=key))
        return key
    def review(self,run):
        self.verify();idx=self.index(run)
        if not idx:raise InvalidRun('No received data for '+run)
        manifest=read(self.root/'runs'/run/'attempts'/idx['attempt']/'manifest.json')
        for obj in manifest['assets'].values():
            p=self.root/obj['path']
            if not p.is_file() or sha(p)!=obj['sha256']:raise InvalidRun('Received data changed after ingest')
        stamp=digest(dict(engine=sha(Path(__file__)),registry=sha(self.root/'registry.json'),
            policy=sha(self.root/'policy.json'),assets=sha(self.root/'assets_manifest.json'),
            environment=environment(),attempt=manifest['attempt']))[:20]
        target=self.root/'runs'/run/'attempts'/manifest['attempt']/'reviews'/(stamp+'.json')
        if target.exists():
            if idx.get('review')==str(target.relative_to(self.root)) and idx.get('review_sha256')!=sha(target):
                raise InvalidRun('Cached review artifact was modified')
            result=read(target)
        else:
            spec=self.registry['runs'][run];paths={k:self.root/manifest['assets'][k]['path'] for k in ['battery','velocity','generator']}
            snapshot=self.root/'versions'/stamp;snapshot.mkdir(parents=True,exist_ok=True)
            for source in [Path(__file__),self.root/'registry.json',self.root/'policy.json',self.root/'assets_manifest.json']:
                destination=snapshot/source.name
                if not destination.exists():shutil.copyfile(source,destination)
            result=dict(run=run,attempt=manifest['attempt'],review_id=stamp,harness_version=VERSION,
                engine_sha256=sha(Path(__file__)),registry_sha256=sha(self.root/'registry.json'),
                policy_sha256=sha(self.root/'policy.json'),assets_manifest_sha256=sha(self.root/'assets_manifest.json'),
                environment=environment(),configuration_snapshot=str(snapshot.relative_to(self.root)),
                user_confirmed_unmodified=manifest['user_confirmed_unmodified'],origin=manifest['origin'],
                automatic_parameter_adoption=False,physical_cause_contribution_identified=False,
                CRUISE_launched_by_harness=False,execution_binding_verified_by_harness=False)
            try:
                m,protocol=metrics(spec,paths,self.root/spec['reference'])
                gates={k:bool(abs(m[k])<=limit) for k,limit in self.policy['accuracy_limits'].items()}
                result.update(data_status='VALIDATED_EXPORT',metrics=m,protocol_checks=protocol,
                    numerical_comparison_usable=all(protocol.values()),accuracy_checks=gates,
                    model_accuracy_targets_met=all(gates.values()))
            except (ValueError,KeyError,StopIteration,pd.errors.ParserError) as exc:
                result.update(data_status='INVALID_EXPORT',failure_reason=str(exc),numerical_comparison_usable=False,
                    model_accuracy_targets_met=False)
            project=manifest['assets'].get('project')
            result['project_evidence']='NOT_PROVIDED'
            if project:result['project_evidence']='EXACT_PREPARED_BYTES_PROVIDED' if project['sha256']==spec['project_sha256'] else 'DIFFERENT_BYTES_SEMANTIC_REVIEW_NEEDED'
            elif manifest['user_confirmed_unmodified']:result['project_evidence']='USER_CONFIRMED_UNMODIFIED'
            log=manifest['assets'].get('log')
            result['log_review']=log_review(self.root/log['path'] if log else None)
            result['historical_execution_notes']=manifest.get('evidence',{})
            write(target,result)
        idx['review']=str(target.relative_to(self.root));idx['review_sha256']=sha(target)
        write(self.root/'runs'/run/'index.json',idx)
        return result
    def latest(self,run):
        idx=self.index(run)
        if not idx or 'review' not in idx:return None
        if not idx.get('review_sha256') or sha(self.root/idx['review'])!=idx['review_sha256']:
            raise InvalidRun('Review artifact changed or unversioned; run review again')
        return read(self.root/idx['review'])
    def sensitivities(self):
        self.verify()
        base=self.latest('R0_BASE');out=[]
        for name,lo,hi in self.registry['pairs']:
            a,b=self.latest(lo),self.latest(hi)
            if not all(x and x.get('numerical_comparison_usable') for x in [base,a,b]):continue
            e0=base['metrics']['battery_net_kWh'];em=a['metrics']['battery_net_kWh'];ep=b['metrics']['battery_net_kWh']
            out.append(dict(factor=name,central_delta_kWh_at_10percent=(ep-em)/2,
                normalized_elasticity=(ep-em)/(.2*e0),actual_cause_contribution_identified=False))
        return out
    def next_action(self):
        run='SMCT_DENSE_SAVED10';v=self.latest(run)
        if not v:return dict(run=run,state='AWAITING_MANUAL_CRUISE_RUN',action='SMCT_DENSE_SAVED10.proj 한 건의 실제 세밀 CSV를 기다립니다. 기존 R0·감도7건 재실행은 요청하지 않습니다.')
        if not v.get('numerical_comparison_usable'):return dict(run=run,state='REVIEW_DATA_OR_PROTOCOL',action='검증 실패 사유를 확인합니다. 물리 파라미터를 자동 수정하지 않습니다.')
        if v['log_review']['status']=='REPORTED_FAILURE':return dict(run=run,state='EXECUTION_WRITE_FAILURE_REVIEW',action='수치 결과와 결과 저장 실패를 구분해 검토합니다. 정상 완료로 승격하지 않습니다.')
        m=v['metrics']
        if not m['output_integration_screen_pass']:return dict(run='SMCT_DENSE_SAVED1',state='FINER_OUTPUT_COMPARISON_NEEDED',action='출력 적분 차이가 제안 기준0.1%를 넘었습니다. SAVED1의 추가 비교를 검토합니다.')
        return dict(run=run,state='OUTPUT_SCREEN_REVIEWED',action='출력 적분1차 점검을 통과했습니다. 두 세밀 수준·solver 시간간격 수렴 완료로 표현하지 않고 남은 물리 모델 오차를 검토합니다.')
    def report(self):
        self.verify()
        lines=['# BEV 연구 하네스 현재 상태','',
            '자동 모델 보정·CRUISE 실행·GitHub 게시를 수행하지 않습니다. 수치 검사와 실차 모델 채택을 구분합니다.','',
            '|시험|자료 상태|에너지 오차 %|전압 RMSE V|전압 편향 V|정확도 목표|','|---|---|---:|---:|---:|---|']
        for run in self.registry['runs']:
            v=self.latest(run)
            if not v:lines.append(f'|{run}|실제 CSV 대기|||||');continue
            if 'metrics' not in v:lines.append(f'|{run}|자료 검증 실패|||||');continue
            m=v['metrics'];lines.append(f"|{run}|CSV 수치 검토|{m['energy_error_percent']:+.4f}|{m['voltage_RMSE_V']:.4f}|{m['voltage_bias_V']:+.4f}|{'충족' if v['model_accuracy_targets_met'] else '미달'}|")
        lines+=['','## 같은 ±10%의 국소 감도','','|항목|중앙 영향폭 kWh|정규화 감도|','|---|---:|---:|']
        for x in self.sensitivities():lines.append(f"|{x['factor']}|{x['central_delta_kWh_at_10percent']:.8f}|{x['normalized_elasticity']:.6f}|")
        lines+=['','실제 원인별 기여율이 아닙니다. 한40마일 시험의 지정된 섭동 범위에 대한 비교입니다.','',
            '## 다음 작업','',self.next_action()['action'],'',
            'R0는 제공 파일을 수정 없이 실행했다는 사용자 확인을 수용했습니다. 이전 결과 저장 실패 로그와 성공 여부는 별도로 기록합니다.','',
            '상태 정의: 준비본→CSV 접수→자료 검증→수치·프로토콜 검토. 모델 채택은 자동화하지 않습니다.']
        folder=self.root/'reports';folder.mkdir(exist_ok=True)
        (folder/'CURRENT_KO.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        write(folder/'state.json',dict(harness_version=VERSION,generated_at_UTC=utc(),
            next_action=self.next_action(),sensitivities=self.sensitivities(),
            runs={k:self.latest(k) for k in self.registry['runs']},automatically_adopted=False))
        return folder/'CURRENT_KO.md'

    def analyze(self,name):
        self.verify();recipes=read(self.root/'recipes.json')
        if name not in recipes:raise InvalidRun('Unknown analysis recipe')
        recipe=recipes[name];source=self.root/recipe['script']
        key=digest(dict(recipe=sha(source),assets=sha(self.root/'assets_manifest.json'),engine=sha(Path(__file__)),environment=environment()))[:20]
        dest=self.root/'reports/analyses'/name/key
        if (dest/'record.json').exists():return read(dest/'record.json')
        with tempfile.TemporaryDirectory(prefix='bev_harness_') as td:
            stage=Path(td)/'stage';stage.mkdir()
            shutil.copyfile(source,stage/'analyze.py')
            # Isolated work folder prevents historical scripts from rewriting sources.
            shutil.copytree(self.root/'assets/offline_inputs',stage/'inputs')
            if recipe.get('stopped_windows'):
                shutil.copyfile(self.root/recipe['stopped_windows'],stage/'stopped_windows_input.csv')
            result=subprocess.run([sys.executable,str(stage/'analyze.py')],cwd=stage,capture_output=True,text=True)
            if result.returncode:raise InvalidRun('Analysis failed '+name+': '+result.stderr[-1200:])
            dest.mkdir(parents=True,exist_ok=True)
            for f in stage.iterdir():
                if f.is_file() and f.name!='stopped_windows_input.csv' and f.suffix in ['.csv','.json','.md']:shutil.copyfile(f,dest/f.name)
            (dest/'execution.txt').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
            record=dict(recipe=name,analysis_id=key,source_sha256=sha(source),
                assets_manifest_sha256=sha(self.root/'assets_manifest.json'),returncode=0,
                environment=environment(),
                outputs={f.name:sha(f) for f in dest.iterdir() if f.is_file()},
                new_CRUISE_runs=0,parameter_fitting=False,automatic_parameter_adoption=False)
            write(dest/'record.json',record)
        return record

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--root',type=Path,default=HARNESS_DIR)
    sub=a.add_subparsers(dest='cmd',required=True)
    for name in ['status','verify','review-all','sensitivities','report','resume','refresh']:sub.add_parser(name)
    x=sub.add_parser('analyze');x.add_argument('--stage',required=True)
    x=sub.add_parser('ingest');x.add_argument('--run',required=True)
    for n in ['battery','velocity','generator']:x.add_argument('--'+n,type=Path,required=True)
    x.add_argument('--project',type=Path);x.add_argument('--log',type=Path)
    x.add_argument('--confirm-unmodified',action='store_true',help='Only with an actual user confirmation, not inferred from equal metrics')
    x=sub.add_parser('review');x.add_argument('--run',required=True)
    args=a.parse_args();h=Harness(args.root)
    try:
        if args.cmd=='verify':print(json.dumps({'assets_verified':h.verify()}))
        elif args.cmd=='analyze':print(json.dumps(h.analyze(args.stage),ensure_ascii=False,indent=2))
        elif args.cmd=='refresh':
            results={k:h.review(k)['data_status'] for k in h.registry['runs'] if h.index(k)}
            analyses={k:h.analyze(k)['analysis_id'] for k in read(h.root/'recipes.json')}
            report=h.report();print(json.dumps(dict(runs=results,analyses=analyses,report=str(report),next_action=h.next_action()),ensure_ascii=False))
        elif args.cmd=='ingest':
            key=h.ingest(args.run,{n:getattr(args,n) for n in ['battery','velocity','generator']},args.project,args.log,args.confirm_unmodified)
            result=h.review(args.run);h.report();print(json.dumps(dict(attempt=key,review=result),ensure_ascii=False,indent=2))
        elif args.cmd=='review':print(json.dumps(h.review(args.run),ensure_ascii=False,indent=2))
        elif args.cmd=='review-all':
            results={k:h.review(k)['data_status'] for k in h.registry['runs'] if h.index(k)}
            h.report();print(json.dumps(results,ensure_ascii=False))
        elif args.cmd=='sensitivities':print(json.dumps(h.sensitivities(),ensure_ascii=False,indent=2))
        elif args.cmd=='report':print(h.report())
        elif args.cmd=='resume':h.verify();print(json.dumps(h.next_action(),ensure_ascii=False,indent=2))
        elif args.cmd=='status':
            h.verify();print(json.dumps({k:(h.latest(k) or {}).get('data_status','AWAITING_EXPORT') for k in h.registry['runs']},ensure_ascii=False,indent=2))
    except (InvalidRun,OSError,json.JSONDecodeError) as exc:
        print('Harness rejected operation: '+str(exc),file=sys.stderr);raise SystemExit(2)

if __name__=='__main__':main()
