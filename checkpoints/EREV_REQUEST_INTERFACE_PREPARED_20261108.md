# 요청형 발전원 연결 준비

입력 근거 감사 완료 커밋 8c699b8 이후의 제어 인터페이스 준비 기록이다. 기존 source_reference.py를 변경 없이 복사하고, 2 ms 간격으로 요청·타이머·보호 동작을 검산했다. 현재 CRUISE M의 T1 FMU는 시간 예약 파형을 사용하므로, 아래 인터페이스를 가진 요청형 공급원 구현이 후속 연결 작업이다.

## 보존할 프로토콜

발전 상한 26 kW, 기동지연 0.5 s, 상승률 20 kW/s, 하강률 50 kW/s, 최소 ON 10 s, 최소 OFF 5 s다. ON은 STARTING 진입부터, OFF는 공급 0의 OFF 진입부터 측정한다. 초기 OFF는 5초 경과 상태다. 보호와 충전수용 제한이 최소 유지시간보다 우선한다. 이 규칙의 기준은 2026-11-01 재개 묶음이다. 기동지연과 램프는 실측 발전계 값으로 확정되지 않았다.

## 외부 입력 계약

| 제안 채널 | 단위 | 연결 의미 |
|---|---|---|
| V_bus_V | V | 실제 공통 DC 버스 전압. 기존 Electrical FMU 전기 포트 매핑 |
| request_on | 0 또는 1 | EMS의 발전 ON 요청. STARTING/ON 타이머와 구분 |
| P_load_W | W | 실제 부호 포함 DC 수요. 회생은 음수. 회로수지·충전수용 제한에 사용 |
| P_charge_available_W | W | 현재 배터리가 받을 수 있는 충전전력의 양수 크기 |
| protection_off | 0 또는 1 | 전압·전류·기타 보호의 즉시 정지 요청 |

유효 입력에서 허용 공급은 min(26 kW, max(0, P_load + P_charge_available))이다. 배터리 자체 충전수용을 초과하는 회생은 구동/제동 제어에서 별도로 제한해야 한다. 발전원을 0으로 줄이는 것만으로 기존 회생부하의 배터리 과충전까지 해결됐다고 해석하지 않는다. 참조 함수는 Vbus≤0에서 OFF 처리한다. 실제 최소/최대 허용 전압은 배터리·기기 보호 출력으로 protection_off에 연결해야 한다.

## 출력 및 집계 연결 계약

| 제안 채널 | 단위 | 의미 |
|---|---|---|
| I_terminal_A | A | 현재 T1에서 확인한 공급 부호를 사용한 전기 포트 전류 |
| P_target_W | W | 상한 및 수용성으로 제한한 목표 |
| P_generated_W | W | 지연·램프·보호를 적용한 실제 버스 공급 |
| state | 정수 | OFF 0, STARTING 1, RAMP 2, RUN 3, STOPPING 4 |
| start_count | 정수 | STARTING 진입 누적 횟수 |
| on_elapsed_s / off_elapsed_s | s | 기존 규칙의 유지시간 상태 |
| protection_active | 0 또는 1 | 보호 상태 |

BMS·Vehicle Current Analysis의 발전 집계는 실제 전기 공급 신호를 기준으로 연결해야 한다. 기존 native Generator가 OFF인 상태에서 나오는 0 신호를 새 공급원 실적으로 집계하지 않는다. 제한 전 DC 요구와 배터리 가용출력은 별도 스크리닝 신호다. 실제 전달 전력에서 제한 전 요구를 추정해 출력 부족 판정을 대신하지 않는다.

## 참조 검산 결과

| 시나리오 | 검산 내용 |
|---|---|
| 짧은 ON 요청 | 1 s ON, 2 s OFF 요청. 11 s 정지 시작, 11.52 s 공급 0 |
| 재기동 대기 | 12 s 재요청. OFF가 된 11.52 s부터 5 s 뒤 16.52 s 재기동 |
| 충전수용 0 | 6 s 이후 부하 10 kW 한도까지 즉시 공급 제한 |
| 비상 보호 | 6 s 즉시 OFF. 최소 ON보다 보호 우선. 11 s 재기동 가능 |
| 무효 전압 | 6 s의 0 V 입력에서 공급 0. 5 s OFF 유지 후 재기동 |

5개 모두 참조 규칙 검산을 통과했다. 각 시나리오 0–20 s, 10,001개 표본의 상세 기록은 traces에 보존했다. 이 검산은 외부 Python 참조 함수의 규칙 확인이다. 요청형 FMU의 Windows 바이너리, CRUISE M 포트 연결, 주행 EMS 실행은 아직 준비/확인되지 않았다. 기존 T1 결과를 이 상태기의 실행 검증으로 확대하지 않는다.

## 다음 시작점

다음 구현 대상은 이 입력·출력 계약을 갖는 요청형 Electrical FMU와 실제 전력 집계 연결이다. 포트 생성/매핑 후 초기 OFF, 짧은 요청, 충전수용 제한, 보호 우선, 재기동 대기를 같은 프로젝트에서 확인한다. 그 뒤 기존 재개 지침의 제한 전 요구/배터리 가용출력 스크리닝을 진행한다. 엔진·발전기 연료맵 채택은 해당 근거가 확보될 때 별도로 진행한다.

원래 source_reference.py의 SHA-256과 결과 해시는 SHA256SUMS.txt에 기록했다. 검산 실행은 python verify_protocol.py다.
{
  "reference_implementation": "copied unchanged from 2026-11-01 resume bundle",
  "step_s": 0.002,
  "cases": {
    "short_request": {
      "status": "REFERENCE_PASS",
      "rows": 10001,
      "start_events_s": [
        1.0
      ]
    },
    "restart_dwell": {
      "status": "REFERENCE_PASS",
      "rows": 10001,
      "start_events_s": [
        1.0,
        16.52
      ]
    },
    "charge_curtail": {
      "status": "REFERENCE_PASS",
      "rows": 10001,
      "start_events_s": [
        1.0
      ]
    },
    "emergency": {
      "status": "REFERENCE_PASS",
      "rows": 10001,
      "start_events_s": [
        1.0,
        11.0
      ]
    },
    "zero_voltage": {
      "status": "REFERENCE_PASS",
      "rows": 10001,
      "start_events_s": [
        1.0,
        11.0
      ]
    }
  },
  "CRUISE_runs": 0,
  "scope": "Reference timer/protection checks only; no request-driven Electrical FMU built or connected"
}
