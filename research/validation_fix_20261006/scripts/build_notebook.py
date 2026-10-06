from pathlib import Path
import nbformat
import ast, contextlib, io, os
root=Path(__file__).resolve().parents[1]
n=nbformat.v4.new_notebook(metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}})
c=nbformat.v4
n.cells=[c.new_markdown_cell('# Bolt reference-input validation audit\n\nOffline ANL voltage/SOC checks and completed EDU map provenance. **CRUISE M was not executed.** The discharge battery model has not passed independent validation.\n\nData: native CSV channels plus TDMS Phase 1 indices; NREL Figure 12; EPA EDU completed map and original SwRI points. SOC channel identity, single-voltage EDU transfer and charge/discharge differences remain material assumptions.'),
c.new_code_cell('from pathlib import Path\nimport json, subprocess, sys, hashlib\nimport pandas as pd\nROOT=Path.cwd()\nSOURCE=ROOT.parent / "validation_sources/public_inputs/Bolt_CRUISE_M_DataKit"\nRAW=ROOT.parent / "validation_sources/raw_reference/raw_tdms"\nassert SOURCE.is_dir() and RAW.is_dir(), "Materialize the separate source archives and update SOURCE/RAW."\nrun=subprocess.run([sys.executable,str(ROOT/"scripts/audit_inputs.py"),"--source",str(SOURCE),"--raw",str(RAW)],capture_output=True,text=True,check=True)\n(ROOT/"results/audit_run.json").write_text(run.stdout)\nprint("Raw-source numerical audit completed. No simulation execution.")\nquality=json.loads((ROOT/"results/battery_data_quality.json").read_text())'),
c.new_markdown_cell('## Data quality and time alignment\n\nUse the original Phase 1 row boundaries; deduplicate channel clocks by median; hold CAN observations; exclude invalid voltage/current rows and gaps >2 s from integration. Missing coverage is reported rather than silently filled. Numeric integration and declared phase totals are distinct.'),
c.new_code_cell('pd.DataFrame([{k:r[k] for k in ["test","native_phase_rows","unique_meter_rows","invalid_voltage_or_current_rows","coverage_fraction","integrated_valid_meter_Wh","declared_phase_Wh"]} for r in quality])'),
c.new_markdown_cell('## Battery reference equation and SOC meaning\n\nThe specific Figure 12 coefficient coordinate is **percent SOC**, despite the general report equation describing fractional SOC. Fractional input z requires coefficient conversion. Displayed and internal ECU SOC are separate observed channels; neither is established as NREL\'s exact coordinate or chemical SOC. The 5–95% priority window is a research choice, not a validated domain.'),
c.new_code_cell('r=pd.read_csv(ROOT/"results/battery_voltage_by_SOC.csv")\nr[(r.SOC_lower_inclusive_percent==5)&(r.SOC_upper_percent==95)][["test","SOC_channel","rows","RMSE_V","mean_bias_predicted_minus_measured_V","p95_abs_error_V"]]'),
c.new_code_cell('pd.read_csv(ROOT/"results/display_to_internal_SOC_observed_fit.csv")'),
c.new_markdown_cell('## Completed-map provenance\n\nInside the original measurement convex hull does not mean a direct measured grid node. Regen loss uses EPA drive-loss mirror factor1.05, with no original regen observations. Reconstruction error against original fitting points is not independent validation. Runtime lookup uses bilinear loss, with Full load/power/axis constraints and no external extrapolation.'),
c.new_code_cell('print(json.dumps(json.loads((ROOT/"results/bolt_map_audit.json").read_text()),indent=2))\npd.read_csv(ROOT/"results/bolt_map_support_counts.csv")'),
c.new_markdown_cell('## Evaluator checks and comparison gates\n\nSynthetic fixtures verify dimensional integrals and refusal of invalid input or unmatched terminal battery energy. They do not establish vehicle-model accuracy. Independent battery/cycle results and actual CRUISE traces are still required. Fuel/genset bounds, transient fuel and depletion mission definitions are required for EREV fuel/range claims.'),
c.new_code_cell('run=subprocess.run([sys.executable,str(ROOT/"scripts/check_evaluator.py")],capture_output=True,text=True,check=True)\njson.loads((ROOT/"results/evaluator_checks.json").read_text())'),
c.new_markdown_cell('## Takeaways\n\nCharge reference replay is much closer than discharge replay; changing SOC channel alone does not fix discharge residuals. No full-SOC discharge acceptance domain has been established. Preserve equation/data lineage, identify discharge dynamics and coordinate/capacity on suitable data, validate on independent conditions, then compare like-for-like cycle results. Official wall-AC label values and battery-DC results need matching boundaries and procedures. EREV total range requires explicit initial inventories, stopping criteria and feasible speed tracking.')]
path=root/'Bolt_Validation_Audit.ipynb';nbformat.write(n,path)
# Jupyter TCP kernels are unavailable in this managed workspace. Execute these
# generated standard-Python cells sequentially in one shared namespace instead.
# Outputs below come from actual execution, with the execution route recorded.
namespace={};previous=Path.cwd();os.chdir(root);count=0
try:
 for cell in n.cells:
  if cell.cell_type!='code':continue
  count+=1;tree=ast.parse(cell.source);last=None
  if tree.body and isinstance(tree.body[-1],ast.Expr):last=ast.Expression(tree.body.pop().value)
  buf=io.StringIO()
  with contextlib.redirect_stdout(buf):
   exec(compile(tree,'notebook-cell-'+str(count),'exec'),namespace)
   value=eval(compile(last,'notebook-cell-'+str(count),'eval'),namespace) if last else None
  cell.execution_count=count;cell.outputs=[]
  if buf.getvalue():cell.outputs.append(c.new_output('stream',name='stdout',text=buf.getvalue()))
  if value is not None:
   data={'text/plain':repr(value)}
   if hasattr(value,'to_html'):data['text/html']=value.to_html()
   cell.outputs.append(c.new_output('execute_result',execution_count=count,data=data))
finally:os.chdir(previous)
n.metadata['execution_route']='Sequential in-process standard Python; nbclient TCP kernel unavailable in managed environment. All code cells actually executed.'
nbformat.write(n,path)
assert all(cell.get('execution_count') for cell in n.cells if cell.cell_type=='code')
print('Notebook executed:',path,'code cells',sum(c.cell_type=='code' for c in n.cells))
