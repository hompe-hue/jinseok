from pathlib import Path
import csv,json,statistics
root=Path(__file__).resolve().parents[1]
p=root/'empirical_alignment_20261013/ANL_61905054_phase1'
r=[{k:float(v) for k,v in z.items()} for z in csv.DictReader((p/'ANL_61905054_Phase1_reference_native.csv').open())]
# Read exactly the tables imported by the current GUI model; linear interpolation.
def table(name):
    return [tuple(map(float,s.split())) for s in (root/'inputs/battery'/name).read_text().splitlines()[2:]]
u=table('Bolt_Cell_OCV_25C.dat');res=table('Bolt_Cell_Resistance_25C.dat')
def lerp(tab,x):
    for a,b in zip(tab,tab[1:]):
        if a[0]<=x<=b[0]:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
    raise ValueError(x)
i=r[0]['meter_pack_current_A_discharge_positive'];target=r[0]['meter_pack_voltage_V']
def voltage(s):return 96*lerp(u,s)-32*lerp(res,s/100)*i
lo,hi=0,100
for _ in range(80):
    mid=(lo+hi)/2
    if voltage(mid)<target:lo=mid
    else:hi=mid
soc=(lo+hi)/2
startup=[x for x in r if x['phase_time_s']<=20]
assert max(abs(x['measured_speed_kmh']) for x in startup)<.001
# Effective idle scaling includes converter losses AND other HV standby loads;
# cannot be labeled measured converter efficiency.
k=statistics.median((x['meter_pack_voltage_V']*x['meter_pack_current_A_discharge_positive'])/x['LV_DCDC_output_W'] for x in startup)
integ=sum((b['phase_time_s']-a['phase_time_s'])*(a['LV_DCDC_output_W']+b['LV_DCDC_output_W'])/2 for a,b in zip(r,r[1:]))
avg=integ/r[-1]['phase_time_s']
report={'status':'Initialization and auxiliary approximation candidate, not completed matched validation','initial_SOC_percent':soc,'initial_voltage_reconstructed_V':voltage(soc),'reference_initial_voltage_V':target,'reference_initial_current_A':i,'SOC_basis':'Invert current imported OCV/R tables against first low-load measured terminal voltage; initialization calibration only, not proof of physical or CAN SOC','startup_identification_window_s':[0,20],'effective_standby_HV_to_LV_ratio':k,'full_phase_mean_LV_output_W':avg,'estimated_mean_HV_aux_W':k*avg,'aux_basis':'Measured mean LV output scaled by initial stationary effective HV/LV ratio; constant-load approximation and unmeasured moving HV accessories remain limitations','candidate_aux_kW':.4,'aux_sensitivity_kW':[.35,.4,.45],'battery_initial_temperature_C':22,'environment_temperature_C':23.34,'temperature_limitation':'OCV/R tables have only 25 C data; setting 22 C does not establish identified temperature dependence','held_out_segment':'After 20 s driving; model maps and Q fixed. Same-test segment evaluation only; second test required for broader generalization','SOC_result':'Compare integrated Ah and voltage; chemical/CAN SOC endpoint error unavailable until coordinate mapping is established','existing_provisional_targets_file':'research/validation_fix_20261006/inputs/validation_and_comparison_gates.csv','next_user_run':'ANL61905054_AlignedCandidate: both modules initial SOC as calculated, EConsumer 0.40kW, same speed, generator stays off'}
(p/'matched_candidate.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(p/'NEXT_RUN_KO.md').write_text(f'''# 다음 실행: ANL61905054_AlignedCandidate\n\n기존 설정 확인을 반복하지 않고 기존 ANL 케이스를 복사한다. 이번 변경은 실측 시험에 대응하기 위한 초기화/보조부하 후보이며 실차 검증 완료가 아니다.\n\n| 항목 | 다음 입력 | 근거 |\n|---|---:|---|\n| Module 1 Initial SOC | {soc:.6f}% | 현재 import된 OCV/R 선형표와 실측 시작 전압 {target:.6f} V·전류 {i:.6f} A에 대응하는 초기화 |\n| Module 2 Initial SOC | {soc:.6f}% | 동일 직렬 모듈 초기상태 |\n| E-Consumer Power | 0.40 kW (=400 W) | 실측 평균 LV {avg:.3f} W × 초기 정지구간 유효 HV/LV 비 {k:.6f} ≈ {k*avg:.3f} W. 정격 DC/DC 효율 측정값이 아닌 근사 |\n| Battery Defined temperature | 22°C | 실측 배터리 초기값. 맵은 25°C 단일 자료로 유지 |\n| Environment temperature | 23.34°C | 시험실 값 |\n| 속도 / 종료시간 | 기존 ANL DAT / 1144.898908 s | 현재 속도 입력은 검증 완료 |\n\n질량·ABC·용량·모터/배터리 맵·회생 설정·발전계는 고정한다. SOC Target60/하한40 등 기존 발전 조건은 임의 변경하지 않는다. 새 높은 초기SOC의 부작용으로 발전 여부는 결과에서 다시 확인한다.\n\n실행 후 velocity_ANL_aligned.csv / battery_ANL_aligned.csv / generator_ANL_aligned.csv로 export한다. 값의 단위가 W인 입력칸에는400, kW인 입력칸에는0.40을 넣는다. 프로파일/결과 케이스 참조는 새 케이스를 선택한다.\n\n0–20초 정지구간과 첫 전압은 초기화·보조부하 추정에 사용됐다. 따라서 그 구간을 제외한 주행구간에서 전압/전류/Ah/DC에너지 오차를 보고한다. 목표 오차를 맞추려고 맵·SOC·부하를 동시에 재조정하지 않는다. 기존 제안 기준은 전압RMSE≤2V·평균편차≤1V·에너지오차≤5%이며 인증기준 또는 이미 승인된 합격선으로 표시하지 않는다. SOC≤2pp 기준은 SOC 좌표 미정으로 현재 판정 불가다.\n\n0.35/0.40/0.45kW는 보조부하 근사 불확실성 시나리오다. 먼저0.40 실행을 분석한 뒤 불확실성이 결과에 중요하면 나머지를 수행한다. 결과가 목표에 못 미쳐도 실차 비교표와 모델 한계는 보고하고 독립 검증 통과를 주장하지 않는다. 61905054 단일 고SOC 시험의 한정 검증과 저SOC/다른 주행조건 일반화는 구분한다.\n''')
print(json.dumps({k:report[k] for k in ['initial_SOC_percent','estimated_mean_HV_aux_W','status']}))
