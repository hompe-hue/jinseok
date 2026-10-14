# 재개와 재현

사용자는START_HERE_KO.md의 첫 가속 시험부터 진행한다. 실제 CRUISE M 결과는 아직 없으므로 프로젝트·로그·CSV를 보관한다. 기존 온난 C2 baseline은baseline/에 보존했다.

Python 분석 환경에는numpy,pandas,scipy,nptdms,lxml이 필요하다. `scripts/evaluate_C2_performance.py`는 실제 CRUISE CSV만 평가한다. `scripts/build_C2_performance_projects.py`는 baseline에서 사본을 재구성하며 proprietary solver 실행을 하지 않는다.

064/067 원본 TDMS 약380MB는 패키지에 넣지 않았다. sources/source_manifest.json의 정확한공개URL·크기·SHA256으로원본을 sources/ANL61905064.tdms, sources/ANL61905067.tdms에복구하면 `scripts/replay_C2_depletion.py`를 다시 실행할 수 있다. replay/의 두 CSV는 샘플이 아닌 이번 평가에 쓴 전체 고유 계측시각의 재현 결과이다. SOC구간별 수치·요약·그림도 포함했다. 다른 CSV의 해시를 원본TDMS 해시로 오해하지 않는다.

중간보고에는“온난 조건, 모델SOC79.5–94.2%, 같은차량의 보정 미사용 시험2건이 사전 연구기준 통과”를 사용한다. 독립 차량/환경 검증, 전 구간 배터리 검증, 공식 인증 주행거리 재현 완료라고 쓰지 않는다. 이번 추가 방전 재현의 미달 결과도 함께 제시한다.
