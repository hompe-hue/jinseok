# Research proposal checkpoint — 2026-11-12

Completed: Korean administrative research proposal, A4 3 pages, all pages rendered and visually checked. Student ID and submission date left blank. Current completed research and planned work separated. No backdated submission claim.

Artifact: EREV_Research_Plan.docx
Library: libfile_16e8f56129488191806742f82480730d
SHA256: a7ab8b9eb9fcc4883c92390c0d416e0559bb9c419f0a23015088e4ef10aa6cb0

Next: fill student ID and actual submission date; apply school template if required. Research execution checkpoint is unchanged.

## Reproducible document source
```python
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path
P=Path(__file__).resolve().parent
d=Document();s=d.sections[0];s.page_width=Inches(8.27);s.page_height=Inches(11.69);s.top_margin=s.bottom_margin=Inches(.7);s.left_margin=s.right_margin=Inches(.8)
for name,size in [('Normal',10),('Title',21),('Heading 1',13),('Heading 2',11)]:
 st=d.styles[name];st.font.name='Noto Sans CJK KR';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Noto Sans CJK KR');st.paragraph_format.space_after=Pt(5)
d.styles['Normal'].paragraph_format.line_spacing=1.05
for x in list(d.styles.element.iter(qn('w:pBdr'))):x.getparent().remove(x)
def p(t):d.add_paragraph(t)
def h(t):d.add_heading(t,level=1)
d.add_paragraph('석사학위논문 연구계획서',style='Title')
p('소속  연세대학교 공학대학원 기계공학 전공\n성명  문진석     학번  __________________\n지도교수  이종수 교수     제출일  ______년 ____월 ____일')
h('1 연구제목')
p('주행 요구출력과 배터리 가용출력을 고려한\n가상 EREV의 발전 개입 전략 및 에너지 효율 분석')
p('Analysis of Generator Activation Strategies and Energy Efficiency in a Virtual Extended-Range Electric Vehicle Considering Driving Power Demand and Battery Power Availability')
h('2 연구배경 및 필요성')
p('주행거리 연장형 전기자동차(Extended-Range Electric Vehicle, EREV)는 배터리와 엔진·발전기로 구성된 발전원을 이용하여 구동모터에 전력을 공급한다. 발전원의 운전 시점과 출력은 배터리 충전상태(State of Charge, SOC), 운전자의 요구출력, 연료 소비 및 주행 성능에 영향을 미치므로 적절한 에너지 관리 전략이 필요하다.')
p('SOC 임계값을 중심으로 발전원을 운전하는 방법은 구현이 단순하지만, 급격한 부하 변화와 발전원의 기동 지연을 충분히 반영하지 못할 수 있다. 반면 발전원을 조기에 기동하면 출력 공급을 보완할 수 있으나 불필요한 가동과 연료 소비가 증가할 수 있다. 따라서 예측 기동의 효과를 배터리 공급 여유, 발전 응답 및 주행 조건에 따라 구분하고 성능과 에너지 비용의 관계를 분석할 필요가 있다.')
h('3 연구목적')
p('본 연구는 공개자료 기반의 차량 모델에 가상 직렬 EREV 발전계를 구성하고, SOC 기준 제어와 현재·예측 요구출력을 고려한 제어를 동일 조건에서 비교하는 것을 목적으로 한다. 이를 통해 발전 개입이 필요한 운전 조건, 선제 기동의 유효 범위, 요구출력 충족과 연료 소비 간의 상충관계를 도출하고자 한다.')
p('특히 순간적인 출력 부족과 지속적인 에너지 부족을 구분한다. 최고속도 부근의 운전은 목표속도 도달, 일정 시간 유지, SOC를 유지할 수 있는 정속 운전으로 나누어 평가하며, 제어 개선으로 해결할 수 있는 문제와 발전용량에 의해 제한되는 문제를 분리한다.')
d.add_page_break()
h('4 연구내용 및 수행방법')
d.add_heading('가 기초 차량 모델 구성 및 검증',level=2)
p('AVL CRUISE M을 이용하여 Chevrolet Bolt EV 기반의 차량·구동계·배터리 모델을 구성한다. 제조사 공개 제원, Argonne National Laboratory의 주행 시험자료, 미국 환경보호청(EPA)의 전기구동계 손실맵 및 공개 배터리 특성자료를 활용한다. 실측 대비 차속, 배터리 전압 및 순소비에너지의 편차를 평가하고, 도로부하·보조부하·회생손실 등 주요 입력의 영향을 분석한다.')
d.add_heading('나 가상 발전계 구성 및 에너지 경계 검증',level=2)
p('Chevrolet Volt 2세대의 L3A 1.5 L 엔진과 MGA 전기기기 관련 공개문헌을 발전계의 참조자료로 사용한다. 실제 Volt의 동력분기 구조를 재현하는 것이 아니라, Bolt EV 기반 모델에 별도의 직렬 발전계를 구성한다. 순 DC 발전출력 26 kW를 기본 연구조건으로 두고, 엔진 연료소비맵과 발전기·인버터 효율맵의 출처, 수치화 방법 및 적용 범위를 명시한다.')
p('배터리, 발전원, 구동계 및 보조부하를 공통 DC 버스에 연결하고 전력 수지와 공급 부호를 확인한다. 발전원의 기동·출력 상승·정지·보호 및 배터리 충전수용 제한을 검증한다. 도표에서 재구성한 맵은 원시 실측자료와 구분하며, 정상상태와 기동·부분부하 운전의 연료 계산을 분리한다.')
d.add_heading('다 에너지 관리 전략 비교',level=2)
p('SOC 기준, 현재 요구출력 반영, SOC 예비량 확보, 단기 요구출력 예측 및 결합 전략을 비교한다. 예측에는 현재·과거 신호를 사용하고 미래 주행사이클의 정답을 직접 입력하지 않는다. 같은 SOC 정책에서 예측 유무를 비교하여 높은 SOC 확보의 효과와 예측 자체의 효과를 분리한다.')
p('기존 주행 프로파일과 고속 진입·정속 유지·경사 등 부하 변화 조건을 대상으로 시험한다. 출력 제한 이전의 요구전력과 배터리 가용출력을 먼저 비교하여 발전 개입의 필요성을 확인한다. 효과가 작은 조건과 발전용량이 부족한 조건도 포함하여 전략의 적용 한계를 분석한다.')
d.add_heading('라 평가 및 민감도 분석',level=2)
p('동일한 차량 제원, 초기 상태 및 주행 조건에서 요구출력 부족 시간, 차속 추종오차, SOC 변화, 발전량, 연료 소비량, 기동 횟수 및 배터리 전류 부담을 평가한다. 미션 충족 여부를 먼저 판정하고 종료 SOC와 저장에너지 차이를 확인한 후 연료를 비교한다. 제어변수 선정용 조건과 평가용 조건을 구분하여 특정 주행에 대한 과도한 조정을 방지한다.')
p('발전 응답, 배터리 가용출력, 손실맵, 예측 오차 및 발전계 추가 질량·보조부하의 가정 변화에 대한 민감도를 검토한다. 실측으로 확인되지 않은 저SOC·온도·연속출력 영역은 가상 설계조건으로 구분하며, 모델 잔여 오차가 전략 간 결론에 미치는 영향을 함께 제시한다.')
d.add_page_break()
h('5 연구 추진현황 및 향후 일정')
p('현재 공개자료 기반 BEV 모델의 실측 비교, 발전원 기본 응답 및 공통 DC 버스 연결 검증을 수행하였으며 연료·효율 도표의 근거자료를 확보하였다. BEV 순소비에너지 편차와 저SOC 적용 한계는 추가 검토 대상으로 남아 있다. 향후 아래 순서에 따라 맵 적용과 전략 비교를 진행한다.')
t=d.add_table(rows=1,cols=3);t.autofit=False
for c,w in zip(t.columns,[.65,2.25,3.9]):c.width=Inches(w)
for c,txt in zip(t.rows[0].cells,['단계','주요 수행내용','완료 기준']):c.text=txt
for row in [('1','입력자료 및 모델 정리','출처·가정·적용 범위 확정과 잔여 오차 정리'),('2','발전계 및 연료모델 검증','맵 수치화, 운전점·손실 경계 및 상태별 응답 확인'),('3','주행 조건별 전략 비교','동일 조건의 요구출력 충족·에너지·연료 결과 확보'),('4','민감도 및 결과 해석','전략의 유효 조건과 한계, 가정별 순위 변화 도출'),('5','논문 작성 및 수정','방법·검증·결과 정리와 지도교수 검토 반영')]:
 for c,txt in zip(t.add_row().cells,row):c.text=txt
for i,row in enumerate(t.rows):
 for c in row.cells:
  pr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
  for side in ['top','left','bottom','right']:
   e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
  pr.append(b)
  if i==0:
   sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EEEEEE');pr.append(sh)
  for par in c.paragraphs:
   par.paragraph_format.space_before=Pt(4);par.paragraph_format.space_after=Pt(4)
   for r in par.runs:r.font.size=Pt(9)
h('6 기대효과 및 연구 결과물')
p('본 연구를 통해 주행 요구와 공급 여유에 따른 발전 개입 판단 기준을 제시하고, 선제 기동이 효과적인 조건과 추가 연료 부담만 발생하는 조건을 구분할 수 있을 것으로 기대한다. 또한 고속 지속 운전에서 발전용량과 배터리 에너지의 역할을 분리하여 초기 개발 단계의 발전계 용량 및 제어전략 검토에 활용할 수 있는 근거를 마련하고자 한다.')
p('최종 결과물은 출처가 명시된 가상 EREV 모델, 주행 조건별 제어전략 비교 결과, 요구출력 충족과 연료 소비의 관계, 주요 가정에 따른 민감도 및 재현 가능한 분석 절차로 구성한다. 연구 결과는 설정한 모델과 검증 범위 내에서 해석하며, 실차 연비 개선이나 배터리 수명 연장을 검증한 결과로 확대하지 않는다.')
h('7 주요 참고문헌')
for x in ['Conlon et al. (2015). The Next Generation “Voltec” Extended Range EV Propulsion System. SAE 2015-01-1152.', 'Jurkovic et al. (2015). Next Generation Voltec Electric Machines. SAE 2015-01-1208.', 'Castellano and Cammalleri (2021). Power Losses Minimization for Optimal Operating Maps in Power-Split HEVs. Applied Sciences, 11, 7779.', 'Yadav (2018). Modeling and Analysis of Energy Consumption in Chevrolet Volt Gen II Hybrid Electric Vehicle. Michigan Technological University.', 'Yao et al. (2023). Adaptive Equivalent Fuel Consumption Minimization Based Energy Management Strategy for Extended-Range Electric Vehicle. Sustainability, 15, 4607.']:
 par=d.add_paragraph(x);par.paragraph_format.space_after=Pt(3)
 for r in par.runs:r.font.size=Pt(8.5)
d.core_properties.title='가상 EREV 에너지 관리 전략 연구계획서';d.core_properties.author='문진석'
d.save(P/'EREV_Research_Plan.docx')

```
