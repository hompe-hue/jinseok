"""Reproducible offline audit; no CRUISE M execution or parameter refitting.
Run: python scripts/audit_inputs.py --source <DataKit> --raw <raw_tdms_dir>
"""
import argparse, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from nptdms import TdmsFile
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[1]

def ocv(s): return 322.397+1.29836*s-.0184756*s*s+.000143235*s**3
def resistance(s): return .0806969-.000281326*s+1.66726e-6*s*s
def jsonwrite(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))

def align_can(d, meter_t, field, gap_limit=2.):
    # Channel clocks are authoritative; median collapses repeated held samples.
    c=d[['CAN_clock_s',field]].dropna().groupby('CAN_clock_s')[field].median()
    x=c.index.to_numpy(); y=c.to_numpy()
    j=np.searchsorted(x,meter_t,side='left')
    lo=np.clip(j-1,0,len(x)-1); hi=np.clip(j,0,len(x)-1)
    exact=(x[hi]==meter_t)
    valid=exact | ((meter_t>=x[0]) & (meter_t<=x[-1]) & ((x[hi]-x[lo])<=gap_limit))
    # SOC and other CAN fields are held observations, not continuously measured ramps.
    held=np.where(exact,hi,lo)
    out=y[held].copy(); out[~valid]=np.nan
    return out

def segment_integral(t, y, valid, max_gap=2.):
    dt=np.diff(t); keep=valid[:-1]&valid[1:]&(dt>0)&(dt<=max_gap)
    return float(np.sum((y[:-1][keep]+y[1:][keep])*.5*dt[keep])), float(dt[keep].sum())

