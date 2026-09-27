#!/usr/bin/env python3
import hashlib,json,os,tempfile
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
    os.environ['SNAPSHOT_DIR']=d
    spec=spec_from_file_location('search_api',ROOT/'search_api.py')
    m=module_from_spec(spec);spec.loader.exec_module(m)
    c=m.canon('json',{'b':2,'a':1})
    assert c=='j:{"a":1,"b":2}'
    g=m.enc(c)
    assert m.dec(g)==c
    assert m.obj(g)['value']=={'a':1,'b':2}
    a=m.write_snapshot(g,'test-v1',{'status':404})
    b=m.write_snapshot(g,'test-v1',{'status':200})
    assert a['GSNAPSHOT']==b['GSNAPSHOT']
    assert a['result']==b['result']=={'status':404}
    r=m.read_snapshot(a['GSNAPSHOT'])
    v=dict(r);digest=v.pop('sha256')
    raw=json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    assert hashlib.sha256(raw).hexdigest()==digest
print('PASS address snapshot unit test')
