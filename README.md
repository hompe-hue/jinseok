# 논문 연구 자료

Bolt 기반 BEV 검증과 Volt 발전계 기반 가상 EREV/EMS 연구의 CRUISE M 입력자료 및 작업 기록입니다.

## 최신 작업 — 2026-10-11

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
