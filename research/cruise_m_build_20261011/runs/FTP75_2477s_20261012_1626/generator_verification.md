# FTP75 발전 정지 검증 완료

사용자 제공 generator.csv 원본을 검증했다. 0–2477 s, 1 s 간격, 2478점이며 battery_FTP75.csv 및 velocity_FTP75.csv의 시간축과 일치한다. 모든 수치는 유한수다. 발전 모니터 전압과 SOC Target 채널은 기존 BMS 전압/SOC와 각각 최대 차이 0 V, 0 %p로 일치한다. SOC Target이라는 모니터 채널명만으로 제어 목표 SOC라고 재정의하지 않는다.

| 신호 | 단위 | 최소 | 최대 | 0이 아닌 점 |
|---|---|---:|---:|---:|
| Power Generator | kW | 0 | 0 | 0 |
| Cumulated Fuel Consumption | kg | 0 | 0 | 0 |
| Fuel Massflow | kg/h | 0 | 0 | 0 |
| Actual Engine Speed | rpm | 0 | 0 | 0 |
| Current | A | 0 | 0 | 0 |
| Power ICE | kW | 0 | 0 | 0 |

이 FTP75 실행의 기록된 전 구간에서 발전기 출력, 엔진 출력/회전수, 발전계 전류, 연료 유량 및 누적 연료가 모두 정확히 0이다. 따라서 기존 배터리/속도 결과를 발전이 개입하지 않은 BEV 실행 결과로 사용할 수 있다. 1 s export 자료의 검증이며 실차 적합성 검증이나 다른 SOC 조건의 발전 정지 보장은 아니다.

Load Signal Generator, SOC max/min, Power Threshold Activation 등의 명령·설정 신호가 0이어야 하는 것은 아니다. 모든 채널의 최소/최대/첫값/끝값은 generator_verification.json에 보관했다. 실제 출력·연료와 명령/설정을 구분한다.

직전 스크린샷의 약 1200–2477 s 부분 확인 한계는 이번 전체 CSV로 해소됐다. 같은 그래프를 다시 제출하거나 시뮬레이션을 다시 실행할 필요가 없다.

다음 단계는 기존 선정 Bolt 공개 실험자료에 맞춰 FTP75 입력조건을 대조하는 것이다. 기존 차량 질량·보조부하·시험 온도·SOC 정의·주행저항·속도 프로파일 대응과 실제 CRUISE M 적용 여부를 확인하고, 확인된 동일 조건에서 실험 trace와 비교한다. 연비 숫자에 맞추기 위한 임의 동시 보정이나 EREV 전환은 이 단계의 완료조건에 섞지 않는다.
