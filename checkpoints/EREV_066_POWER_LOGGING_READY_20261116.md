# ANL61905066 주행 전력 기록용 프로젝트 — 2026-11-16

기준은 기존 BEV_PUBLIC_066.proj (SHA-256 0918e3dbcae9650595cc5c812287a55dc95915229e7e4c6f59ed18631589941f)이다. 파생 파일 BEV_PUBLIC_066_PowerLogging.proj에는 BMS Monitor에 읽기 전용 입력 8개와 그 연결을 추가했다. 원래 차량·발전원 OFF 설정·주행 프로파일·시간 설정·제어식·결과 저장 설정을 유지했다. 원본 대비 기존 XML 데이터 구조와 단위, ID와 참조 순서, ZIP CRC를 확인했다. CRUISE M GUI 로딩과 실행은 아직 확인하지 않았다.

## 실행

1. BEV_PUBLIC_066_PowerLogging.proj를 연다. 모델 REEV_MBE에서 Cycle Run의 ANL61905060 한 케이스만 선택한다. 메뉴 이름은 기존 슬롯 이름이며 이 파일의 내장 속도표는 61905066 SMCT다.
2. End time 7630.892723 s를 확인하고 1회 실행한다. 사용자 실차 시험은 추가로 필요하지 않다.
3. 같은 실행의 BMS Monitor, Vehicle Monitor, Range Extender Monitor CSV를 전체 시간 범위로 내보낸다. 초기 구간과 4,091초 부근이 포함되어야 한다. BMS Monitor CSV에 Discharge Available, Drive Load In, Drive Load Out, Motor Torque Max, Motor Speed, Motor Torque Actual, Motor DC Actual, Motor Current Limit이 있는지 확인한다. 로딩·계산에 실패하면 .debug 또는 Job Log를 보존한다.

## 신호 해석과 다음 판정

Discharge Available은 BMS ECM의 Max. Power Discharge 신호다. 모델의 가용전력 출력이므로 실차 제원으로 해석하지 않는다. Drive Load In과 Out은 모터 전류 제한 전후의 부하 지령이다. 두 부하 신호는 비율이며, 제한 전 DC 요구전력 자체는 이 프로젝트에 직접 출력되지 않는다. 후속 분석에서는 양의 구동 구간에서 제한 전 토크 지령의 스케일을 무제한 구간의 실제 토크로 확인하고, 속도와 해당 요구점의 EDU 손실 및 보조전력을 적용한다. 실제 모터 DC 출력과 변환값을 비교해 경계를 확인하고 맵 밖의 구간은 미판정한다. 배터리 가용 DC 전력과 비교한 발전원 개입 후보 판정은 새 실행 CSV 이후 진행한다.

직전 분석 체크포인트 2255886b1e16a035b90a8d854518f2452f6a99ca. BUILD_QA.json에 입력 및 실행 파일 SHA-256, 채널 사양과 구조 검사 결과를 기록했다.

실행 패키지 https://chatgpt.com/library?file_id=libfile_bc92f379f1948191a8d9497a3a09db2d&account_id=personal
