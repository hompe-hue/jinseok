# Range Extender 입력자료 재개 체크포인트 — R65C_04

현재 GitHub 상태(2026-10-06): 연결 계정과 저장소 소유자 `hompe-hue`, 지침의 비공개 저장소 `hompe-hue/jinseok`를 확인하여 반영을 완료했다. 자료 커밋 `0aa56ea76eaa8d0c3e9a25d4ef568b1cb1b7718b`의 연구 파일 70개를 GitHub에서 다시 읽고 로컬 Git blob 해시와 전부 대조했다. 최신 상태는 저장소 루트 `checkpoints/github_sync_20261006.json`을 따른다. 아래의 쓰기 보류 문구는 R65C_04 작성 당시의 과거 기록이며 현재 작업을 막는 규칙이 아니다. 연구 입력과 계산값은 변경하지 않았다.

완료: 기존 R65C_03의 입력 CSV 41개·엑셀 44시트·설명서 복구. 원본 체크포인트 01~03과 맵은 수정하지 않았다. 잘린 ZIP의 완전한 63개 멤버에 CRC를 확인했고, 원본 manifest 62개 파일의 SHA256 및 엑셀/CSV 41표 전체 일치를 확인했다. 마지막에 잘린 엑셀은 별도 정상 저장본으로 대체하고 원래 패키징 스크립트가 포함하도록 지정한 정상 DOCX도 넣어 ZIP을 완성했다.

다음 시작점: CRUISE M 별도 작업 사본에서 Engine Program 열·질량유량 단위를 확인하고, 650 V 발전 링크/DC 변환 및 저속·시동·단일 온도 처리를 결정한 후 정속점과 DC 전력수지를 검사한다. 현재 GUI 입력·프로그램 실행은 미완료이며 시뮬레이션 결과를 생성하지 않았다.

대응표: 엑셀 INDEX의 CSV/시트 매핑, Scalars와 UI_fields, 설명서의 화면별 표를 이용한다. AG80_FL_Q1Q4와 AG80_ETA_Q1Q4는 가상 후보다. 650 V와 효율 %를 유지하고 Q4 토크는 음수다. A는 설계 가정이고 REF에도 EPA 보간·추정이 포함된다. 실제 Honda/EMRAX 65 kW 발전계의 실측 입력표로 사용하지 않는다.

GitHub: hompe-hue/jinseok 읽기 확인 완료. 이전 증거 문서의 자동 승인 검토 거절을 보존하여 저장소 쓰기를 재시도하지 않았다. 구체적인 이전 거절 사유는 현재 자료에서 확인되지 않는다. 이 폴더의 Git은 복구 산출물만 기록하는 별도 snapshot이며 과거 3618ce2의 전체 이력을 복원한 것이 아니다.

재개 번들: `git clone RangeExtender_Recovery_20261006.bundle recovered-inputs`로 복구한다. CSV 동일성/해시 검증: `python RangeExtender_CRUISE_M/scripts/verify_recovery.py`. 기존 생성 스크립트에는 과거 절대경로가 남아 있으므로 자동 재실행하지 않는다.
