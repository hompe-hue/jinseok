# 요청형 전원 실행 CSV 검토

2 ms, 0–16 s, 8,001개 표본의 시간축이 세 파일에서 일치한다. 실제 부하는 전 구간 10 kW이고 배터리는 약 10 kW를 계속 방전했다. 배터리 단자 순방전에너지는 44.444444 Wh이며 SOC는 81.252051%에서 81.187229%로 감소했다. 부하와 배터리 단자전력으로 계산한 다른 공급원의 순기여는 최대 절댓값 0.000003912 kW다. 이번 자료에서 요청형 공급원 26 kW의 주입은 관측되지 않는다.

Generator Monitor FMY 26.csv의 실제 열 이름은 기존 Range Extender Monitor다. 엔진 속도·연료·native Generator 값이 0인 것은 기존 native 발전계 OFF 조건과 일치한다. 이 파일에 새 Generator Monitor의 Request ON, Generated W, State, Start Count, 타이머·보호 신호는 없다. 파일명만으로 새 모니터의 실행 출력으로 판단하지 않았다.

직접 Plus 단자 CSV도 이번 묶음에는 없다. 전력수지 추론은 기존 정차 버스 구조와 별도 미측정 저장소 영향이 작다는 범위에 따른다. 요청형 FMU가 어떤 입력을 받아 어떤 상태에 있었는지, 파일/포트/모델 선택 또는 실행에서 어디가 달랐는지는 현재 CSV로 확정할 수 없다. 새 입력을 보지 않고 지연·상한·배터리 값을 수정하지 않는다.

다음 시작점은 이번 실행을 저장한 EREV_Request26_Connected.proj와 새 Generator Monitor CSV다. Results의 Data Browser에서 Generator Monitor를 검색해 Request ON, Generated W, State, Start Count가 있는 항목을 내보낸다. 해당 항목이 없으면 저장한 .proj와 현재 모델 제목·Data Browser 목록이 보이는 화면으로 구성부터 확인한다. 같은 기존 Range Extender Monitor 결과를 반복해서 내보낼 필요는 없다.

고정 파형 T1 완료 판정은 유지한다. 이번 요청형 연결 시험의 공급·타이머 판정은 보류한다. 원본 CSV 세 개, 파일 해시, 전력수지 표본 계산, 재현 코드와 체크포인트를 보존했다.
{
  "status": "REQUEST_RUN_SUPPLY_NOT_OBSERVED_NEEDS_INPUT_AND_STATE",
  "samples": 8001,
  "dt_max_s": 0.002000000000000668,
  "start_s": 0.0,
  "end_s": 16.0,
  "actual_demand_min_kW": 9.999999999999996,
  "actual_demand_max_kW": 10.000000000000004,
  "battery_discharge_min_kW": 9.99999608807694,
  "battery_discharge_max_kW": 9.999999999999996,
  "inferred_net_other_supply_max_abs_kW": 3.911923059263245e-06,
  "battery_terminal_discharge_Wh": 44.444444442933914,
  "soc_start_percent": 81.2520512871387,
  "soc_end_percent": 81.18722915591222,
  "native_generator_power_max": 0.0,
  "supplied_generator_export": "Range Extender Monitor channels",
  "requested_new_monitor": "Generator Monitor: Request ON, Generated W, State, Start Count, protection and timers",
  "new_request_state_channels_present": false,
  "Plus_export_present": false,
  "source_hashes": {
    "generator": "3c5bc5763ecb3349cb2ca367935cda103a549f28700e7e8840b4d9066e1d8680",
    "bms": "8748e51efcc07c7b13e21c19e3e3413e07ec7d575a0cc3f3e7a83146f2582942",
    "vehicle": "eaa3a89fd5336141dfe534b8df3538f8aa363452986bd6e11199c316bbb8f856"
  },
  "conclusion": "No positive net source contribution observed through the measured battery/load balance. The exact request, voltage, charge-acceptance or FMU execution cause remains unidentifiable from these exports.",
  "inference_boundary": "Bus balance uses the accepted stationary topology and neglects unmeasured transient storage; direct FMU terminal measurements are absent.",
  "previous_T1_status": "Existing validated fixed-waveform T1 remains numerically passed",
  "next_start": "Inspect actual Generator Monitor CSV and user-saved EREV_Request26_Connected.proj before modifying or rerunning"
}
