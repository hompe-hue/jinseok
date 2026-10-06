from pathlib import Path
import json,csv,hashlib,math,zipfile
import numpy as np,pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
from docx import Document
from docx.shared import Inches,Pt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];IN=ROOT/'inputs';OUT=ROOT/'results'
def savecsv(name,rows):
 with (IN/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sources=[
 ('S01','GM','2016 Volt Voltec drive unit release','https://media.gm.com/content/dam/Media/microsites/product/Volt_2016/doc/VOLT_DRIVEUNIT.pdf','GM_Volt2016_DriveUnit.pdf','1.5L DI, compression 12.5:1, cooled EGR, regular fuel; manufacturer overview'),
 ('S02','INL / DOE','2016 Volt baseline vehicle factsheet','https://avt.inl.gov/sites/default/files/pdf/phev/fact2016chevroletvolt.pdf','','Indexed primary PDF contents read; direct download 403. L3A 75kW@5600,140Nm@4300; generating45kW at vehicle level; nominal360V'),
 ('S03','GM / SAE','Conlon et al. 2015-01-1152','https://doi.org/10.4271/2015-01-1152','','Original engine BSFC map referenced by S06; full SAE numeric array not obtained'),
 ('S04','GM / SAE','Jurkovic et al. 2015-01-1208','https://doi.org/10.4271/2015-01-1208','','Original Gen2 PMAC machine paper referenced by S06; raw Q4 array and test V/T not confirmed'),
 ('S05','GM / SAE','Anwar et al. 2015-01-1201','https://doi.org/10.4271/2015-01-1201','','Separate TPIM performance; raw numerical inverter map not obtained'),
 ('S06','Castellano and Cammalleri','Applied Sciences 2021,11,7779','https://doi.org/10.3390/app11177779','MDPI_PowerLosses_2021_vor.pdf','OPEN CC BY; Figure4 reconstructed engine efficiency; Figure5 MGA(MG I),MGB(MG O) maps reused for both directions; vector paths extracted from p8 of downloaded earlier version'),
 ('S07','ANL','EVS30 2017 Vehicle level control analysis','https://www.citelec.org/EVS30/download.php?f=papers/EVS30-2460262.pdf','ANL_Voltec_Control_EVS30_2017.pdf','Production power-split modes/control; not a standalone series generator control map'),
 ('S08','Bhasme et al. MTU','ICAVP2019 supervisory controller','https://sites.ualberta.ca/~mahdi/Docs/ICAVP19_MichiganTech_ChevyVoltModeling.pdf','MTU_Volt_Gen2_Controller_2019.pdf','Table1: engine140Nm75kW,MGA118Nm48kW,MGB280Nm87kW; machine maps and TPIM treated separately. Table curb mass160kg apparent typo: not used'),
 ('S09','Hemmati et al.','Powertrain dynamics 2021 author preprint','https://doi.org/10.21203/rs.3.rs-536651/v1','Powertrain_Dynamics_2021.pdf','CC BY preprint; Figures8/15 BSFC;16 multi-quadrant operation; startup/catalyst/transient fuel penalties described. No raw arrays used'),
 ('S10','GM service manual','5ET50 general description','https://estimate.mymitchell.com/GMC/document/4/0/9/1/9/100304692_4091910_10188404.html','GM_ServiceManual_5ET50.html','Two machines, planetary sets, integrated TPIM; extraction is a newly assumed coupling, not production Volt topology'),
 ('S11','GM / SAE','Jocsak et al. 2015-01-1272','https://doi.org/10.4271/2015-01-1272','','Engine combustion design; raw Full load/fuel dataset not obtained')]
registry=[]
for sid,org,title,url,fn,scope in sources:
 f=ROOT/'sources'/fn
 registry.append(dict(source_id=sid,organization=org,title=title,url=url,local_file=fn,sha256=hashlib.sha256(f.read_bytes()).hexdigest() if fn and f.exists() else '',scope=scope))
savecsv('source_register.csv',registry)
def param(component,field,value,unit,source,status,note):return dict(component=component,field=field,value=value,unit=unit,source=source,status=status,note=note)
params=[
 param('Engine','RPO','L3A','-','S02','SOURCED','Gen2 2016-2019 donor; do not mix Gen1 1.4L'),
 param('Engine','Displacement',1.5,'L','S01,S02','SOURCED','Inline4,4-stroke,naturally aspirated,gasoline DI'),
 param('Engine','Cylinder_count',4,'-','S02','SOURCED',''),param('Engine','Compression_ratio',12.5,'-','S01','SOURCED',''),
 param('Engine','Peak_power',75,'kW','S02','SOURCED','At5600rpm; not net electric power'),param('Engine','Peak_power_speed',5600,'rpm','S02','SOURCED',''),
 param('Engine','Peak_torque',140,'Nm','S02','SOURCED','At4300rpm'),param('Engine','Peak_torque_speed',4300,'rpm','S02','SOURCED',''),
 param('Engine','Fuel','regular unleaded','-','S01,S02','SOURCED','Fuel LHV/density in map source not confirmed'),
 param('MGA','Machine_type','PMAC synchronous ferrite','-','S04,S08','SOURCED','Select PM synchronous option, not screenshot asynchronous default'),
 param('MGA','Peak_power',48,'kW','S02,S08','SOURCED','Peak/nameplate; not standalone net continuous generating power'),
 param('MGA','Peak_torque',118,'Nm','S08','SOURCED','Torque ceiling alone cannot fill speed envelope'),
 param('MGB','Machine_type','PMAC synchronous NdFeB','-','S04,S08','SOURCED','Alternative generator only; Bolt traction unit retained'),
 param('MGB','Peak_power',87,'kW','S02,S08','SOURCED','Alternative topology with new generator role; not 87kW net rating'),param('MGB','Peak_torque',280,'Nm','S08','SOURCED',''),
 param('Volt vehicle','Reported_generating_power',45,'kW','S02','SOURCED','Vehicle level entry; not independent MGA continuous rating'),
 param('Volt vehicle','Nominal_DC_voltage',360,'V','S02','SOURCED','Nominal vehicle pack value, not source map test voltage'),
 param('Map preview','Voltage_axis',360,'V','Assumption','ASSUMED','One placeholder axis; no voltage dependence or Bolt terminal range validated'),
 param('Map preview','Temperature_axis',25,'degC','Assumption','ASSUMED','One placeholder axis; NOT measured map temperature'),
 param('Fuel conversion','LHV',43,'MJ/kg','Assumption','ASSUMED','Changing LHV changes inferred fuel; BSFC=3600/(eta*LHV)'),
 param('Series coupling','Ratio_gen_over_engine',2,'-','Assumption','ASSUMED','26kW warm operating-point candidate; sweep alternatives included'),
 param('Series coupling','Mechanical_efficiency',.98,'fraction','Assumption','ASSUMED',''),param('TPIM','Efficiency',.98,'fraction','Assumption','ASSUMED','Separate from machine eta; source machine/TPIM boundary needs OEM confirmation'),
 param('DC/DC','Efficiency',.98,'fraction','Assumption','ASSUMED','Additional conversion if implemented; bypass scenario=1.0; common-bus voltage feasibility still required'),
 param('Genset auxiliary','Power',.5,'kW','Assumption','ASSUMED','Pump/fan/controller illustrative load, not Volt measurement'),
 param('Engine','Inertia','','kg m2','Missing','REQUIRED_FOR_DYNAMICS','Do not reuse screenshot .134 as OEM value'),param('Generator','Inertia','','kg m2','Missing','REQUIRED_FOR_DYNAMICS','Do not reuse screenshot .05 as OEM value'),
 param('Generator','Continuous_thermal_rating','','kW','Missing','REQUIRED_FOR_CONTINUOUS_CLAIMS','Need coolant flow/temperature, winding limits, duration'),
 param('Vehicle','Added_genset_mass','','kg','Missing','REQUIRED_FOR_VEHICLE_COMPARISON','Engine+MG+mount+fuel+exhaust+cooling+TPIM/DC/DC; entire5ET50 mass cannot represent isolated generator'),
 param('Engine','Idle_start_fuel_map','','g/s','Missing','REQUIRED_FOR_ABSOLUTE_FUEL','No zero-power fuel from BSFC; startup thermal/catalyst penalties and cranking separate'),
 param('Generator','Safe_max_speed','','rpm','Missing','REQUIRED_FOR_HARDWARE_CLAIMS','Figure ends10000; not demonstrated mechanical limit')]
savecsv('component_parameters.csv',params)
fields=[
 ('Engine','Full load','Speed_rpm,Torque_Nm','rpm,Nm','L3A_FullLoad_CRUISE_PREVIEW.csv','Positive shaft torque; graph boundary clipped to75kW/140Nm with separate source curve retained'),
 ('Engine','Fuel consumption','Speed_rpm,Torque_Nm,FuelConsumption_g_s','rpm,Nm,g/s','L3A_CRUISE_PREVIEW_assumed_axes.csv','528 warm positive-load points; kg/h=g/s*3.6; LHV43MJ/kg assumed; no idle/coldstart'),
 ('Generator MGA','Full load','Voltage_V,Speed_rpm,Torque_Nm','V,rpm,Nm','MGA_FullLoad_CRUISE_PREVIEW.csv','360V placeholder; Q1 positive and Q4 negative load. Plot boundary is motoring source mirrored to Q4'),
 ('Generator MGA','Efficiency','Temperature_degC,Voltage_V,Speed_rpm,Torque_Nm,Efficiency_pct','degC,V,rpm,Nm,%','MGA_CRUISE_PREVIEW_assumed_axes.csv','657 each direction,1314 total;25degC and360V are assumed axes; exported percentage, not fraction'),
 ('Generator MGB alt','Full load','Voltage_V,Speed_rpm,Torque_Nm','V,rpm,Nm','MGB_FullLoad_CRUISE_PREVIEW.csv','Optional generator variant; does not replace Bolt traction unit'),
 ('Generator MGB alt','Efficiency','Temperature_degC,Voltage_V,Speed_rpm,Torque_Nm,Efficiency_pct','degC,V,rpm,Nm,%','MGB_CRUISE_PREVIEW_assumed_axes.csv','690 each direction,1380 total; Q4 mirror, not independently measured'),
 ('Engine/Generator','Transient/start domain','Speed below data core,zero torque,inertia','various','No validated table','Do not extrapolate silently; use explicit ideal warm-start abstraction for SOC-only scenarios or obtain dynamics before fuel claims')]
savecsv('CRUISE_field_mapping.csv',[dict(component=a,field=b,columns=c,units=d,file=e,application=f) for a,b,c,d,e,f in fields])
# Meaningful sanity checks against exported physical limits and sign/power conversions.
checks=[]
for name in ['L3A','MGA','MGB']:
 x=pd.read_csv(IN/(name+'_CRUISE_PREVIEW_assumed_axes.csv'));fl=pd.read_csv(IN/(name+'_full_load_source_and_cap.csv'))
 bound=np.interp(x.Speed_rpm,fl.speed_rpm,fl.scenario_capped_torque_Nm)
 assert np.all(abs(x.Torque_Nm)<=.97*bound+1e-5)
 if name!='L3A':
  assert x.Efficiency_pct.between(0,100,inclusive='neither').all();q1=x[x.Torque_Nm>0].reset_index(drop=True);q4=x[x.Torque_Nm<0].reset_index(drop=True);assert np.allclose(q1.Efficiency_pct,q4.Efficiency_pct)
  assert np.allclose(q1.Torque_Nm,-q4.Torque_Nm)
 else:
  a=pd.read_csv(IN/'L3A_warm_core_physical.csv');pw=a.speed_rpm*a.torque_Nm*2*np.pi/60000
  assert np.allclose(a.fuel_g_s,pw*a.BSFC_g_kWh/3600)
 checks.append(dict(check=name+' exported limits/sign/units',passed=True,interpretation='Internal reconstruction consistency; not independent validation'))
(OUT/'quality_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
# Exact contour and output grid overlay, helps inspect reconstruction and axes.
fig,axs=plt.subplots(1,3,figsize=(15,4.3))
for ax,name in zip(axs,['L3A','MGA','MGB']):
 c=pd.read_csv(IN/(name+'_contour_vertices.csv'));g=pd.read_csv(IN/(name+'_warm_core_physical.csv'));fl=pd.read_csv(IN/(name+'_full_load_source_and_cap.csv'))
 ax.scatter(c.speed_rpm,c.torque_Nm,c=c.efficiency_pct,cmap='turbo',s=.25,vmin=c.efficiency_pct.min(),vmax=c.efficiency_pct.max())
 t=g.torque_Nm if name=='L3A' else g.torque_abs_Nm
 ax.scatter(g.speed_rpm,t,s=3,c='black',alpha=.25);ax.plot(fl.speed_rpm,fl.source_plot_torque_Nm,'k-',lw=1);ax.plot(fl.speed_rpm,fl.scenario_capped_torque_Nm,'k--',lw=1)
 ax.set(xlabel='Mechanical speed [rpm]',ylabel='Torque magnitude [Nm]',title=name+' | digitized warm core')
fig.suptitle('Volt Gen2 published contours + exported grid (dots); solid=source / dashed=scenario cap')
fig.tight_layout();fig.savefig(OUT/'map_reconstruction_audit.png',dpi=170);plt.close(fig)
audit=json.loads((OUT/'audit.json').read_text());peaks=pd.read_csv(IN/'genset_peak_sweep.csv');target=pd.read_csv(IN/'genset_target_candidates.csv');best=target[(target.generator=='MGA')&(target.target_net_kW==26)&target.status.str.startswith('candidate')].sort_values('net_fuel_g_kWh').iloc[0]
readme=f'''# Bolt EV + Volt Gen2 구성품 기반 가상 직렬형 EREV 입력자료\n\n2026-10-06 / 연구용 도표 재구성 v1 / CRUISE M 실행하지 않음\n\n## 연구 방향과 선정 사유\nBolt EV의 차체·배터리·구동 EDU를 기준으로 BEV 검증을 진행하고, 이후 Volt 2세대의 L3A 엔진과 MGA를 추가한 가상 직렬형 EREV의 SOC 제어를 비교한다. 같은 Chevrolet/GM의 승용 전동화 차량이라는 구성품 선정 일관성, 제조사·정부 제원과 공개 효율도 확보 가능성이 장점이다. Bolt와 Volt는 같은 플랫폼이나 동일 인증 차종이 아니며, 상호 장착·전압·냉각 호환성이 입증된 것은 아니다.\n\n실제 Volt는 2개 유성기어와 클러치를 가진 동력분기 구조다. 이 연구는 해당 기어장치를 복제하지 않고 엔진과 발전기의 독립 고정비 연결을 설계 가정으로 추가한다. 따라서 실차 Volt의 42mpg·53mile·420mile 등은 가상 모델의 검증 목표로 직접 사용하지 않는다. Bolt BEV의 실험/공식 데이터 검증과 가상 EREV의 비교 실험을 구분한다.\n\n## 확보한 실제 제원\n- L3A: 1.5L 직렬4기통, 자연흡기 DI 가솔린, 압축비12.5:1,75kW@5600rpm,140Nm@4300rpm,일반 무연가솔린.\n- MGA: PMAC 동기기, 페라이트 자석,118Nm/48kW 피크 제원. 발전용 기본 후보.\n- MGB: PMAC 동기기, NdFeB,280Nm/87kW 피크. 별도 발전기 대안으로만 사용하며 Bolt 구동기는 유지.\n- INL 차량 제원에는 발전45kW, 배터리 공칭360V가 기재되어 있다. 차량 전체의 발전 값이며, 독립 MGA 연속 정격이나 효율맵 시험전압으로 해석하지 않는다.\n- Volt18.4kWh 배터리, 기어비, 전체 주행거리는 Bolt 가상 모델 입력으로 이전하지 않는다.\n\n## 실제로 확보한 맵과 수치표\nCastellano/Cammalleri(2021)의 Figure4,5 및 PDF p8의 벡터 경로를 추출했다. Figure4는 Conlon2015 엔진맵을 재구성한 효율도이며, Figure5는 Jurkovic2015 전기기계 맵을 재구성했다. 원 GM 실측 숫자 행렬은 확보하지 못했다. 도표 변환 결과는 실측 원본이 아니라 2차 도표에서 파생된 연구 입력 후보이다.\n\n엔진 연료표 {audit['qa']['L3A']['grid_points']}점, MGA 효율 Q1/Q4 각각657점(총1314), MGB 각각690점(총1380)을 제공한다. Full load 원 도표 곡선과 피크제원으로 제한한 후보곡선을 별도로 제공한다. 전기기계 모터영역의 최대토크와 효율을 |T|에 따라 Q4로 대칭 사용한 가정이므로 발전 영역 독립 실측은 아니다. 엔진 정지/공회전과 발전기 저속 시동/무부하 전력손실 맵은 없다.\n\nPDF 축을 기계 회전수 rpm와 축 토크Nm로 보정하고, 명시된 등고선 레벨을 사용했다. 축 정규화 후 등고선 내부 삼각형 선형 보간만 사용하며 외삽은 하지 않았다. 최고 등고선 내부에는 더 높은 효율을 만들지 않고 최고 사용레벨(엔진36%,MGA94%,MGB96%)을 유지한다. 효율점을 원곡선 및 제원 제한 Full load의97% 이내로 필터했다. 이3%는 모델링 여유이지 열적 연속 정격 여유가 아니다.\n\nCSV의 PREVIEW 표는 CRUISE M 열에 맞춘 후보다. 360V는 차량 공칭전압에서 가져온 **모델 축 가정**,25°C는 **임의 단일 온도축**이다. 실제 도표 시험전압/온도는 미확인이다. 이 값으로 전압·온도 의존성이 검증된 것으로 주장할 수 없다. 배터리 실제 단자전압을 연결한 경우 CRUISE M의 단일축 보간·외삽 처리를 확인하고, 지원 범위 밖 횟수를 기록해야 한다.\n\n연료 변환: P[kW]=2πnT/60000; BSFC[g/kWh]=3600/(ηengine·43); fuel[g/s]=P/(ηengine·43); kg/h=g/s·3.6. LHV43MJ/kg는 원맵 연료 성상으로 검증한 값이 아닌 가정이다. η는 계산 시0~1, 발전기 효율 입력에는0~100% 사용한다.\n\n## 권장 초기 variant와 출력 계산\n기본안은 Bolt EV + L3A + MGA로 시작한다. 기존26kW 순발전 제어를 검토할 수 있는 예비 운전점은 엔진{best.engine_rpm:.0f}rpm/{best.engine_torque_Nm:.0f}Nm, 발전기{best.generator_rpm:.0f}rpm/{best.generator_torque_Nm:.2f}Nm, 기어비ng/ne={best.ratio_generator_over_engine:.2f}, 엔진축출력{best.engine_shaft_kW:.3f}kW, 순발전{best.net_bus_kW:.3f}kW이다. 이는 가정하의 정속 후보이며 효율 최적성·연속운전·시동성을 검증한 값은 아니다. 기존 제어규칙은 이 자료로 자동 교체하지 않는다.\n\nPnet=Pe·ηcoupling·ηmachine·ηinverter·ηDC/DC−Paux. 예비 계산은 각각0.98,도표효율,0.98,0.98,0.5kW를 사용했다. 전기기계 도표는 기계 자체 효율로 임시 해석했으나 OEM 시험경계는 미확인이다. 인버터 포함 맵이라면 추가 인버터 손실은 중복이므로 경계를 확인해 수정해야 한다. 공통 DC 버스로 DC/DC를 생략한다면 ηDC/DC=1로 별도 계산하되 단자전압과 기기 한계가 먼저 충족되어야 한다.\n\n8개 고정비(0.45~2.0), 엔진1200~5800rpm(50rpm 간격),25~140Nm(1Nm 간격)의 제한적 warm core 탐색에서 최대 후보는 MGA {peaks[peaks.generator=='MGA'].net_bus_kW.max():.2f}kW, MGB {peaks[peaks.generator=='MGB'].net_bus_kW.max():.2f}kW였다. 65kW 운전점은 이 탐색에서 발견되지 않았다. 이는 해당 부품이 어떠한 조건에서도65kW를 낼 수 없다는 입증은 아니다. 48/87kW 명판, 차량발전45kW를 곧바로 순발전65kW로 스케일링하지 않는다.\n\n## CRUISE M 구성 순서\n1. 검증 중인 Bolt EV 복사본에 새 variant를 만든다. 배터리60kWh급 기준/EDU151? 숫자는 현재 Bolt 승인 자료를 그대로 참조하고 최신60/66kWh 연식을 섞지 않는다. 원 BEV 구성은 변경하지 않는다.\n2. 엔진→신규 고정비 커플링→MGA(또는 별도 MGB variant)→TPIM→DC 버스(필요 시DC/DC) 경로를 만든다. 엔진과 차축의 기계적 직접 경로는 두지 않는다.\n3. 엔진 양의 토크, 발전 Q4는 n>0,T<0으로 입력한다. 커플링 발전 토크는 Tg=−ηcoupling·Te/r. 엔진/발전기 관성과 시동기 선택은 자료 확보 후 설정한다.\n4. 엔진 Full load/Fuel, 발전기 Voltage-Speed-Torque Full load와 Temperature-Voltage-Speed-Torque-Efficiency 표를 field_mapping 기준으로 가져온다. 누락/불규칙 격자 수용 여부를 확인한다. 빈 칸을0으로 채우거나 직사각형 외삽으로 채우지 않는다.\n5. PM 동기기 선택, 효율 %/전력손실 정의, 별도TPIM 포함 범위, 회전수/토크 부호를 저부하 정속점에서 확인한다. 버전에 따라 UI명이 다를 수 있어 실제프로젝트에서 직접 확인해야 한다.\n6. 정속 후보를 먼저 검산하고SOC 제어를 연결한다. 스타터와 시동 연료가 미완성이면 warm ideal-start로 제한한 SOC 민감도 결과에 해당 추상화를 명시한다. 절대연료/총주행거리 결론은 보류한다.\n7. 실제 배터리 SOC 유효범위·정의와 기존 Bolt 회생추정 감사를 유지한다. 충전전력=발전전력−구동기/차량부하이며,발전정격이 항상 배터리충전으로 들어간다고 가정하지 않는다. 고SOC/고온/전압·충전전류 제한에서발전을 줄이거나 정지한다.\n\n## 추가로 필요한 항목과 비교 조건\n원 GM L3A Full load/BSFC 또는연료g/s 배열, 각맵 연료LHV/온도/보조기기 범위, MGA/MGB Q4 실측배열과DC전압/온도,TPIM효율배열,시동·공회전·냉시동/촉매가열 연료,열연속정격,관성,추가질량/냉각/기어패키징을 확보해야 실제품 수준의 연료·연속발전 주장을 할 수 있다. 정확한 추가 요청 대상 논문은 source_register에 기록했다.\n\nBEV와EREV 비교 시주행사이클·온도·HVAC·초기SOC 정의와사용가능에너지·차량적재·roadload를통일하고,EREV추가질량을반영한다. 연료만비교할경우종단저장에너지차이를정규화하거나동일하게맞춘다. 기존검증평가도구의0.1kWh 에너지차허용치는연구용기준으로사용가능하나인증기준이아니다. 공식전비의wall energy와시뮬레이션battery DC energy도구분한다.\n\n## 검증 수준과 파일\n내부검산은축보정,토크한계,출력환산,연료변환,Q1/Q4대칭및퍼센트단위이다. 등고선원점 재현오차는보간코드자기일관성을보일뿐실측검증이아니다. CRUISE M 프로젝트실행·시동시험·전압/열호환성·실차연비 검증은 수행하지 않았다.\n\ninputs: 소스등록·실제/가정파라미터·도표곡선·격자·탈락점·입력후보·정속탐색. results: audit/quality_checks와그림. scripts: 재현코드. 원문PDF/그림과출처별해시는별도원자료ZIP에보존한다.\n'''
# Remove ambiguous casual placeholder from retained baseline instruction.
readme=readme.replace('배터리60kWh급 기준/EDU151? 숫자는 현재 Bolt 승인 자료를 그대로 참조하고 최신60/66kWh 연식을 섞지 않는다.','배터리와 EDU 값은 현재 Bolt 승인 자료를 그대로 참조하고 60/66kWh 연식을 섞지 않는다.')
(ROOT/'README_가상EREV.md').write_text(readme,encoding='utf-8')
# Spreadsheet includes exact imports + status, not only project prose.
wb=Workbook();ws=wb.active;ws.title='READ_FIRST'
for r in [['분류','내용'],['모델','Bolt EV + Volt Gen2 L3A/MGA 가상 직렬형 EREV'],['입력 성격','공개 도표 재구성 + 명시적 가정; OEM 숫자원맵 아님'],['발전 Q4','양의회전수/음의토크;효율 대칭추정'],['조건축','360V/25degC는 가정;시험조건 미확인'],['연료','LHV43MJ/kg 가정; warm positive-load만'],['발전 정격','48/87kW 피크와 차량45kW를 독립 순발전 연속 정격으로 사용하지 않음'],['시뮬레이션','CRUISE M 실행/차량 검증 미수행'],['누락영역','시동/무부하/열연속운전, 단일축외전압/온도'],['기본운전점','MGA 26kW 후보; ng/ne2; engine2950rpm98Nm,gen5900rpm -48.02Nm'],['65kW','현재 도표+손실 가정의 제한 탐색에서 미확보']]:ws.append(r)
for fn,title in [('component_parameters.csv','Parameters'),('source_register.csv','Sources'),('CRUISE_field_mapping.csv','CRUISE_Fields'),('genset_peak_sweep.csv','Peak_Sweep'),('genset_target_candidates.csv','Targets'),('L3A_CRUISE_PREVIEW_assumed_axes.csv','ENG_Fuel_g_s'),('L3A_FullLoad_CRUISE_PREVIEW.csv','ENG_FullLoad'),('MGA_CRUISE_PREVIEW_assumed_axes.csv','MGA_Eff_Pct'),('MGA_FullLoad_CRUISE_PREVIEW.csv','MGA_FullLoad'),('MGB_CRUISE_PREVIEW_assumed_axes.csv','MGB_Eff_Pct'),('MGB_FullLoad_CRUISE_PREVIEW.csv','MGB_FullLoad'),('L3A_warm_core_physical.csv','ENG_Physical'),('contour_legend.csv','Contour_Legend')]:
 ws=wb.create_sheet(title)
 with (IN/fn).open(newline='',encoding='utf-8') as f:
  for row in csv.reader(f):
   values=[]
   for v in row:
    try:values.append(float(v) if v else None)
    except ValueError:values.append(v)
   ws.append(values)
for ws in wb:
 ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
 for c in ws[1]:c.font=Font(color='FFFFFF',bold=True);c.fill=PatternFill('solid',fgColor='183B56')
 for col in ws.columns:
  idx=col[0].column;long=max(len(str(c.value or '')) for c in list(col)[:70]);ws.column_dimensions[get_column_letter(idx)].width=min(max(long+2,16),65)
 for row in ws:
  for c in row:c.alignment=Alignment(vertical='top',wrap_text=ws.title in ['READ_FIRST','Parameters','Sources','CRUISE_Fields'])
wb.save(ROOT/'Bolt_Volt_EREV_Input_Data_20261006.xlsx')
doc=Document();doc.styles['Normal'].font.size=Pt(10)
for line in readme.splitlines():
 if line.startswith('# '):doc.add_heading(line[2:],0)
 elif line.startswith('## '):doc.add_heading(line[3:],1)
 elif line.strip():doc.add_paragraph(line.replace('**',''))
doc.add_picture(str(OUT/'map_reconstruction_audit.png'),width=Inches(6.3))
doc.add_heading('출처 목록',1)
for r in registry:doc.add_paragraph(r['source_id']+' | '+r['title']+'\n'+r['url']+'\n'+r['scope'])
doc.save(ROOT/'Bolt_Volt_EREV_Data_Guide_20261006.docx')
# Checkpoint + file inventory before archive.
(ROOT/'checkpoints/VGEN_02.json').write_text(json.dumps(dict(stage='VGEN_02',status='RECONSTRUCTED_INPUT_CANDIDATES_AND_DATA_COLLECTION_COMPLETE',CRUISE_M_executed=False,raw_OEM_numeric_maps_obtained=False,generator_Q4_measured=False,existing_Bolt_maps_modified=False,existing_controller_modified=False,source_pdf='S06 p8 vector contours',candidate_net26=best.to_dict()),ensure_ascii=False,indent=2))
manifest=[]
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and '.git' not in f.parts and f.suffix!='.zip' and f.name!='file_manifest_sha256.csv':manifest.append(dict(path=str(f.relative_to(ROOT)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
with (ROOT/'file_manifest_sha256.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(manifest)
D=ROOT.parent/'deliverables';D.mkdir(exist_ok=True)
with zipfile.ZipFile(D/'Bolt_Volt_EREV_Data_Kit_20261006.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(ROOT.rglob('*')):
  if f.is_file() and 'sources' not in f.relative_to(ROOT).parts and '.git' not in f.parts:z.write(f,arcname='Bolt_Volt_EREV/'+str(f.relative_to(ROOT)))
with zipfile.ZipFile(D/'Volt_Gen2_Reference_Sources_20261006.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((ROOT/'sources').glob('*')):
  if f.suffix in ['.pdf','.png','.json'] or f.name=='GM_ServiceManual_5ET50.html':z.write(f,arcname=f.name)
 z.write(IN/'source_register.csv',arcname='source_register.csv')
print('DELIVERABLES_COMPLETE',len(manifest),'manifest entries;',len(checks),'internal checks passed')
