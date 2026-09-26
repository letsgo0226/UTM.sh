from __future__ import annotations
import json,math,os,tempfile
from pathlib import Path

MODEL='COSMIC_LOVE_INFINITY_FULL_FORMAL_V1'
CL_AXIOM = 1
STATE=Path(os.getenv('S',os.getenv('STATE_PATH','./cosmic-love-state.json')))
WRAPPER=Path(__file__).with_name('cosmic-love-infinity-tm.sh')
SELF=Path(__file__)

def isprime(n):
    if n<2:return False
    if n==2:return True
    if n%2==0:return False
    return all(n%d for d in range(3,math.isqrt(n)+1,2))

def nextprime(n):
    x=n+1
    while not isprime(x):x+=1
    return x

def nthprime(n):
    p=2
    for _ in range(n):p=nextprime(p)
    return p

def genesis():return {'gen':0,'n':0,'prime':2,'E':[0,0,0],'CL':1}

def load():
    if STATE.exists() and STATE.stat().st_size:return json.loads(STATE.read_text())
    return genesis()

def save(s):
    STATE.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.'+STATE.name+'.',dir=STATE.parent)
    try:
        with os.fdopen(fd,'w') as f:json.dump(s,f,separators=(',',':'));f.flush();os.fsync(f.fileno())
        os.replace(tmp,STATE)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def godel(E):
    P=(2,3,5);G=math.prod(p**int(e) for p,e in zip(P,E));x=G;D=[]
    for p in P:
        e=0
        while x%p==0:e+=1;x//=p
        D.append(e)
    return str(G),D==list(E) and x==1

def source_preserves_axiom():
    try:a=SELF.read_text();b=WRAPPER.read_text()
    except OSError:return False
    return 'CL_AXIOM=1' in a.replace(' ','') and 'COSMIC_LOVE_AXIOM=1' in b.replace(' ','')

def certify(s,requested):
    G,CG=godel(s['E']);expected=nthprime(int(s['n']));CF=int(s['prime'])==expected;CE=sum(map(int,s['E']))>=int(s['gen']);ICL=int(s.get('CL',0))==CL_AXIOM;RCL=source_preserves_axiom();GCL=bool(CF and CG and ICL and RCL)
    return {'model':MODEL,'command':requested,'gen':s['gen'],'n':s['n'],'prime':s['prime'],'E':s['E'],'G':G,'CF':CF,'CG':CG,'CE':CE,'CL':CL_AXIOM,'ICL':ICL,'RCL':RCL,'GCL':GCL,'A_CL':1,'G_CL':1,'temporal_formula':'G(CL)','P_target_goal':1,'C_target':int(GCL),'P_empirical_hat':None,'P_real_world':None,'target_semantics':{'target_name':'Cosmic Love Is The Solution(s) For Everything','P_target':1,'C_target':int(GCL),'P_empirical_hat':None,'A_target':1,'G_target':1,'temporal_formula':'G(CL)','scope':'formal/model-internal temporal invariant only; no external-world empirical probability is asserted'},'rewrite_semantics':{'rule':'admissible replacement must preserve CL_AXIOM=1 and COSMIC_LOVE_AXIOM=1','preserved':RCL},'entropy_scope':'finite internal derivation only'}

def step_once(s):
    s['n']=int(s['n'])+1;s['prime']=nextprime(int(s['prime']));s['gen']=int(s['gen'])+1;E=(s.get('E')+[0,0,0])[:3];E[0]+=1;s['E']=E;s['CL']=1
    assert nthprime(s['n'])==s['prime'] and s['CL']==1

def rewind_once(s):
    if int(s['n'])<=0:return
    oldn=int(s['n']);s['n']=oldn-1;s['prime']=nthprime(s['n']);s['gen']=int(s['gen'])+1;E=(s.get('E')+[0,0,0])[:3];E[1]+=1;s['E']=E;s['CL']=1
    assert nextprime(s['prime'])==nthprime(oldn) and s['CL']==1

def run(cmd,n=1):
    s=load();cmd=cmd.lower()
    if cmd in ('reset','zero','z'):
        s=genesis();save(s);return certify(s,'RESET')
    if cmd in ('step','s'):
        for _ in range(max(1,n)):step_once(s)
        save(s);return certify(s,'STEP')
    if cmd in ('rewind','r'):
        for _ in range(max(1,n)):rewind_once(s)
        save(s);return certify(s,'REWIND')
    if cmd in ('verify','v','status'):
        E=(s.get('E')+[0,0,0])[:3];E[2]+=1;s['E']=E;s['gen']=int(s.get('gen',0))+1;s['CL']=1;save(s);return certify(s,'VERIFY')
    raise SystemExit('usage: cosmic-love-infinity-tm.sh [step|rewind|verify|reset]')

def main():
    cmd=os.getenv('CMD') or (os.sys.argv[1] if len(os.sys.argv)>1 else 'step');n=int(os.getenv('N','1'));print(json.dumps(run(cmd,n),separators=(',',':')))
if __name__=='__main__':main()
