# 논문 연구 자료

Bolt 기반 BEV 검증과 Volt 발전계 기반 가상 EREV/EMS 연구의 CRUISE M 입력자료 및 작업 기록입니다.

## 최신 단계 — 2026-10-13

[FTP75 발전 정지 검증 완료](research/cruise_m_build_20261011/runs/FTP75_2477s_20261012_1626/generator_verification.md): 사용자 generator.csv의 0–2477초 / 2478점에서 발전기·엔진 출력/회전수·전류·연료가 모두 0이며, 기존 배터리/속도 export와 일치합니다.

[ANL 실측 속도 실행 검증 완료](research/cruise_m_build_20261011/runs/ANL61905054_20261013/RESULT.md). [최신 재개 지점](research/cruise_m_build_20261011/empirical_alignment_20261013/RESUME.md)은 실측 초기상태·보조부하 후보 적용 후 실행입니다. 기존 설정 화면 확인은 반복하지 않습니다. 독립 실차 검증 통과는 아직 판정하지 않았습니다.

화면 자료 복구의 최신 반영 범위는 [PUBLISH_STATUS.json](research/cruise_m_build_20261011/session_recovery_20261012_1649/PUBLISH_STATUS.json)에 기록합니다.

## 복구 기록 — 2026-10-12

[CRUISE M 입력표 복구: 최신 완료 상태와 다음 시작점](research/cruise_m_build_20261011/session_recovery_20261012_1649/RESUME.md)

FTP75 실행·수치 점검과 Report Page 오류 해결까지 기존 커밋에 저장돼 있습니다. 누락된 결과 CSV와 화면 자료를 추가했습니다. FTP75 발전 정지 확인은 완료됐습니다. 과거의 첫 실행 전 체크리스트보다 최신 runs 체크포인트와 위 인계 기록을 우선합니다.

## 초기 구축 기록 — 2026-10-11

[CRUISE M 구축 기록과 재개 체크리스트](research/cruise_m_build_20261011/README.md)

- 모터 EDU 손실맵 regular DAT 및 배터리 OCV/R DAT import 성공을 화면에서 확인했습니다.
- 작동한 DAT·ZIP, 원본 export 문법, 주요 화면 6장, 설정의 확인/미확인 상태와 입력 검산을 보관했습니다.
- 마지막 REEV_MBE Data Checks는 `No data check messages`. 주행 시뮬레이션과 실측 대비 검증은 아직 미완료입니다.
- 다음 시작점은 Range Extender Control로 발전을 비활성화하고 Power Consumer 보조부하 조건을 확인하는 것입니다.
- 실제 Windows CRUISE M 프로젝트 파일은 아직 전달받지 않아 저장소에 없습니다.

## 기존 연구 자료

- [검증 보완 및 SOC/완성맵 적용 한계](research/validation_fix_20261006/README_검증보완.md)
- [Bolt + Volt Gen2 가상 EREV 자료](research/bolt_volt_genset_20261006/README_가상EREV.md)
- [이전 Range Extender 입력자료](research/range_extender_20261006/RESUME.md)

이전 65 kW 표는 가정 기반 후보이며 실측 연속 정격 검증이 아닙니다. 과거 GitHub 쓰기 거절 기록은 이전 시도에 관한 것으로, 이후 동기화 완료 기록과 최신 커밋으로 실제 반영 상태를 확인합니다.
