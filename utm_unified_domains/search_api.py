#!/usr/bin/env python3
import base64,hashlib,html,json,os,re,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import parse_qs,quote,quote_plus,urlparse
from urllib.request import Request,urlopen

MAXQ=512
MAX_BODY=65536
SNAPSHOT_DIR=os.getenv("SNAPSHOT_DIR","/tmp/utm-address-snapshots")

def enc(s):
    n=1
    for b in s.encode("utf-8"):
        n=n*257+b+1
    return str(n)

def dec(x):
    n=int(x);a=[]
    if n<1: raise ValueError("invalid address")
    while n>1:
        n,r=divmod(n,257)
        if not 1<=r<=256: raise ValueError("invalid address")
        a.append(r-1)
    return bytes(a[::-1]).decode("utf-8")

def canon(kind,value):
    if kind=="text":
        if not isinstance(value,str): raise ValueError("text value must be string")
        return "t:"+value
    if kind=="json":
        return "j:"+json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    if kind=="bytes":
        if not isinstance(value,str): raise ValueError("bytes value must be base64 string")
        raw=base64.b64decode(value,validate=True)
        return "b:"+base64.b64encode(raw).decode("ascii")
    raise ValueError("type must be text, json, or bytes")

def uncanon(c):
    if len(c)<2 or c[1]!=":": raise ValueError("invalid canonical object")
    k,v=c[0],c[2:]
    if k=="t": return "text",v
    if k=="j": return "json",json.loads(v)
    if k=="b":
        base64.b64decode(v,validate=True)
        return "bytes",v
    raise ValueError("invalid canonical object")

def obj(g):
    c=dec(g);kind,value=uncanon(c)
    return {"GOBJECT":str(g),"type":kind,"value":value,"canonical":c}

def snapshot_path(gs):
    return os.path.join(SNAPSHOT_DIR,gs+".json")

def write_snapshot(g,version,result=None):
    x=obj(g);identity="snapshot:"+version+":"+g;gs=enc(identity)
    rec={**x,"version":version,"GSNAPSHOT":gs,"created_at":int(time.time()),"result":result,"immutable_identity":True,"result_persistence":True}
    os.makedirs(SNAPSHOT_DIR,exist_ok=True)
    p=snapshot_path(gs)
    body=json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    digest=hashlib.sha256(body).hexdigest();rec["sha256"]=digest
    final=json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    try:
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
        with os.fdopen(fd,"w",encoding="utf-8") as f:f.write(final)
    except FileExistsError:
        old=json.load(open(p,encoding="utf-8"))
        if old.get("GOBJECT")!=str(g) or old.get("version")!=version:raise ValueError("snapshot identity collision")
        rec=old
    return rec

def read_snapshot(gs):
    p=snapshot_path(gs)
    with open(p,encoding="utf-8") as f:return json.load(f)

def search(q,site="",limit=8):
    z=("site:"+site+" " if site else "")+q
    t=urlopen(Request("https://html.duckduckgo.com/html/?q="+quote_plus(z),headers={"User-Agent":"Mozilla/5.0"}),timeout=12).read().decode("utf8","ignore")
    out=[]
    for m in re.finditer(r'href="([^"]+)"',t):
        u=html.unescape(m.group(1))
        if "uddg=" in u:u=parse_qs(urlparse(u).query).get("uddg",[u])[0]
        if not u.startswith("http") or (site and site not in u) or u in out:continue
        out.append(u)
        if len(out)>=limit:break
    return out

def logos(states,i="I",p="P",q="Q"):
    S=[x.strip() for x in states.split(",") if x.strip()]
    if not S or any(not re.fullmatch(r"[01]{2}",x) for x in S):raise ValueError("states must be comma-separated PQ bits, e.g. 11,01")
    poss="11" in S;ctr="10" in S;valid=not ctr
    return {"model":"UTM_LOGOS_V1","I":i,"P":p,"Q":q,"states":S,"possible_I":poss,"counterpossible_P_and_not_Q":ctr,"valid_P_implies_Q":valid,"logos_consistent":poss and valid,"formula":"◇(P∧Q) ∧ ¬◇(P∧¬Q)","scope":"finite-declared-model","metaphysical_proof":False}