def battery(source, raw):
    reports=[]; residuals=[]; mappings=[]; windows=[]
    for test,name in [('61905054','anl_drive.tdms'),('61905064','anl_deplete.tdms'),('61905065','anl_charge.tdms')]:
        p=source/'data'/f'ANL_{test}_selected_native_rows.csv'; df=pd.read_csv(p)
        g=TdmsFile.read_metadata(raw/name).groups()[0]; props=g.properties
        start=int(str(props['Phase_1_Phase_Start_Fill_Index']).strip())-1
        stop=int(str(props['Phase_1_Phase_Stop_Fill_Index']).strip())
        d=df.iloc[start:stop].copy()
        meter_cols=['meter_clock_s','meter_pack_voltage_V','meter_pack_current_A_discharge_positive','meter_pack_power_kW_discharge_positive']
        meter=d[meter_cols].dropna().groupby('meter_clock_s').median().sort_index()
        t=meter.index.to_numpy(); v=meter.meter_pack_voltage_V.to_numpy()
        i=meter.meter_pack_current_A_discharge_positive.to_numpy(); power=meter.meter_pack_power_kW_discharge_positive.to_numpy()
        # Retain the physical low-voltage discharge tail (275.77–279.99 V).
        # This is a broad data-plausibility screen, not an inferred BMS limit.
        valid=(v>=200)&(v<=450)&np.isfinite(i)&(np.abs(i)<=1000)
        q,duration=segment_integral(t,i,valid); e,_=segment_integral(t,power,valid)
        temp=align_can(d,t,'battery_temperature_CAN_degC')
        pair=valid&np.isfinite(temp)
        phase_duration=float(props['Phase_1_Phase_Length_s'])
        report={'test':test,'phase_start_row_zero_based':start,'phase_stop_row_exclusive':stop,
                'native_phase_rows':len(d),'unique_meter_rows':len(t),'duplicate_meter_rows':len(d)-len(t),
                'invalid_voltage_or_current_rows':int((~valid).sum()),'integrated_valid_seconds':duration,
                'phase_declared_seconds':phase_duration,'meter_phase_span_s':float(t[-1]-t[0]),
                'coverage_fraction':duration/float(t[-1]-t[0]),
                'integrated_duration_to_declared_phase_duration_ratio':duration/phase_duration,
                'integrated_valid_Ah':q/3600,'integrated_valid_meter_Wh':e/3.6,
                'declared_phase_Ah':float(props['Phase_1_Elec_Ahr_Ahr']),
                'declared_phase_Wh':float(props['Phase_1_Elec_Whr_Whr']),
                'meter_power_minus_VI_median_kW':float(np.median((power-v*i/1000)[valid])),
                'temperature_min_degC':float(temp[pair].min()),'temperature_max_degC':float(temp[pair].max()),
                'no_silent_gap_integration':True,'analysis_voltage_filter_V':[200,450],
                'analysis_filter_is_BMS_limit':False,'SOC_channels':[]}
        aligned={}
        for field in ['displayed_SOC_percent','internal_SOC_HPCM2_percent','internal_SOC_HPCM_percent']:
            if field not in d: continue
            s=align_can(d,t,field); aligned[field]=s
            mask=valid&np.isfinite(s)&(s>=0)&(s<=100)
            report['SOC_channels'].append({'channel':field,'minimum':float(s[mask].min()),'maximum':float(s[mask].max()),'aligned_valid_rows':int(mask.sum())})
            pred=ocv(s)-i*resistance(s); err=pred-v
            for a,b in [(0,5),(5,10),(10,20),(20,40),(40,60),(60,80),(80,95),(95,100),(5,95)]:
                m=mask&(s>=a)&(s<b if b<100 else s<=b)
                if not m.any(): continue
                residuals.append({'test':test,'SOC_channel':field,'SOC_lower_inclusive_percent':a,'SOC_upper_percent':b,'rows':int(m.sum()),'RMSE_V':float(np.sqrt(np.mean(err[m]**2))),'mean_bias_predicted_minus_measured_V':float(err[m].mean()),'p95_abs_error_V':float(np.quantile(abs(err[m]),.95)),'status':'OFFLINE_ALIGNED_REFERENCE_CHECK_NOT_CRUISE_VALIDATION'})
            for k in np.flatnonzero(mask)[::1000]:
                windows.append([test,float(t[k]),field,float(s[k]),float(i[k]),float(v[k]),float(pred[k]),float(err[k]),float(temp[k]) if np.isfinite(temp[k]) else None])
        display=aligned['displayed_SOC_percent']
        report['apparent_endpoint_capacity_not_cell_capacity']=[]
        for field,s in aligned.items():
            m=valid&np.isfinite(s)&(s>=0)&(s<=100)
            ix=np.flatnonzero(m)
            if len(ix)<2:continue
            first,last=ix[0],ix[-1]
            window=np.arange(len(t)); mq=valid&(window>=first)&(window<=last)
            charge,_=segment_integral(t,i,mq)
            change=(s[first]-s[last])/100
            if abs(change)>.005:
                report['apparent_endpoint_capacity_not_cell_capacity'].append({'channel':field,'initial_SOC_percent':float(s[first]),'terminal_SOC_percent':float(s[last]),'valid_segment_net_Ah':charge/3600,'apparent_Ah_per_unit_channel_SOC':charge/3600/change,'replayed_terminal_SOC_percent_assuming_168Ah':float(s[first]-charge/3600/168*100),'note':'Channel-based endpoint estimate; excludes invalid segments; not a measured usable or chemical capacity. Initial/full SOC plateaus can distort this estimate.'})
        for field,s in aligned.items():
            if field=='displayed_SOC_percent': continue
            m=valid&np.isfinite(display)&np.isfinite(s)&(display>=5)&(display<=80)
            if m.sum()<5: continue
            # Equal weighting per displayed SOC step, not per held-row duration.
            pairs=pd.DataFrame({'display':display[m],'internal':s[m]}).groupby('display').median()
            slope,intercept=np.polyfit(pairs.index,pairs.internal,1)
            r=pairs.internal.to_numpy()-(slope*pairs.index.to_numpy()+intercept)
            mappings.append({'test':test,'internal_channel':field,'display_low':float(pairs.index.min()),'display_high':float(pairs.index.max()),'unique_display_steps':len(pairs),'slope':float(slope),'intercept_percent':float(intercept),'mapping_RMSE_percentage_points':float(np.sqrt(np.mean(r*r))),'status':'EMPIRICAL_CHANNEL_CONVERSION_IN_THIS_TEST_ONLY_NOT_CHEMICAL_SOC'})
        reports.append(report)
    pd.DataFrame(residuals).to_csv(ROOT/'results/battery_voltage_by_SOC.csv',index=False)
    pd.DataFrame(mappings).to_csv(ROOT/'results/display_to_internal_SOC_observed_fit.csv',index=False)
    pd.DataFrame(windows,columns=['test','meter_time_s','SOC_channel','SOC_percent','current_A_discharge_positive','measured_V','reference_predicted_V','residual_V','temperature_degC']).to_csv(ROOT/'results/battery_aligned_residual_sample.csv',index=False)
    jsonwrite(ROOT/'results/battery_data_quality.json',reports)
    # Tabulation remains unchanged; acceptance metadata is separate.
    s=np.arange(101,dtype=float)
    pd.DataFrame({'SOC_fraction':s/100,'SOC_percent':s,'pack_OCV_V':ocv(s),'pack_R_ohm':resistance(s),'cell_OCV_V_96S':ocv(s)/96,'cell_R_ohm_96S3P':resistance(s)*3/96,'offline_priority_window_5_to_95':((s>=5)&(s<=95)).astype(int),'discharge_validated':0,'BMS_limits_identified':0}).to_csv(ROOT/'inputs/battery_reference_with_validity.csv',index=False)
    return reports, residuals, mappings

