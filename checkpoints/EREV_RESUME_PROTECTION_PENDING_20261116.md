# 연구 재개 체크포인트 — 2026-11-16
## 확인한 최신 상태
GitHub checkpoints 목록과 2026-11-10 연구 비판검토/연료근거 보고서를 대조했다. 11월12일 행정 제출자료 작업은 시뮬레이션 상태를 변경하지 않았다.
요청형 26 kW 정상 펄스와 공통 DC 버스 검증 완료. 보호정지/충전수용 제한/재기동 시험은 PREPARED 상태이며 검토한 기록에서 실제 PASS 증거를 확인하지 못했다.
BEV 순에너지 +5.98~+8.85% 오차 및 저SOC 적용 한계는 미해결 상태를 유지한다.
새 연료맵 수치화·통합 및 S0–S4 주행 비교도 미완료다.

## 현재 단계: Protection 실제 실행 및 평가
다음 파일은 새로 생성하거나 수정하지 않고 기존 검증된 패키지를 사용한다.
패키지: EREV_Request26_Protection_ChargeLimit_Restart_Package.zip
Library: libfile_08a42c22f2348191bead7ee1e7b95535
패키지 SHA256: cab9deaeea888aa37fb3785657e412f6cc2103622b1aa96b09d47e6b0351f687
실행: EREV_Request26_Protection.proj
프로젝트 SHA256: 8b87fc92263fe90cb8a7e6cdb27e7b2d6d118fc36f9a737a3638d84d6248187f
FMU: 포함된 EREV_Request26.fmu를 C:\CRUISEM\EREV_Request26.fmu에 배치.
Case: ANL61905060. End time: 16 s. 정차/부하 10 kW 원래 설정 유지.

## 제출할 실행 증거
같은 실행의 Generator Monitor, Electrical FMU 1 / Plus, BMS Monitor, Vehicle Monitor CSV 4개.
원래 헤더와 단위 행 유지. 출력시간 0~16 s, 기존 2 ms 설정 유지.
가능하면 실행 후 저장한 PROJ와 Job Log 동봉.
오류 시 화면과 생성된 debug 파일 보존.
REFERENCE_ONLY 및 QA_SYNTHETIC_ONLY 자료는 실제 실행 결과로 사용하지 않는다.

## 예상 반응과 판정
기대 반응: 1초 이후 ON 요청, 6.0~6.1초 보호입력. 약6초 공급0, 약11초 재기동, 약12.8초 26kW 회복.
위 시간은 모델의 예상값이며 새 실행 관측값이 아니다. 기존 2ms 동기화와 ±6ms 이벤트 판정 유지.
기존 evaluate_scenario.py --case Protection으로 네 CSV 평가.
공통버스잔차0.1kW, 부하오차0.1kW, 전류오차0.5A 및 기존 모든 조건 유지.
코드/가정/전력부호/포트/입력·출력단위를 변경하지 않는다.

## 완료 및 다음 시작점
이번 완료: 최신 상태 대조, 중복 실행 배제, 보호정지 실행파일·증거·기준 재연결.
미완료: CRUISE M 실제 보호정지 실행 및 판정. 이 세션에서 실행하지 않았다.
현재 시작점: 보호정지 실제 실행 4 CSV 수신 후 판정·저장·commit.
그 단계 완료 후 충전수용 제한, 이후 재기동 순서. 후속 단계의 합격이나 EMS/연료 개선을 미리 주장하지 않는다.

## 근거
checkpoints/EREV_REQUEST26_PROTECTION_CHARGELIMIT_RESTART_PREPARED_20261108.md
checkpoints/EREV_REQUEST26_COMMON_DC_BUS_COMPLETE_20261108.md
THESIS_CRITICAL_REVIEW_KO.md (libfile_b545d27567b08191936a80d8bd04736d)
RESULT_KO.md (libfile_dcdecd49140c8191af2c1a0559446d6d)
