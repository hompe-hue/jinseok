# Research topic presentation checkpoint 2026-11-12

Completed: exactly 3 editable Korean slides based on the current research proposal. Fields/topic; background/questions; methods/expected outcomes. All slides visually reviewed. No simulation results invented.

File: EREV_Research_Topic_3slides.pptx
Library: libfile_04c02b8568b4819198dcb25af8cd6322
SHA256: 7ac2e3ea98fcf400e5433d246c745a3b9772129a7efbd742f0a6756666f9b219
Next: ready for submission/presentation. Research simulation checkpoint unchanged.

## Reproducible source
```javascript
import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation} from '/home/agent/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';
const root=path.resolve('outputs/research_topic_slides_20261112');
const p=Presentation.create({slideSize:{width:1280,height:720}});
const font='Noto Sans CJK KR', navy='#102C48', blue='#006A89', gray='#425567';
function text(s,name,t,x,y,w,h,size=25,color=navy,bold=false){let a=s.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=t;a.text.style={typeface:font,fontSize:size,color,bold,insets:0,verticalAlignment:'top',autoFit:'none'};return a;}
function base(title,n){const s=p.slides.add();s.background.fill='#FFFFFF';text(s,'title',title,64,48,1148,72,44,navy,true);text(s,'page',String(n).padStart(2,'0'),1160,659,56,28,18,gray);return s;}
let s=base('연구 희망 분야와 주제',1);
text(s,'field-label','연구 희망 분야',66,157,1090,35,25,blue,true);
text(s,'field','전동화 차량 에너지 관리 및 시스템 시뮬레이션',66,205,1135,56,36,navy,true);
text(s,'topic-label','연구 주제',66,306,1090,34,25,blue,true);
text(s,'topic','주행 요구출력과 배터리 가용출력을 고려한\n가상 EREV의 발전 개입 전략 및 에너지 효율 분석',66,354,1138,132,40,navy,true);
text(s,'definition','EREV: 배터리와 엔진·발전기로 구동모터에 전력을 공급하는 주행거리 연장형 전기차',66,520,1140,66,23,gray);
text(s,'author','연세대학교 공학대학원 기계공학 전공   문진석\n지도교수  이종수 교수',66,612,1040,68,22,gray);
s.speakerNotes.text='희망 연구 분야는 전동화 차량의 에너지 관리와 1D 시스템 시뮬레이션입니다. 배터리 상태뿐 아니라 주행 요구출력과 공급 여유를 함께 고려해 발전원 기동 시점과 출력을 결정하는 연구를 수행하고자 합니다.\n출처: EREV_Research_Plan.docx, 2026-11-12 작성본, 1쪽. 연구 제목은 현재 제안 제목입니다.';
s=base('연구 배경과 핵심 질문',2);
text(s,'background-label','연구 배경',66,155,470,40,28,blue,true);
text(s,'background','SOC 기준 발전 제어는 단순하지만,\n급격한 부하 변화와 기동 지연을\n충분히 반영하지 못할 수 있음\n\n조기 기동은 전력 공급을 보완하지만\n추가 연료 소비를 유발할 수 있음',66,217,505,300,28,navy);
text(s,'question-label','핵심 연구 질문',660,155,530,40,28,blue,true);
text(s,'questions','어떤 주행 조건에서 발전 개입이 필요한가?\n\n예측 기동은 출력 부족을 얼마나 줄이는가?\n\n성능 확보에 필요한 연료 비용은 얼마인가?',660,217,548,300,27,navy);
text(s,'goal','연구 목표   요구출력 충족과 연료 소비를 함께 평가하여\n                 발전 개입 전략의 유효 조건과 적용 한계 도출',66,554,1135,92,29,blue,true);
s.speakerNotes.text='SOC는 배터리 충전상태를 의미합니다. 배터리 공급 여유가 충분하면 예측 기동의 이점이 작을 수 있으므로 효과가 없는 조건도 함께 비교합니다. 최고속도 부근에서는 일시적 속도 유지와 SOC를 유지하는 지속 운전을 구분하고, 제어로 개선 가능한 문제와 발전용량 한계를 분리합니다.\n출처: EREV_Research_Plan.docx 1~2쪽. 아직 전략 간 개선 효과를 확정한 단계가 아니며 슬라이드는 연구 질문을 제시합니다.';
s=base('연구 방법과 기대효과',3);
text(s,'method-label','연구 방법',66,147,690,40,28,blue,true);
text(s,'method1','01  공개자료 기반 차량 모델 검증',66,207,710,40,28,navy,true);
text(s,'method1detail','Bolt EV 실측 비교 및 순소비에너지 오차 분석',118,253,650,42,25,gray);
text(s,'method2','02  가상 직렬 EREV 발전계 구성',66,318,710,40,28,navy,true);
text(s,'method2detail','Volt 2세대 발전계 자료 참조, 순 DC 26 kW 조건\n공통 DC 버스 전력 수지와 연료·효율맵 검증',118,363,650,77,24,gray);
text(s,'method3','03  동일 조건에서 제어전략 비교',66,462,710,40,28,navy,true);
text(s,'method3detail','SOC 기준 제어와 현재·예측 요구출력 제어 비교\n주행 사이클 및 고속·경사 조건에서 평가',118,507,650,77,24,gray);
text(s,'effect-label','평가 및 기대효과',820,147,394,40,28,blue,true);
text(s,'evaluation','출력 부족 시간, 차속 추종오차\nSOC 변화, 연료 소비량 평가\n\n발전 기동의 판단 기준 도출\n성능과 연료 비용의 관계 규명\n발전용량·제어 설계 근거 확보',820,213,395,340,25,navy);
text(s,'scope','수행 도구: AVL CRUISE M     연구 범위: 공개자료 기반 가상 차량의 시뮬레이션 비교',66,624,1128,38,22,gray);
s.speakerNotes.text='기초 BEV 모델의 실측 비교와 공통 DC 버스 연결 시험을 진행했으며, 연료·효율맵 근거 도표를 확보했습니다. BEV 순소비에너지 편차와 저SOC 영역의 대표성은 추가 검토 대상입니다. 26 kW는 순 DC 출력의 연구조건이며 엔진 정격이나 실차 Volt 정격을 의미하지 않습니다. Bolt EV 차체 기반에 가상 직렬 발전계를 구성하며 실제 Volt 동력분기 구조를 재현하지 않습니다. 동일 초기조건에서 종료 SOC와 저장에너지 차이를 확인한 후 연료를 비교합니다. 실차 연비 개선이나 배터리 수명 연장은 검증 범위에 포함하지 않습니다.\n출처: EREV_Research_Plan.docx 2~3쪽. 발전계 참고문헌: Conlon et al. SAE 2015-01-1152; Jurkovic et al. SAE 2015-01-1208; Yadav (2018), Michigan Technological University. 상세 출처는 연구계획서 참조.';
await (await PresentationFile.exportPptx(p)).save(root+'/build/candidate.pptx');
await finalizePresentation({workspaceDir:root,candidatePath:root+'/build/candidate.pptx',finalPath:root+'/final/EREV_Research_Topic_3slides.pptx',pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:'/home/agent/.codex/skills/builtins/presentations/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:'/home/agent/.codex/skills/builtins/presentations/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:3,fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:root+'/build/validation.json'});
for(let i=0;i<p.slides.items.length;i++){const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(root+`/build/slide-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));}
console.log('Completed 3 slides');

```
