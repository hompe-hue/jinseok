"""Evaluate five actual confirmation windows without adopting a model automatically."""
import argparse,json,subprocess,sys
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--exports-root',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.package/'manifest.json').read_text());results=[]
    for case in manifest['projects']:
        folder=a.exports_root/case['test'];assert folder.is_dir(),folder
        subprocess.run([sys.executable,str(a.package/'evaluate_final_candidate.py'),'--package',str(a.package),'--test',case['test'],'--exports',str(folder)],check=True)
        result=json.loads((folder/f'C3_limits_{case["test"]}_result.json').read_text())
        # Full intended window is required by the evaluator, not a shortened passing segment.
        results.append(result)
    aggregate=dict(status='ACTUAL_FIVE_WINDOW_CONFIRMATION_EVALUATED',all_declared_7_gates_pass=all(r['all_research_gates_pass'] for r in results),parameter_sha256=manifest['parameter_sha256'],all_five_core_maps_identical=manifest['all_five_core_maps_identical'],cases=results,final_model_adopted=False,scope='Warm same-vehicle effective energy/voltage/velocity reproduction, not OEM BMS/lowSOC maximum-output identification',note='Review saved-project provenance, SOC map domain and late voltage residuals before scope-limited final adoption. No automatic blanket validation.')
    (a.exports_root/'BEV_final_batch_results.json').write_text(json.dumps(aggregate,indent=2)+'\n')
if __name__=='__main__':main()
