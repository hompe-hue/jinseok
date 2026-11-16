# EREV 재기동 시험 20초 프로파일 수정

기존 관측 기록은 16초에서 끝났다. 원본 Restart 프로젝트의 명시적 End time과 저장된 FMU DefaultExperiment stop_time은 20초다. ANL61905060 정차 프로파일의 시간 배열은 [0, 16] s이고 속도 배열은 [0, 0] km/h였다. 보고서 그래프에도 16초 상한이 저장돼 있었다. Cycle Run의 입력 프로파일 종료점에 맞춰 계산이 끝난 것으로 판단한다. 검증된 변경은 프로젝트 XML의 해당 시간 배열 [0, 16] → [0, 20] s 한 곳이며 속도와 나머지 프로젝트 바이트는 유지했다.

EREV_Request26_Restart_Profile20s.proj를 열고 ANL61905060 / End time 20 s로 실행한다. FMU는 C:/CRUISEM/EREV_Request26.fmu를 사용한다. 최신 계산의 Generator Monitor, FMU Plus, BMS Monitor, Vehicle Monitor를 전체 0~20 s 범위로 내보낸다. 그래프 축이 16초까지만 보이면 새 계산 결과의 실제 마지막 표본과 내보내기 범위를 확인한다.

파일 구조와 프로파일 데이터 변경은 로컬에서 검증했다. CRUISE M 재실행 및 재기동 결과 판정은 대기 중이다. 기존 16초 분석은 cccc64c8df1157f66fd65de45c358340c2e76f4b에 있다.
Original PROJ SHA256 07d807687022a96d5d2e75f963e7c4ef412c4ca21d75fbb55af03529b0780d5e
Patched PROJ SHA256 88a52de6fb54cdd655a9c04949deea79f8f3edbc1c6bb3715345f522b66cbb19
FMU SHA256 6cca9fd6f20595387df9924d27dfccc9540efa712409664667477002571d6294
Verified only the stationary velocity-profile time array payload changed. CRUISE M execution pending.

패키지 https://chatgpt.com/library?file_id=libfile_d53ac30ea688819188dce08a5825c557&account_id=personal
