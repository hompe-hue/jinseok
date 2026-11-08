# 요청형 발전원 실제 모니터 검증 완료

접수 파일 Generator Monitor FMY 26(1).csv는 새 Generator Monitor의 요청·상태·실제 발전전력·타이머를 포함한다. 0–16 s, 2 ms 간격, 8,001개 표본이다. 이전의 native Range Extender Monitor CSV와 다른 데이터이며, 이전 공급 미관측 실행의 BMS/Vehicle 자료와 결합하지 않았다.

| 사건 | 실제 시각 |
|---|---|
| 외부 ON 요청 | 1.000 s |
| STARTING 진입·기동횟수 1 | 1.002 s |
| RAMP 진입 | 1.502 s |
| RUN·26 kW 도달 | 2.802 s |
| 외부 OFF 요청 | 2.000 s |
| STOPPING 진입 | 11.002 s |
| OFF·발전 0 | 11.522 s |

기동지연은 STARTING→RAMP 기준 0.500 s, 최소 ON은 STARTING→STOPPING 기준 10.000 s, 정상 정지 램프는 0.520 s다. 요청에 대한 상태 진입의 2 ms 차이는 이 FMU의 통신 구간 끝 상태 갱신 정의와 일치한다. 상승률 20 kW/s, 하강률 50 kW/s, 기동 1회, 최대 26 kW를 확인했다.

시간축을 이동하지 않은 기존 시험 지령 대비 RMSE는 0.021329396 kW로 0.100 kW 기준을 충족한다. 최대 순간 오차는 0.100000 kW다. 기존 기준은 RMSE이며, 최대 순간 오차를 새 합격 기준으로 변경하지 않았다.

공급 시 Generated W는 양수, Terminal Power W는 같은 크기 음수이며 Terminal Current A도 음수다. 보고된 발전에너지는 65.794444 Wh로 발전전력 CSV의 사다리꼴 적분과 일치한다. 이는 전원 내부 출력과 집계의 자기일관성 확인이다. 전기 단자 실제 측정과 배터리 수지를 별도로 확인해야 한다.

Protection Active는 t=0의 초기 표본에서 1이고 0.002 s부터 0이다. 최초 입력 전압 초기화 구간과 일치하는 패턴이다. 이번에는 ON 요청에 대한 최소 유지와 정상 정지만 시험했으며, 보호 우선 정지·충전수용 포화·재기동 대기의 실제 CRUISE 동작은 이 단일 펄스로 검증한 범위에 포함하지 않는다.

## 완료 범위와 다음 시작점

요청·상태 전이·타이머·출력 파형·부호·전원 에너지 집계를 확인했다. 새 요청형 발전원이 외부 요청에 반응하는 실제 실행 결과가 확보됐다. 실제 실행 프로젝트의 정확한 저장 해시와 런타임 로그까지 이 CSV만으로 식별한 것은 아니다.

다음은 같은 실행의 Electrical FMU 1 Plus, BMS Monitor, Vehicle Monitor CSV다. 이번 요청 모니터의 시간축과 전압·전류를 대조하고, 실제 10 kW 부하에서 배터리 약 16 kW 충전 및 공통 DC 버스 수지, 발전전력 집계 연결을 확인한다. 이미 완료된 이번 실행의 CSV를 내보내면 된다.

원본, SHA-256, 이벤트 시각, 상세 수치 판정 및 한계는 RESULT.json에 기록했다. 표본별 정상화 결과는 NORMALIZED_TRACE.csv다. 재현 명령은 python analyze_monitor.py다.
{
  "status": "REQUEST_MONITOR_NUMERIC_GATES_PASS",
  "checks": {
    "complete_2ms_window": true,
    "request_at_1_to2": true,
    "one_start_only": true,
    "startup_delay_0p5s": true,
    "minimum_on_10s": true,
    "normal_stop_0p52s": true,
    "rising_rate_20kW_s": true,
    "falling_rate_50kW_s": true,
    "maximum26kW": true,
    "unshifted_profile_RMSE_0p1kW": true,
    "terminal_power_sign": true,
    "energy_integration": true,
    "charge_acceptance_limit": true,
    "no_supply_during_start": true,
    "zero_after_off": true,
    "no_protection_after_initialization": true
  },
  "source_sha256": "daacd48d88478c0cc10101878377a94e20606a2975fa467c6956e1ca7d308701",
  "samples": 8001,
  "output_step_s": 0.002,
  "request_transitions": [
    {
      "time_s": 0.0,
      "value": 0.0
    },
    {
      "time_s": 1.0,
      "value": 1.0
    },
    {
      "time_s": 2.0,
      "value": 0.0
    }
  ],
  "state_transitions": [
    {
      "time_s": 0.0,
      "value": 0.0
    },
    {
      "time_s": 1.002,
      "value": 1.0
    },
    {
      "time_s": 1.502,
      "value": 2.0
    },
    {
      "time_s": 2.802,
      "value": 3.0
    },
    {
      "time_s": 11.002,
      "value": 4.0
    },
    {
      "time_s": 11.522,
      "value": 0.0
    }
  ],
  "start_count_transitions": [
    {
      "time_s": 0.0,
      "value": 0.0
    },
    {
      "time_s": 1.002,
      "value": 1.0
    }
  ],
  "protection_transitions": [
    {
      "time_s": 0.0,
      "value": 1.0
    },
    {
      "time_s": 0.002,
      "value": 0.0
    }
  ],
  "startup_delay_s": 0.5,
  "minimum_on_elapsed_s": 10.0,
  "stop_ramp_elapsed_s": 0.5199999999999996,
  "profile_RMSE_kW": 0.021329395962110257,
  "maximum_profile_error_kW": 0.10000000000004405,
  "reference_timing_shift_s": 0.0,
  "generated_energy_Wh": 65.79444444444445,
  "generated_energy_trapezoid_Wh": 65.79444444444445,
  "start_request_to_state_latency_s": 0.0020000000000000018,
  "accepted_scope": "Actual external request, state timers, source output, sign and internal energy accounting",
  "pending_scope": "Same-execution Plus, BMS and Vehicle exports for physical terminal, battery and aggregation checks",
  "previous_no_supply_run": "Different export set. Not combined with this monitor.",
  "limitations": "Initial protection flag at t=0 clears at 0.002 s. No protection or charge-curtailment experiment is validated by this request pulse alone."
}
