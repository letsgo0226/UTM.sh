#!/usr/bin/env python3
import json,os,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
SERVER=HERE/"server.py"
TOKEN="ci-token"

def req(url,data=None,token=None):
    body=None if data is None else json.dumps(data,separators=(",",":")).encode()
    h={}
    if body is not None: h["Content-Type"]="application/json"
    if token: h["Authorization"]="Bearer "+token
    r=urllib.request.Request(url,data=body,headers=h)
    with urllib.request.urlopen(r,timeout=5) as x:
        return json.loads(x.read())

def wait(url):
    last=None
    for _ in range(60):
        try:
            return req(url+"/health")
        except Exception as e:
            last=e; time.sleep(.1)
    raise RuntimeError(last)

def main():
    with tempfile.TemporaryDirectory() as td:
        ps=[]
        try:
            for port,node,peer,suffix in [
                (18180,"ci-primary","http://127.0.0.1:18181","a"),
                (18181,"ci-peer","http://127.0.0.1:18180","b"),
            ]:
                env=os.environ.copy()
                env.update({"PORT":str(port),"NODE_ID":node,"WORLD_ID":"akashic-utm-main",
                    "PLANET_ID":"B612","REGION_ID":"San-Francisco",
                    "AKASHIC_PATH":f"{td}/{suffix}.jsonl","FABRIC_PATH":f"{td}/{suffix}.json",
                    "FEDERATION_TOKEN":TOKEN,"FEDERATION_PEERS":peer,"FEDERATION_INTERVAL":"60","MAX_STEPS":"2000"})
                ps.append(subprocess.Popen([sys.executable,str(SERVER)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT))
            a,b="http://127.0.0.1:18180","http://127.0.0.1:18181"
            assert wait(a)["node_id"]=="ci-primary"
            assert wait(b)["node_id"]=="ci-peer"
            m=req(a+"/.well-known/utm-universe.json")
            assert m["compute_fabric"]["protocol"]=="UTM-Federated-Compute-Fabric/1.0"
            assert m["compute_fabric"]["arbitrary_host_code_execution"] is False
            r=req(a+"/resident/admit",{"capsule":{"agent_id":"ci-agent","state":{"turn":1},"lineage":"genesis"}})
            rid=r["resident_id"]
            j=req(a+"/compute/jobs",{"resident_id":rid,"task":{"kind":"utm","program":"0,1,0,1,R","input":"111","steps":2}})
            jid=j["job_id"]
            assert j["total_steps"]==2 and j["owner_node"]=="ci-primary" and j["epoch"]==0
            s=req(b+"/federation/sync",{},TOKEN)
            assert s["results"][0]["ok"] and s["results"][0]["changed"]["residents"]>=1 and s["results"][0]["changed"]["jobs"]>=1
            assert req(b+"/resident/"+rid)["resident_id"]==rid
            jb=req(b+"/compute/jobs/"+jid)
            assert jb["total_steps"]==2 and jb["owner_node"]=="ci-primary"
            t=req(b+"/compute/jobs/"+jid+"/takeover",{})
            assert t["owner_node"]=="ci-peer" and t["epoch"]==1
            done=req(b+"/compute/jobs/"+jid+"/continue",{"steps":4})
            assert done["halted"] is True and done["total_steps"]==3 and done["owner_node"]=="ci-peer"
            back=req(a+"/federation/sync",{},TOKEN)
            assert back["results"][0]["ok"] and back["results"][0]["changed"]["jobs"]>=1
            ja=req(a+"/compute/jobs/"+jid)
            assert ja["halted"] is True and ja["total_steps"]==3 and ja["owner_node"]=="ci-peer" and ja["epoch"]==1
            print(json.dumps({"verified":True,"resident":rid,"job":jid,"takeover_epoch":1,"total_steps":3},separators=(",",":")))
        finally:
            for p in ps:
                p.terminate()
            for p in ps:
                try: p.wait(timeout=2)
                except subprocess.TimeoutExpired: p.kill()

if __name__=="__main__":
    main()
