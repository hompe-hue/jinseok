"""End-time-only diagnostic copy; never substitute this window for full067 validation."""
import argparse,copy,hashlib,json,os,shutil,zipfile
from pathlib import Path
from lxml import etree as E
from audit_dis80_semantic import SavedProject
SOURCE_SHA='48adab1848b68edac991e7d937ad5a56d363ba16af554e4226863f00cee6338c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-directory',type=Path,required=True);ap.add_argument('--output-directory',type=Path,required=True);a=ap.parse_args()
    src=a.source_directory/'C3_LIMITS_ANL61905067.proj';assert sha(src)==SOURCE_SHA
    out=a.output_directory;out.mkdir(parents=True,exist_ok=True)
    before=SavedProject(src);p=SavedProject(src)
    candidates=[n for n in p.nodes('cruise.props.tasks.tasks_settings.EndTimeSelection') if p.decode(p.fields(n)['active'])=='end_time' and abs(p.amount(n,'end_time')-10122.190356254578)<1e-6]
    assert len(candidates)==1
    setting=candidates[0];amount=p.resolve(p.fields(setting)['end_time']);value=p.fields(amount)['value'];assert value.tag=='num'
    value.text='9500.0'
    dest=out/'C3_DIAG_ANL61905067_END9500.proj';tmp=dest.with_suffix('.proj.part')
    with zipfile.ZipFile(src) as zi,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
        for info in zi.infolist():zo.writestr(copy.copy(info),E.tostring(p.root,encoding='utf-8',xml_declaration=True) if info.filename=='project.xml' else zi.read(info.filename))
    with tmp.open('rb') as f:os.fsync(f.fileno())
    with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
    os.replace(tmp,dest);fd=os.open(out,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
    after=SavedProject(dest);assert before.index.keys()==after.index.keys()
    assert [n.get('id') for n in before.root.iter('ref')]==[n.get('id') for n in after.root.iter('ref')]
    assert after.amount(after.index[setting.get('id')],'end_time')==9500
    # Stronger than a property-list check: restoring this one numeric leaf must
    # make the complete XML tree identical, including cases, profiles, maps and controller code.
    q=SavedProject(dest);qamount=q.resolve(q.fields(q.index[setting.get('id')])['end_time'])
    q.fields(qamount)['value'].text=before.fields(before.resolve(before.fields(before.index[setting.get('id')])['end_time']))['value'].text
    assert E.tostring(q.root)==E.tostring(before.root)
    with zipfile.ZipFile(src) as zi,zipfile.ZipFile(dest) as zo:
        assert zi.namelist()==zo.namelist()
        assert all(zi.read(n)==zo.read(n) for n in zi.namelist() if n!='project.xml')
    original=json.loads((a.source_directory/'manifest.json').read_text());case=next(c for c in original['projects'] if c['test']=='61905067').copy()
    case.update(project=dest.name,sha256=sha(dest),bytes=dest.stat().st_size,end_time_s=9500.,CRUISE_loaded=False,CRUISE_solved=False)
    manifest={k:v for k,v in original.items() if k not in ['projects','frozen_demand_screen']}
    manifest.update(status='SHORT_DIAGNOSTIC_PENDING_USER_RUN',purpose='Obtain failed-run-equivalent data before SOC exhaustion; not a completed067 validation',projects=[case],original_full_test_end_time_s=10122.190356254578,only_project_change='active Task Settings End time:10122.190356254578 ->9500s',initial_SOC_unchanged=True,all_other_XML_bytes_verified_unchanged=True,full067_validation_complete=False,previous_failure_partial_CSV_unavailable=True)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    for name in ['ANL61905067_driver_1s.csv','ANL61905067_reference_native.csv','Unified_Candidate_Cell_OCV_25C.dat','Unified_Candidate_Cell_Resistance_25C.dat']:
        shutil.copyfile(a.source_directory/name,out/name);assert sha(a.source_directory/name)==sha(out/name)
    script=(a.source_directory/'evaluate_C3_common_limits.py').read_text()
    old="result=dict(test=a.test,status='ACTUAL_USER_EXPORT_EVALUATED',"
    new="result=dict(test=a.test,status='SHORT_DIAGNOSTIC_USER_EXPORT_EVALUATED',diagnostic_only=True,original_full_test_end_time_s=manifest['original_full_test_end_time_s'],full067_validation_complete=False,"
    assert script.count(old)==1;script=script.replace(old,new)
    (out/'evaluate_C3_067_diagnostic.py').write_text(script)
    print(json.dumps(dict(project=case,only_end_time_changed=True,full067_validation_complete=False),indent=2))
if __name__=='__main__':main()