def maps(source):
    d=pd.read_csv(source/'data/bolt_power_loss_long.csv')
    hull=pd.read_csv(source/'data/bolt_test_hull_mask.csv')
    d=d.merge(hull,on=['speed_rpm','torque_Nm'],validate='one_to_one')
    regen=d.torque_Nm<0; inside=d.inside_measured_point_convex_hull.astype(bool)
    d['support_class']=np.where(regen,'REGEN_ESTIMATE_DRIVE_LOSS_MIRROR_1p05',np.where(inside,'COMPLETED_MAP_INSIDE_MEASURED_HULL','COMPLETED_MAP_OUTSIDE_MEASURED_HULL'))
    d['runtime_allowed']=d.within_operating_envelope.astype(bool).astype(int)
    d['direct_measurement']=0
    d['interpretation']='Hull inclusion is geometric support, not a measured grid node; loss lookup is bilinear; external extrapolation is forbidden.'
    d.to_csv(ROOT/'inputs/bolt_map_provenance_and_limits.csv',index=False)
    counts=d.groupby(['support_class','runtime_allowed']).size().reset_index(name='grid_nodes')
    counts.to_csv(ROOT/'results/bolt_map_support_counts.csv',index=False)
    r=pd.read_csv(source/'data/bolt_map_vs_measured_residuals.csv')
    err=r.residual_kW.dropna().to_numpy()
    out={'grid_nodes':len(d),'runtime_allowed_grid_nodes':int(d.runtime_allowed.sum()),
         'measured_source_points':len(r),'reconstruction_RMSE_kW':float(np.sqrt(np.mean(err*err))),
         'reconstruction_is_independent_validation':False,'regen_measured_source_points':0,
         'source_regen_loss_mirror_factor':1.05,'nominal_voltage_V':400,
         'voltage_temperature_dependence_identified':False,'CRUISE_M_executed':False}
    jsonwrite(ROOT/'results/bolt_map_audit.json',out)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True);ap.add_argument('--raw',type=Path,required=True)
    args=ap.parse_args(); ROOT.joinpath('results').mkdir(exist_ok=True)
    b,r,m=battery(args.source,args.raw); e=maps(args.source)
    print(json.dumps({'battery_quality':b,'SOC_mapping':m,'EDU':e},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
