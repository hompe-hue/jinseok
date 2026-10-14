"""Read saved ACT XML without executing it; compare properties by type/occurrence.

Serializer IDs are not persistent across saves. Never compare arrays by old IDs.
Occurrence comparison is a screening aid; changed-count groups are not paired.
"""
import base64, hashlib, json, sys, zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/dis80_project_closure_20261014'
OUT.mkdir(parents=True,exist_ok=True)

class SavedProject:
    def __init__(self,path):
        self.path=Path(path)
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            self.root=E.fromstring(z.read('project.xml'),E.XMLParser(resolve_entities=False,no_network=True))
        self.index={n.get('id'):n for n in self.root.iter() if n.get('id') and n.tag!='ref'}
        self.memo={}
    def resolve(self,n):
        return self.index[n.get('id')] if n.tag=='ref' else n
    def fields(self,n):
        n=self.resolve(n)
        if n.tag=='object':n=n.find('dict')
        a=list(n)
        return {self.decode(k):v for k,v in zip(a[::2],a[1::2]) if k.tag=='str'}
    def decode(self,n,seen=frozenset()):
        n=self.resolve(n); oid=n.get('id')
        if oid in seen:return {'cycle_type':n.get('type') or n.tag}
        if oid in self.memo:return self.memo[oid]
        ns=seen|{oid} if oid else seen
        if n.tag=='object' and not (n.get('type') or '').startswith(('cruise.props.','common.props.','act.units.','act.tbl.')):
            return {'opaque_type':n.get('type'),'scope':'Excluded non-property/UI graph; not compared'}
        if len(seen)>30:return {'depth_limit_type':n.get('type') or n.tag}
        if n.tag=='str':v=base64.b64decode(n.text or '').decode(errors='replace') if n.get('coding')=='base64' else n.text or ''
        elif n.tag=='num':v=json.loads(n.text)
        elif n.tag=='none':v=None
        elif n.tag in ('true','false'):v=n.tag=='true'
        elif n.tag=='numpy_array':
            b=base64.b64decode(n.text or '');a=np.frombuffer(b,dtype=n.get('dtype'))
            v={'array_dtype':n.get('dtype'),'shape':n.get('dim'),'sha256':hashlib.sha256(b).hexdigest(),'count':len(a)}
            if len(a)<=30:v['values']=a.tolist()
            elif len(a):v.update(first=float(a[0]),last=float(a[-1]),minimum=float(a.min()),maximum=float(a.max()))
        elif n.tag=='dict' or (n.tag=='object' and n.find('dict') is not None):
            v={k:self.decode(x,ns) for k,x in self.fields(n).items()}
            if n.tag=='object':v={'type':n.get('type'),'fields':v}
        else:v={'tag':n.tag,'type':n.get('type'),'items':[self.decode(x,ns) for x in n]}
        if oid:self.memo[oid]=v
        return v
    def properties(self):
        d=defaultdict(list)
        for n in self.root.iter('object'):
            if (n.get('type') or '').startswith('cruise.props.'):
                d[n.get('type')].append({'serializer_id':n.get('id'),'semantic':self.decode(n)})
        return dict(d)
    def nodes(self,type_name):
        return [n for n in self.root.iter('object') if n.get('type')==type_name]
    def amount(self,n,key):
        return self.decode(self.fields(n)[key])['fields']['value']
    def arrays_under(self,n):
        # Follow references as well as physical children; retain column order.
        found=[];seen=set()
        def walk(x):
            x=self.resolve(x);oid=x.get('id')
            if oid and oid in seen:return
            if oid:seen.add(oid)
            if x.tag=='object' and x.get('type') in ('act.tbl.NumArray','act.tbl.IntArray'):
                f=self.fields(x);a=self.resolve(f['data'])
                arr=np.frombuffer(base64.b64decode(a.text or ''),dtype=a.get('dtype')).copy()
                found.append((x.get('id'),self.decode(f['unit']) if 'unit' in f else None,arr));return
            for c in x:walk(c)
        walk(n);return found

def main():
    old,new=map(SavedProject,sys.argv[1:3]); op,np_=old.properties(),new.properties()
    changed=[];counts=[];same=0
    for t in sorted(op.keys()|np_.keys()):
        aa,bb=op.get(t,[]),np_.get(t,[])
        if len(aa)!=len(bb):counts.append({'type':t,'old_count':len(aa),'new_count':len(bb)});continue
        for k,(a,b) in enumerate(zip(aa,bb)):
            if a['semantic']!=b['semantic']:changed.append({'type':t,'occurrence':k,'old':a,'new':b})
            else:same+=1
    report={'old_sha256':hashlib.sha256(old.path.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(new.path.read_bytes()).hexdigest(),
            'CRC_passed':True,'unchanged_property_occurrences':same,'changed_property_occurrences':len(changed),
            'count_changed_groups':counts,'changes':changed,
            'scope':'Read-only property screening by type and occurrence; non-property/UI objects excluded. Not runtime identity or physical calibration; serializer IDs are not stable.'}
    (OUT/'semantic_diff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='changes'},ensure_ascii=False))
    for c in changed:print(c['type'],c['occurrence'])

if __name__=='__main__':main()
