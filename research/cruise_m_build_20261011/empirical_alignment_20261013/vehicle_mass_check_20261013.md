# Vehicle 질량 입력 확인 — 2026-10-13

사용자 제공 image(20261012-155425).png에서 확인했다.

| 항목 | 화면 값 |
|---|---:|
| Curb weight | 1625 kg |
| Additional load | 132.6704 kg |
| Gross weight 표시 | 1757.6704 kg |
| Number of passengers | 0 |
| Weight per passenger | 0 kg |
| Load state | Empty |

1625 + 132.6704 = 1757.6704 kg로 기존 목표 시험질량 입력과 일치한다. 이는 GUI 입력 및 합계 확인이며 동역학 유효 질량 또는 ANL 개별시험의 실제 질량을 독립 확인했다는 뜻은 아니다. Gross weight 표시만으로 관성 모델 전체의 검증 완료라고 기록하지 않는다.

Driving resistance selection은 Function without reference vehicle로 표시된다. 실제 Total Driving Resistance 수식과 속도 단위/변환은 이번 화면에 보이지 않으므로 미확인이다.

다음 시작점: 왼쪽 Vehicle 아래 Total Driving Resistance를 선택하여 수식, 속도 입력 단위 및 계수를 확인한다. 기존 km/h 기준 참조는 A=126.329494 N, B=0.557775 N h/km, C=0.033456276 N h²/km²이며, 실제 함수 속도 단위를 보기 전 계수를 다시 넣지 않는다.

기타 관찰: Wheelbase 2777 mm, CG 거리 1100 mm/높이500 mm, Frontal area1.97 m²는 기존 템플릿 값으로 남아 있다. 이번 질량 입력 확인 단계에서 임의로 수정하지 않았다. 해당 값의 출처/적용 검토는 기존 미확인 설정 목록에 유지한다.

직전 완료: generator.csv의 FTP75 0–2477 s / 2478점 발전 정지 수치 검증은 e27fc0c 커밋에 저장 완료. 반복하지 않는다.

