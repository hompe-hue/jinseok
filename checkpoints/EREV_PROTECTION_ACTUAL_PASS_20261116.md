# 요청형 26 kW 발전원 보호정지 시험 완료 — 2026-11-16

직전 재개 기록: 862214ddfbe1afad4da1ae6cec5316f933b68cf4.
사용자 제출 CRUISE M CSV 5개를 검토했다. 기존 evaluate_scenario.py의 Protection 판정 15/15 통과. 정규화된 전력 데이터 8,001점, 0~16초, 2 ms. 저장된 실행 PROJ와 Job Log는 제공되지 않아 프로젝트 해시 또는 Job ID는 독립 확인하지 않았다.

| 항목 | 결과 |
|---|---|
| 최초 기동 | 1.002 s |
| 보호 입력 및 OFF 상태 전환 | 6.004 s. 동일 시각 단자 표본은 12.921373 kW |
| 단자 출력 0 kW | 6.006 s. 배터리가 10 kW 부하 공급 |
| 재기동 | 11.004 s. OFF 상태 전환부터 5.000 s |
| 정상운전 상태 및 출력 복구 | 12.804 s 상태 전환, 단자 25.981197 kW. 12.806 s에 26.000956 kW |
| 최대 공통 DC 버스 잔차 | 0.000003911923 kW (기준 0.1 kW) |

Range Extender CSV는 보조 확인에 사용했다. 시간축은 네 판정 입력과 일치하고 엔진 속도·축출력·내장 발전기 출력·연료량은 0이었다. 보조 CSV SHA-256: 83d4a869b045380091ac2a4b8b5d310fba3b397f150d0abaa5a65de2ae219bf3. 나머지 입력 해시와 판정은 RESULT.json에 기록했다. 이 보호정지는 시뮬레이션의 외부 보호 신호에 대한 가상 발전원 응답을 검증한다.

## 모델 출처와 실차 비교 기준
차량·배터리·구동계의 기반은 Chevrolet Bolt EV. 가상 직렬 발전계의 상세 모델 후보는 별도 차량인 Chevrolet Volt Gen2 L3A 1.5 L 엔진과 MGA 전기기기다. 현 가상 DC FMU는 26 kW 상한으로 요청·보호·출력을 검증한다. Volt 상세 효율·연료맵 통합과 연료 검증은 후속 단계다. Volt의 동력분기 구조는 현재 가상 직렬 구조와 다르다.

사용자 전달 지도교수 의견은 실차 대비 총 DC 소비에너지 오차의 절댓값 15% 이내를 연구 진행에 수용 가능하다는 것이다. 보고된 4건 +5.98~+8.85%는 이 범위에 들어간다. 초기 ±5%는 별도의 정확도 목표로 기록한다. 수용 판정 대상은 동일 경계와 구간의 총 DC 소비에너지 비교로 한정하며, 저SOC 성능이나 연료 정확도에 확대하지 않는다. 기존 검증 계산은 재수행하거나 덮어쓰지 않았다.

## 다음 시작점
기존 패키지 libfile_08a42c22f2348191bead7ee1e7b95535의 EREV_Request26_ChargeLimit.proj. SHA-256 5a8574940fb83402edd1b11927519b99a73f8105d4e09c5d1e497723ec0bb1d0 확인. 동일 FMU 경로 C:/CRUISEM/EREV_Request26.fmu, ANL61905060 / 16초. 다시 같은 실행의 Generator Monitor, Electrical FMU 1 / Plus, BMS Monitor, Vehicle Monitor CSV 4개를 내보낸다. 6초 이후 충전 허용량 0 W 입력, 발전 26→10 kW, 배터리 순충전 약 0 kW가 예상된다. 실행 결과 수신 후 기존 --case ChargeLimit 판정. 재기동 시험은 그다음이다.

결과 ZIP: https://chatgpt.com/library?file_id=libfile_19e41979870c8191b8175d3dda7ef9b8&account_id=personal