class H(BaseHTTPRequestHandler):
    def j(self,x,c=200):
        b=json.dumps(x,ensure_ascii=False,separators=(",",":")).encode();self.send_response(c);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def base(self):
        proto=self.headers.get("X-Forwarded-Proto","https")
        return f"{proto}://{self.headers.get('Host','')}"
    def addressed(self,kind,value):
        c=canon(kind,value);g=enc(c)
        return {"type":kind,"value":value,"canonical":c,"GOBJECT":g,"utm_address":f"{self.base()}/object/{g}"}
    def do_POST(self):
        try:
            path=urlparse(self.path).path
            n=int(self.headers.get("Content-Length","0"))
            if n<1 or n>MAX_BODY:raise ValueError("invalid body length")
            p=json.loads(self.rfile.read(n))
            if not isinstance(p,dict):raise ValueError("body must be JSON object")
            if path=="/address":return self.j(self.addressed(p.get("type","json"),p.get("value")))
            if path=="/snapshot":
                g=str(p.get("GOBJECT",""));ver=str(p.get("version",""))
                if not g or not ver or len(ver)>128:raise ValueError("GOBJECT and version required")
                rec=write_snapshot(g,ver,p.get("result"));rec=dict(rec);rec["snapshot_address"]=f"{self.base()}/snapshot/{rec['GSNAPSHOT']}";return self.j(rec,201)
            return self.j({"error":"not found"},404)
        except Exception as e:self.j({"error":str(e)},400)
    def do_GET(self):
        u=urlparse(self.path);p=parse_qs(u.query)
        try:
            if u.path=="/health":return self.j({"ok":True,"snapshot_dir":SNAPSHOT_DIR})
            if u.path=="/":return self.j({"service":"UTM Universe Address + Search + Logos","usage":["/address?type=text&value=<value>","POST /address","/object/<GOBJECT>","/decode/<GOBJECT>","POST /snapshot","/snapshot/<GSNAPSHOT>","/search?q=<query>","/search/<GQUERY>","/logos?states=11,01&i=I&p=P&q=Q"]})
            if u.path=="/address":
                kind=p.get("type",["text"])[0];raw=p.get("value",[""])[0]
                value=json.loads(raw) if kind=="json" else raw
                return self.j(self.addressed(kind,value))
            if u.path.startswith("/object/") or u.path.startswith("/decode/"):
                g=u.path.split("/",2)[2];x=obj(g);x["utm_address"]=f"{self.base()}/object/{g}";return self.j(x)
            if u.path.startswith("/snapshot/"):
                gs=u.path.split("/",2)[2];x=read_snapshot(gs);x["snapshot_address"]=f"{self.base()}/snapshot/{gs}";return self.j(x)
            if u.path=="/logos":return self.j(logos(p.get("states",["11"])[0],p.get("i",["I"])[0],p.get("p",["P"])[0],p.get("q",["Q"])[0]))
            if u.path=="/search":q=p.get("q",[""])[0]
            elif u.path.startswith("/search/"):q=dec(u.path.split("/",2)[2])
            else:return self.j({"error":"not found"},404)
            if not q or len(q)>MAXQ:raise ValueError("invalid query")
            site=p.get("site",[""])[0];limit=max(1,min(int(p.get("limit",["8"])[0]),10));g=enc(q);c=canon("text",q);go=enc(c)
            self.j({"query":q,"GQUERY":g,"GOBJECT":go,"utm_address":f"{self.base()}/search/{g}","object_address":f"{self.base()}/object/{go}","live":True,"results":search(q,site,limit)})
        except FileNotFoundError:self.j({"error":"snapshot not found"},404)
        except Exception as e:self.j({"error":str(e)},400)

if __name__=="__main__":ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
