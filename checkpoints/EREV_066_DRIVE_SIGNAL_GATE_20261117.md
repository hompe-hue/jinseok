# CRUISE M 066 주행 신호 확인 프로젝트

- 직전 f77206df6931d2a89861f8b47961bd0a8c570a5b. 이미 사용자가 정상 실행한 066 전력 로깅 프로젝트에서 첫 30초용 파생본을 준비했다. 종료시간 30초와 출력 매 1스텝, Charge Available·Consumer Power Total·Motor Total Loss의 읽기 전용 포트만 추가했다. 내장 속도표, 기존 제어, 물리 입력, FMU 상태는 보존했다.
- ZIP 구조, 포트 원본과 단위, 직렬화 ID와 참조 순서, 변경 제거 시 원 프로젝트 XML 구조 일치를 확인했다. 평가기는 기존 1초 자료에서 DC/모터축 복원 검사 통과와 시간 해상도 미충족을 확인했다. 추가 CRUISE M 실행 결과는 아직 없다.
- 다음 실제 입력: BEV_066_DriveSignalGate_30s.proj를 REEV_MBE → Cycle Run → ANL61905060에서 30초 한 번 실행. 원본 간격의 BMS/Vehicle/Range Extender Monitor CSV, Job Log 및 Wheel FL/FR Mechanical 단자 출력(또는 토크와 속도). 휠 출력 채널이 없으면 Results 채널 화면으로 확인한다. 런타임 시간 간격·부호와 물리 연결로 S0/S3 파생본의 필요 채널을 확정한다.

[실행 파일과 검산 도구](https://chatgpt.com/library?file_id=libfile_6d97762e9ffc8191a29102e02783d857&account_id=personal)
