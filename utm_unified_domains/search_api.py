#!/usr/bin/env python3
import json,os,re,html
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs,quote,quote_plus,parse_qs as PQ
from urllib.request import Request,urlopen

MAXQ=512
def enc(s):
 n=1
 for b in s.encode():n=n*257+b+1
 return str(n)
def dec(x):
 n=int(x);a=[]
 while n>1:
  n,r=divmod(n,257)
  if not 1<=r<=256:raise ValueError("invalid address")
  a.append(r-1)
 return bytes(a[::-1]).decode()
def search(q,site="",limit=8):
 z=("site:"+site+" " if site else "")+q
 t=urlopen(Request("https://html.duckduckgo.com/html/?q="+quote_plus(z),headers={"User-Agent":"Mozilla/5.0"}),timeout=12).read().decode("utf8","ignore")
 out=[]
 for m in re.finditer(r'href="([^"]+)"',t):
  u=html.unescape(m.group(1))
  if "uddg=" in u:u=PQ(urlparse(u).query).get("uddg",[u])[0]
  if not u.startswith("http") or (site and site not in u) or u in out:continue
  out.append(u)
  if len(out)>=limit:break
 return out
class H(BaseHTTPRequestHandler):
 def j(self,x,c=200):
  b=json.dumps(x,ensure_ascii=False,separators=(",",":")).encode();self.send_response(c);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=parse_qs(u.query)
  try:
   if u.path=="/health":return self.j({"ok":True})
   if u.path=="/":return self.j({"service":"UTM Addressable Search","usage":"/search?q=<query> or /search/<GQUERY>"})
   if u.path=="/search":q=p.get("q",[""])[0]
   elif u.path.startswith("/search/"):q=dec(u.path.split("/",2)[2])
   else:return self.j({"error":"not found"},404)
   if not q or len(q)>MAXQ:raise ValueError("invalid query")
   site=p.get("site",[""])[0];limit=max(1,min(int(p.get("limit",["8"])[0]),10));g=enc(q)
   proto=self.headers.get("X-Forwarded-Proto","https");host=self.headers.get("Host","")
   a=f"{proto}://{host}/search/{g}"+(("?site="+quote(site)) if site else "")
   self.j({"query":q,"GQUERY":g,"utm_address":a,"live":True,"results":search(q,site,limit)})
  except Exception as e:self.j({"error":str(e)},400)
if __name__=="__main__":ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","8080"))),H).serve_forever()
