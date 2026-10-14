# 먼저 가속1회 → 추가 가속1회 → 주행거리2회

## 1. 가장 먼저 C2_ACC_SOC94.proj를 실행

확정 기본 C2는 C2_CAL_61905060.proj이다. 이번 사본은 시험 SOC/온도/시간/작업 선택만 변경했다. 기본 C2를 덮어쓰지 않는다.

1. projects/C2_ACC_SOC94.proj를 CRUISE M에서 연다. 모델은 기존 실제 BEV 비교에 쓴 **REEV_MBE**를 선택한다. REEV_PhysE 결과와 섞지 않는다.
2. Cases에서 **Performance → FLA**만 선택한다. Cycle Run/NEDC 등 다른 case 일괄 계산은 선택 해제한다. 화면에도 FLA의 기존 시나리오가 적용됐는지 확인한다. 저장파일의 active case를FLA로 설정했지만 프로그램의 적용 여부는 아직 확인하지 못했다.
3. 별도 주행속도 프로파일은 없다. 기존 **Full Load Acceleration** 작업을 사용한다. Accelerator pedal limit=1.0(100%), Launching control=Deactivated, 초기 속도0, SOC94%, 배터리/환경25°C, 최대40초이다.
4. Data Checks 후 실행한다. 초기 SOC94%, 가속 페달100%가 유지되는지, 엔진·발전기가0인지 출력으로 확인한다. 가속 페달/토크 제한/가용출력/모터출력도 추가 저장한다. FLA 작동이나 BEV 조건이 확인되지 않으면 이 결과를 공식 가속 비교로 쓰지 않는다.
5. **CSV 표본 간격0.01초 권장, 최대0.05초**로 내보낸다. 기존1초 CSV로6.5초를 정밀 비교하지 않는다. global output_after_every는1로 줄였지만 실제 출력 시각 간격을 확인한다.
6. battery/velocity/generator CSV3개와 솔버 로그를 내보내고, 실행한 프로젝트도 저장한다. 예: ACC94/battery.csv, ACC94/velocity.csv, ACC94/generator.csv.

이 첫 실행으로 FLA 작업 연결과 방전제한 영향을 확인한다. C2의 표에80kW가 들어 있다는 사실만으로 최종 팩 가용출력이 반드시80kW라고 단정하지 않는다. 실제 적용 위치와 출력 제한을 결과로 확인한다. 공식6.5초에 맞추려고 방전제한표를 수정하지 않는다.

## 2. C2_ACC_SOC100.proj

같은 방식으로Performance/FLA를 실행한다. SOC100%와94% 차이를 구분한다. 100%는 현재 holdout 범위를 넘는 시험 조건이며 새 검증 결과가 아니다. 공식 비교는0–60mph=96.56064km/h를 우선 기록하고0–100km/h는 부가 지표로 기록한다. 시간을0부터 계산하고1-foot rollout은 임의로 빼지 않는다. 질량1757.6704kg는 유지하며 GM 시험질량과 같다고 주장하지 않는다.

## 3. EPA 원본 반복 주행2회

|프로젝트|Cases 선택|프로파일|초기조건|
|---|---|---|---|
|C2_RANGE_UDDS_SOC100.proj|Cycle Run → C2_RANGE_UDDS_SOC100|같은 이름의 내장 EPA UDDS 반복|SOC100%,25°C|
|C2_RANGE_HWFET_SOC100.proj|Cycle Run → C2_RANGE_HWFET_SOC100|같은 이름의 내장 EPA HWFET 반복|SOC100%,25°C|

프로파일은이미 내장했다. 따로 DAT import는 필요하지 않다. Profile pool의 다른 ANL61905061/FTP75/NEDC 항목을 선택하지 않는다. 확인용 단일 및 반복CSV/DAT는profiles/에 있다. 원본은mph→km/h를 정확히1.609344배 변환했다. UDDS 원본은0–1369초, HWFET0–765초이다. 각각60회 반복하며 이어지는 영속도 표본 사이1초 연결 간격을 사용한 연구용 근사이다. 인증 예비주행·휴지·온도절차 전체를 재현한 것은 아니다.

각 시험은 새로운 파일을 열어 SOC100%에서 시작한다. 앞 시험의 마지막 SOC를 이어받지 않는다. 1초 출력으로battery/velocity/generator CSV3개씩을 저장한다. 단거리 소비전력만으로60kWh를 나눠 인증 주행거리라고 보고하지 않는다.

최대시간은 UDDS82199초/HWFET45959초의 **모델 시간 상한**이다. 전 시간을 반드시 계산할 필요는 없다. SOC20% 도달 또는 요구속도보다3.218688km/h 이상 부족한 상태가10초 이상 지속되면 정지하고 그 시점까지 CSV를 내보낼 수 있다. 이 기준은C2의 모델창/연구 진단 기준이며 EPA 인증 종료 기준이 아니다. 충전 손실·차량별 조정계수·실차 BMS 창이 아직 확인되지 않아 결과는 “C2 가용 모델창 거리 및 EPA 표기와 조건부 비교”로 표시한다.

## CSV 신호

- battery: Time, Voltage, Current, SoC(기존 포맷, 방전 Current 음수).
- velocity: Time, Actual Velocity, Desired Velocity, E-Motor Current, E-Consumer Current. 가속에서Desired Velocity가 제공되지 않으면 실제 속도는 반드시 저장한다.
- generator: 기존7신호 Actual Engine Speed, Cumulated Fuel Consumption, Current, Desired Engine Speed, Fuel Massflow, Power Generator, Power ICE.
- 추가: 실제 가속 페달, 모터토크/기계출력, BMS 가용 방전출력 및 제한 신호. 이름은 실제 프로그램의 명칭으로 저장한다. 없는 채널을 만들어내지 않는다.

평가 코드는scripts/evaluate_C2_performance.py이다. 가속94% 예: `python evaluate_C2_performance.py --mode ACC --initial-soc 94 --exports ACC94 --output ACC94/result.json`. 주행거리에서는 --mode UDDS 또는HWFET와 --initial-soc100을 쓴다. 사용자 CSV를 받으면 실제 형식과 신호를 확인한 후 계산한다. 도심·고속 둘 다 검토된 뒤에만0.7×(0.55×도심 모델거리+0.45×고속 모델거리)의 조건부 예시를 계산한다. 인증 재현 PASS로 자동 표기하지 않는다.
