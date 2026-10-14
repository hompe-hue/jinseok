"""Package only completed, hash-verified C1 files; publish by atomic rename."""
import argparse,hashlib,io,json,os,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/final_candidate_C1_20261014'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--destination',required=True,type=Path);args=parser.parse_args()
    destination=args.destination;destination.parent.mkdir(parents=True,exist_ok=True)
    contract=json.loads((OUT/'candidate_contract.json').read_text())
    files={}
    for folder in ['projects','inputs','references']:
        for path in sorted((OUT/folder).glob('*')):
            if path.is_file():files[f'{folder}/{path.name}']=path.read_bytes()
    for name in ['parameters.json','candidate_contract.json','RUNS.csv','DECISION_KO.md','START_HERE_KO.md']:
        files[name]=(OUT/name).read_bytes()
    files['scripts/verify_C1_exports.py']=(ROOT/'scripts/verify_C1_exports.py').read_bytes()
    for case in contract['cases']:
        data=files['projects/'+case['project']]
        assert len(data)>100000 and sha(data)==case['project_sha256'],'Empty/incomplete/wrong project'
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            assert z.testzip() is None and len(z.read('project.xml'))>100000
    assert sha(files['parameters.json'])==contract['parameter_json_sha256']
    for name,h in contract['map_sha256'].items():assert sha(files['inputs/'+name])==h
    for name,h in contract['reference_sha256'].items():assert sha(files['references/'+name])==h
    manifest={name:{'bytes':len(data),'sha256':sha(data)} for name,data in files.items()}
    files['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    temporary=destination.with_suffix(destination.suffix+'.part')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    with temporary.open('rb') as f:os.fsync(f.fileno())
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        for name,data in files.items():assert z.read(name)==data
    os.replace(temporary,destination)
    fd=os.open(destination.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    print(json.dumps({'package':str(destination),'bytes':destination.stat().st_size,'sha256':sha(destination.read_bytes()),'project_bytes':[len(files['projects/'+c['project']]) for c in contract['cases']]}))

if __name__=='__main__':main()
