# 보조전력 분석 재현

`EREV_Aux_Source_Data_20261118.zip`에는 프로젝트 저장소 구조를 유지한 ANL 기준 CSV·CAN 요약, 기존 검증 상태와 BMS·Vehicle CSV가 있다. 두 ZIP을 같은 폴더에 풀고 [직전 30초 프로젝트](https://chatgpt.com/library?file_id=libfile_6d97762e9ffc8191a29102e02783d857&account_id=personal)를 따로 푼다. Python 표준 라이브러리만 필요하다.

```sh
python research/erev_aux_thesis_audit_20261118/reproduce.py \
  --repo . --project BEV_066_DriveSignalGate_30s.proj \
  --bms "runtime/BMS powerlogging.csv" \
  --vehicle "runtime/Vehicle powerlogging.csv" --output reproduced
```

재현 출력은 두 CSV와 AUX_QA.json이다. 30초 PROJ는 오프라인으로 읽고, 기존 정상 실행의 기록을 계산한다.
