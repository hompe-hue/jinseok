# EREV 재기동 시험 — 16초 기록 판정 보류

CSV 5개는 시간축이 일치하며 0~16초, 2 ms 간격, 8,001행이다. 발전원이 11.522초에 OFF로 전환된 뒤 12.000초에 재기동 요청이 들어왔다. 16초까지 상태 OFF, 발전 단자 출력 0 kW, 누적 기동 1회를 확인했다. DC 버스 최대 잔차는 0.000003912 kW다.

관측된 OFF 시각을 기준으로 최소 정지 5초가 충족되는 시각은 16.522초다. 따라서 현재 기록으로는 재요청 후 관측 구간의 기동 억제만 확인했다. 2차 기동과 26 kW 출력 복귀는 판정 보류다. 기존 판정기가 행 수 조건 10,001행에서 중단한 로그를 보존했다.

배포된 EREV_Request26_Restart.proj의 value 및 stop_time은 둘 다 20.0초다. 제출 CSV가 16초로 끝난 원인은 현재 데이터로 특정할 수 없다. CRUISE M에서 20초까지 계산된 결과가 있으면 전체 시간 범위로 다시 내보낸다. 계산이 16초까지라면 Restart 프로젝트, ANL61905060, End time 20초를 확인해 해당 시험만 실행한다. Generator Monitor, FMU Plus, BMS Monitor, Vehicle Monitor CSV 4개(0~20초, 2 ms)를 같은 결과에서 내보낸다.

직전 완료: 충전 제한 시험 15/15 통과, 커밋 9de8db02a4f354d99b2ee42ebd2f7a602497eda0. 다음 시작점은 20초 재기동 CSV 판정이다.

결과 ZIP https://chatgpt.com/library?file_id=libfile_136766c2c77481918af6ed07dec12891&account_id=personal
