# C1 실행 안내

**지금 실행할 파일은 060과 061 두 개입니다.** 066은 두 확인 결과를 평가한 뒤 실행합니다.

1. ZIP을 원하는 폴더에 압축 해제합니다.
2. CRUISE M에서 `projects/C1_CAL_61905060.proj`를 열고 기존 방식으로 주행 계산을 실행합니다.
3. battery·velocity·generator 결과를 CSV로 내보냅니다. 가능하면 `battery_C1_61905060.csv`, `velocity_C1_61905060.csv`, `generator_C1_61905060.csv`로 저장합니다.
4. `projects/C1_CAL_61905061.proj`에도 같은 작업을 합니다. 파일명은 뒤 시험번호만 61905061로 바꿉니다.
5. 새 CSV 총 6개를 올립니다. 기존 파일명 `battery_ANL61905060.csv` 등도 비교 코드에서 허용하지만 새 실행 파일임을 구분해 주세요.

프로젝트에 입력이 내장되어 있습니다. `inputs/`의 DAT와 손실 CSV는 적용 내용을 확인하거나 복구할 때 쓰는 사본이며, 실행을 위해 다시 import할 필요는 없습니다. 기존 프로젝트를 덮어쓰지 마세요.

입력 종료시간은 060 약3150.897초, 061 약1489.899초입니다. 1초 간격 CSV가 3150/1489초에서 끝나는 경우 내보내지 않은 마지막 소수초를 따로 기록합니다. 계산 종료 오류가 나면 그 오류도 함께 보내 주세요.

두 확인이 통과한 뒤 `projects/C1_HOLD_61905066.proj`를 실행합니다. 약7630.893초를 연속 실행하며 7개 구간별로 초기 SOC를 다시 넣지 않습니다.

## 실제 CSV 자동 비교

Python에 numpy·pandas가 설치된 환경에서 ZIP 폴더의 다음 명령을 사용합니다. ChatGPT에 CSV를 보내면 같은 코드로 분석합니다.

```bash
python scripts/verify_C1_exports.py --test 61905060 --exports CSV_FOLDER
python scripts/verify_C1_exports.py --test 61905061 --exports CSV_FOLDER
```

두 결과가 기준을 만족해야 `frozen_for066.json`이 만들어집니다. 그 뒤:

```bash
python scripts/verify_C1_exports.py --test 61905066 --exports CSV_FOLDER
```

066을 보기 전에 고정한 C1 수치를 유지합니다. 자세한 근거·한계·사전 계산 결과는 `DECISION_KO.md`에 있습니다. ZIP에 실제 C1 시뮬레이션 결과 CSV가 포함된 것은 아닙니다.
