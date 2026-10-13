# 61905060 Dis80 诊断执行状态 — 2026-10-13 22:42 KST

用户上传 screenshot image(2).png，当前作业 Bolt_Model_Check2 / REEV_MBE / Cycle Run / ANL61905060 显示 failed。下面保留韩文操作说明供后续会话。

## 화면에서 확인한 사실

- cruise.log: Simulation started → Simulation ended → Writing results / Writing curve results.
- Copying model snapshot failed 경고. copy_file가 경로를 찾지 못했다는 메시지이며, 화면 오른쪽이 잘려 전체 경로/문장은 확인되지 않는다.
- Series result writing successful 및 Text report generation successful 기록.
- 마지막 fatal error는 Result writing failed, Simulation failed다.
- Recuperation Weight(Map)의 Characteristic 외삽 297359회 경고 및 전체7 warnings. 이 경고를 결과저장 실패의 직접 원인 또는 정상으로 확정하지 않는다.
- 현재 화면은 긴 Desktop/한글 폴더 경로를 사용한다. 한글 자체가 원인이라고 단정하지 않는다.

## 판정

로그가 보여주는 직접 실패 단계는 결과 쓰기/모델 snapshot 복사다. 수치 해석의 완료 범위와 말단 도달은 CSV 또는 전체 로그로 확인해야 하며 status failed를 물리 모델 검증 통과로 바꾸지 않는다. 80kW 변경으로 수치 발산했다고 단정하지 않는다.

## 다음 사용자 작업

1. 현재 설정을 유지한 채 새 폴더 C:\CRUISEM\Bolt_Dis80 를 만든다.
2. CRUISE M에서 프로젝트를 다른 이름으로 저장: C:\CRUISEM\Bolt_Dis80\Bolt_Dis80.proj. 탐색기에서 파일만 옮기기보다 앱에서 저장 위치를 갱신한다.
3. 결과 저장 위치를 별도로 지정해 놓았다면 존재하는 C:\CRUISEM\Bolt_Dis80\Results 폴더를 만들어 그 위치로 지정한다. 메뉴가 보이지 않으면 추측하지 말고 Results/Preferences 관련 화면에서 현재 경로를 확인한다.
4. ANL61905060의 초기SOC/온도/종료시간/주행프로파일 및 Discharge Power80kW를 유지해 같은 케이스를 다시 실행한다. 효율맵/ABC/Charge Power는 바꾸지 않는다.
5. 성공하면 velocity/battery/generator CSV3종을 받는다. 같은 실패가 이어지면 cruise.log 전체와 simulation.out을 확보한다. 직전 이미지에서 잘린 snapshot 경로와 앞선7 warnings를 읽어 경로/권한/외부참조를 구분한다.

이 기록은 파일 경로 복구 단계이며 원래 연구의 검증 미달 판정을 바꾸지 않는다. 기존 NEXT_RUN_DISCHARGE_DIAGNOSTIC_20261013.md의 단일변수 실험 조건을 유지한다.
