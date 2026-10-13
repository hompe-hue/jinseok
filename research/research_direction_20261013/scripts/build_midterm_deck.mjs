import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {GlobalFonts} from '@napi-rs/canvas';
import {finalizePresentation} from '/root/.codex/skills/builtins/presentations/container_tools/artifact_tool_utils.mjs';

const workspaceDir=process.env.BOLT_WORKSPACE||'/workspace/scratch/a5204a7b57f4';
const privateDir=path.join(workspaceDir,'private/research_direction_20261013');
const out=path.join(workspaceDir,'output/bolt_midterm_20261013');
const root=path.join(workspaceDir,'jinseok/research/research_direction_20261013');
const font='Noto Sans KR';
for(const f of ['NotoSansKR-Regular.ttf','NotoSansKR-Bold.ttf']) {
  GlobalFonts.registerFromPath(path.join(privateDir,'fonts',f),font);
}
const content=JSON.parse(await fs.readFile(path.join(root,'midterm_content.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const blue='#194D77',dark='#182B3C',muted='#536575';
function text(slide,name,value,x,y,w,h,size,bold=false,color=dark){
  const shape=slide.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});
  shape.text=value;shape.text.style={typeface:font,fontSize:size,bold,color,wrap:'square',autoFit:'none',insets:0,verticalAlignment:'top'};
  return shape;
}
for(const [idx,c] of content.entries()){
  const s=p.slides.add();s.background.fill='#FFFFFF';
  if(idx===0){
    text(s,'title',c.title,72,128,1100,180,58,true,blue);
    text(s,'subtitle',c.lead,76,354,1090,70,32);
    text(s,'author',c.paragraphs[0],76,517,1090,45,25,false,muted);
    text(s,'scope',c.paragraphs[1],76,569,1090,55,24,false,muted);
  }else{
    text(s,'title',c.title,72,46,1128,96,44,true,blue);
    text(s,'lead',c.lead,74,149,1120,74,28,true,dark);
    if(c.table){
      const cols=c.table[0].length;
      const widths=cols===4?[416,212,224,244]:idx===7?[140,470,486]:[370,330,396];
      const top=244;
      const height=c.table.length>5?354:310;
      const t=s.tables.add({rows:c.table.length,columns:cols,left:76,top,width:1096,height,columnWidths:widths,values:c.table});
      t.borders.assign({style:'solid',fill:'#D4DDE4',width:1});
      for(let r=0;r<c.table.length;r++){
        t.rows[r].height=height/c.table.length;
        for(let col=0;col<cols;col++){
          const cell=t.getCell(r,col);
          cell.fill=r===0?'#E7EEF4':'#FFFFFF';
          cell.text.style={typeface:font,fontSize:25,bold:r===0,color:r===0?blue:dark,alignment:'left',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:8};
        }
      }
    }else{
      const spacing=c.paragraphs.length===4?88:112;
      c.paragraphs.forEach((v,i)=>text(s,'paragraph-'+i,v,76,252+i*spacing,1095,82,29,false,dark));
    }
    if(c.foot)text(s,'caveat',c.foot,76,636,1120,39,22,false,muted);
  }
  text(s,'page-number',String(idx+1).padStart(2,'0'),1177,672,54,25,20,false,muted);
  s.speakerNotes.text=c.notes;
}
await fs.mkdir(path.join(privateDir,'deck_render'),{recursive:true});
await fs.mkdir(out,{recursive:true});
const candidatePath=path.join(privateDir,'build/candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(out,'Bolt_EREV_Midterm_Draft_20261013_v4.pptx');
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath,
  pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,
  integrityValidatorPath:'/root/.codex/skills/builtins/presentations/container_tools/inspect_presentation_package_integrity.py',
  layoutValidatorPath:'/root/.codex/skills/builtins/presentations/container_tools/inspect_presentation_layout_geometry.py',
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry',...[4,6,8,11].flatMap(n=>['--require-native-table-slide',String(n)])],
  requiredNativeTableOwnerSlides:[4,6,8,11],
  fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
  receiptPath:path.join(privateDir,'build/final_v4.validation.json')});
console.log(JSON.stringify({finalPath,result}));
// Render the finalized PPTX with the supplied LibreOffice runtime for visual QA.
// Artifact Tool's PDF exporter is unavailable in this runtime (font alias).
for(const [idx,s] of p.slides.items.entries()){
  const png=await p.export({slide:s,format:'png',scale:1});
  await fs.writeFile(path.join(privateDir,'deck_render',`slide-${String(idx+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log(JSON.stringify({slides:content.length,render_pending:true}));
