#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,threading,time
from pathlib import Path

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

class Fabric:
    def __init__(self,world_id,node_id,path,max_steps=2000):
        self.world_id=world_id
        self.node_id=node_id
        self.path=Path(path)
        self.max_steps=max(1,int(max_steps))
        self.lock=threading.RLock()
        self.jobs={}
        self._load()

    def _load(self):
        try:
            x=json.loads(self.path.read_text(encoding="utf-8"))
            if x.get("world_id")==self.world_id and isinstance(x.get("jobs"),dict):
                self.jobs=x["jobs"]
        except (FileNotFoundError,json.JSONDecodeError,TypeError):
            pass

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.path.with_suffix(self.path.suffix+".tmp")
        tmp.write_text(canonical({"protocol":"UTM-Resident-Compute-State/1.0","world_id":self.world_id,"jobs":self.jobs})+"\n",encoding="utf-8")
        os.replace(tmp,self.path)

    def _rules(self,program):
        if not isinstance(program,str) or len(program)>12000:
            raise ValueError("program must be a string <= 12000 chars")
        rules={}
        for raw in program.split(";"):
            raw=raw.strip()
            if not raw:
                continue
            a=raw.split(",")
            if len(a)!=5:
                raise ValueError("each transition must be q,read,next,write,L|R")
            q,read,nq,write,d=a
            if d not in ("L","R"):
                raise ValueError("direction must be L or R")
            rules[(q,read)]=(nq,write,d)
        return rules

    def _render(self,tape,blank):
        keys=list(tape) or [0]
        lo,hi=min(keys),max(keys)
        if hi-lo>8192:
            hi=lo+8192
        return "".join(tape.get(i,blank) for i in range(lo,hi+1))

    def _step(self,job,steps):
        steps=max(0,min(int(steps),self.max_steps))
        if job.get("halted"):
            return 0
        rules=self._rules(job["program"])
        tape={int(k):v for k,v in job.get("tape",{}).items()}
        q=str(job["q"]); h=int(job["h"]); done=0; blank=job["blank"]
        while done<steps:
            r=rules.get((q,tape.get(h,blank)))
            if r is None:
                job["halted"]=True
                break
            nq,write,d=r
            if write==blank:
                tape.pop(h,None)
            else:
                tape[h]=write
            q=nq; h+=1 if d=="R" else -1; done+=1
        job["q"]=q
        job["h"]=h
        job["tape"]={str(k):v for k,v in sorted(tape.items())}
        job["total_steps"]=int(job.get("total_steps",0))+done
        job["version"]=int(job.get("version",0))+1
        job["updated_at"]=time.time()
        return done

    def _public(self,job):
        x=dict(job)
        tape={int(k):v for k,v in x.get("tape",{}).items()}
        x["tape_text"]=self._render(tape,x["blank"])
        x["bounded"]=True
        x["max_steps_per_continue"]=self.max_steps
        return x

    def create(self,resident_id,task):
        if not isinstance(task,dict) or task.get("kind","utm")!="utm":
            raise ValueError("only kind=utm is enabled")
        inp=task.get("input","")
        if not isinstance(inp,str) or len(inp)>4096:
            raise ValueError("input must be a string <= 4096 chars")
        program=task.get("program","")
        self._rules(program)
        blank=str(task.get("blank","_"))
        if len(blank)!=1:
            raise ValueError("blank must be one character")
        created=time.time()
        seed=canonical([self.world_id,self.node_id,resident_id,program,inp,created,os.urandom(8).hex()])
        jid="job-"+hashlib.sha256(seed.encode()).hexdigest()[:20]
        tape={str(i):c for i,c in enumerate(inp) if c!=blank}
        job={"job_id":jid,"world_id":self.world_id,"kind":"utm","resident_id":resident_id,
             "program":program,"blank":blank,"q":str(task.get("start","0")),"h":0,"tape":tape,
             "halted":False,"total_steps":0,"epoch":0,"version":0,"owner_node":self.node_id,
             "created_at":created,"updated_at":created}
        with self.lock:
            self.jobs[jid]=job
            self._step(job,task.get("steps",0))
            self._save()
            return self._public(job)

    def get(self,jid):
        with self.lock:
            j=self.jobs.get(jid)
            return self._public(j) if j else None

    def list_for(self,resident_id):
        with self.lock:
            return [self._public(j) for j in self.jobs.values() if j.get("resident_id")==resident_id]

    def continue_job(self,jid,steps):
        with self.lock:
            j=self.jobs.get(jid)
            if not j:
                return None,"not_found"
            if j.get("owner_node")!=self.node_id:
                return self._public(j),"remote_owner"
            self._step(j,steps)
            self._save()
            return self._public(j),None

    def takeover(self,jid):
        with self.lock:
            j=self.jobs.get(jid)
            if not j:
                return None
            if j.get("owner_node")!=self.node_id:
                j["owner_node"]=self.node_id
                j["epoch"]=int(j.get("epoch",0))+1
                j["version"]=int(j.get("version",0))+1
                j["updated_at"]=time.time()
                self._save()
            return self._public(j)

    def export_jobs(self):
        with self.lock:
            return [dict(j) for j in self.jobs.values()]

    @staticmethod
    def _rank(j):
        return (int(j.get("epoch",0)),int(j.get("version",0)),float(j.get("updated_at",0)),str(j.get("owner_node","")))

    def merge_jobs(self,jobs):
        changed=0
        with self.lock:
            for incoming in jobs if isinstance(jobs,list) else []:
                if not isinstance(incoming,dict) or incoming.get("world_id")!=self.world_id:
                    continue
                jid=str(incoming.get("job_id",""))
                if not jid or incoming.get("kind")!="utm":
                    continue
                try:
                    self._rules(incoming.get("program",""))
                except ValueError:
                    continue
                cur=self.jobs.get(jid)
                if cur is None or self._rank(incoming)>self._rank(cur):
                    self.jobs[jid]=dict(incoming); changed+=1
            if changed:
                self._save()
        return changed
