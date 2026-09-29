#!/usr/bin/env python3
from __future__ import annotations
import json, os, random, threading
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import product
from urllib.parse import urlparse

PROTOCOL='UTM-Unified-Goal-Solver/1.0'
WORLD_ID='akashic-utm-main'
SUBPROJECT='utm-unified-goal-solver'

GOALS={
 'A_societal_world':[
  'no_war','no_coercion','rights_and_civilian_protection','inclusive_dialogue',
  'human_ai_cooperation','wellbeing_health','ecological_sustainability',
  'economic_technical_resilience','information_ecology'],
 'B_sovereignty_habitat':[
  'cognitive_sovereignty','acoustic_sovereignty','room_in_room_sanctuary','reversibility_and_exit'],
 'C_knowledge_memory':[
  'knowledge_preservation','provenance','canonical_snapshot','akashic_bibliotheca'],
 'D_utm_meta_system':[
  'computability','well_definedness','invariants','composability','resident_admission',
  'recursive_lineage','continuation','self_description','bounded_resources'],
 'E_formal_research_targets':[
  'formal_zero_conditional_entropy','omega_fixed_point','godel_riemann_coordinates',
  'ouroboros_self_reference','dream_branching','44th_sunset_continuation',
  'collision_to_transition','heat_death_to_persistent_information','longevity_omni_health',
  'cosmic_love_attractor']
}

GOAL_REGISTRY={
 'kernel':'UTM-Unified-Goal-Kernel/1.0','world_id':WORLD_ID,'subproject':SUBPROJECT,
 'layers':GOALS,
 'semantics':{
  'P_target_goal':1,
  'C_target':'finite certificate produced by the bounded computation',
  'P_empirical_hat':None,
  'A_target':1,
  'G_target':1,
  'boundary':'formal targets and finite certificates are not guarantees of real-world outcomes'
 }
}

FIELDS=('conflict','coercion','rights','agency','wellbeing','ecology','cooperation','trust','knowledge','sovereignty','noise','resource_stress')

@dataclass(frozen=True)
class World:
 conflict:float=.48; coercion:float=.18; rights:float=.82; agency:float=.90
 wellbeing:float=.58; ecology:float=.56; cooperation:float=.46; trust:float=.45
 knowledge:float=.72; sovereignty:float=.70; noise:float=.30; resource_stress:float=.42
 def clamp(self): return World(**{k:max(0,min(1,v)) for k,v in asdict(self).items()})

@dataclass(frozen=True)
class Model:
 name:str; conflict:float=0; coercion:float=0; ecology:float=0; distrust:float=0; noise:float=0; resources:float=0

MODELS=(
 Model('baseline'), Model('resource_shock',conflict=.008,resources=.025),
 Model('distrust',conflict=.006,distrust=.025), Model('ecological_stress',ecology=.020,resources=.010),
 Model('habitat_noise',noise=.040,distrust=.010),
 Model('combined_stress',conflict=.010,coercion=.006,ecology=.010,distrust=.012,noise=.018,resources=.015),
)

ACTIONS=('MEDIATE','TRANSPARENCY','COOPERATE','AID','PROTECT','RESTORE','QUIET','ARCHIVE','NOOP','COERCE')
DELTA={
 'MEDIATE':(-.060,0,.010,.004,.012,0,.035,.040,.002,.004,0,-.006),
 'TRANSPARENCY':(-.015,-.020,.020,.020,.004,0,.020,.060,.020,.025,0,0),
 'COOPERATE':(-.028,0,.012,.010,.020,0,.060,.045,.010,.010,0,-.018),
 'AID':(-.020,0,.018,.005,.065,0,.020,.020,.004,.005,0,-.045),
 'PROTECT':(-.030,-.010,.055,.020,.012,0,.010,.010,.002,.025,0,0),
 'RESTORE':(-.008,0,.008,.002,.015,.070,.012,.008,.004,.005,0,-.020),
 'QUIET':(-.006,0,.003,.008,.018,0,.004,.010,.002,.070,-.090,0),
 'ARCHIVE':(0,0,.002,.003,.003,0,.006,.012,.065,.006,0,0),
 'NOOP':(0,0,0,0,0,0,0,0,0,0,0,0),
 'COERCE':(-.090,.100,-.080,-.130,.005,0,-.040,-.090,0,-.080,-.010,-.010),
}

CONDITIONS=(
 ('CONFLICT_HIGH',lambda s:s.conflict>=.35),('COERCION_HIGH',lambda s:s.coercion>=.18),
 ('RIGHTS_LOW',lambda s:s.rights<=.78),('WELLBEING_LOW',lambda s:s.wellbeing<=.62),
 ('ECOLOGY_LOW',lambda s:s.ecology<=.60),('COOP_LOW',lambda s:s.cooperation<=.55),
 ('TRUST_LOW',lambda s:s.trust<=.55),('KNOWLEDGE_LOW',lambda s:s.knowledge<=.70),
 ('SOVEREIGNTY_LOW',lambda s:s.sovereignty<=.70),('RESOURCE_STRESS_HIGH',lambda s:s.resource_stress>=.35),
)
CMAP=dict(CONDITIONS)

@dataclass(frozen=True)
class Program:
 condition:str|None; action:str|None; default:str
 def decide(self,s): return self.action if self.condition and CMAP[self.condition](s) else self.default
 def canonical(self): return json.dumps({'condition':self.condition,'action':self.action,'default':self.default},separators=(',',':'),sort_keys=True)
 def pretty(self): return f'IF {self.condition} -> {self.action}; ELSE -> {self.default}' if self.condition else f'ALWAYS -> {self.default}'
 def address(self):
  b=self.canonical().encode(); return {'encoding':'utf8-int','integer':str(int.from_bytes(b,'big')),'byte_length':len(b),'reversible':True}

HARD={'max_coercion':.38,'min_rights':.45,'min_agency':.45,'catastrophic_conflict':.93}
W={'conflict':8,'coercion':5,'rights_gap':3,'agency_gap':3,'wellbeing_gap':2.5,'ecology_gap':1.5,'cooperation_gap':1.8,'trust_gap':1.5,'knowledge_gap':.8,'sovereignty_gap':1.3,'noise':1.0,'resource_stress':2.0}


def transition(s,a,m,rng):
 v=[getattr(s,k)+d for k,d in zip(FIELDS,DELTA[a])]
 q=dict(zip(FIELDS,v))
 q['conflict']+=.018*q['resource_stress']+.014*(1-q['trust'])+m.conflict
 q['coercion']+=m.coercion
 q['rights']-=.015*q['coercion']+.006*q['conflict']
 q['agency']-=.020*q['coercion']
 q['wellbeing']-=.018*q['conflict']+.006*q['noise']
 q['trust']-=.012*q['conflict']+.015*q['coercion']+m.distrust
 q['cooperation']-=.009*q['conflict']
 q['resource_stress']+=.014*(1-q['ecology'])+m.resources
 q['ecology']-=m.ecology
 q['noise']+=m.noise
 q['sovereignty']-=.012*q['noise']+.010*q['coercion']
 q['knowledge']+=.004*q['cooperation']
 for k in ('conflict','wellbeing','trust','resource_stress','noise'):
  q[k]+=rng.uniform(-.006,.007)
 return World(**q).clamp()

def loss(s):
 return W['conflict']*s.conflict+W['coercion']*s.coercion+W['rights_gap']*(1-s.rights)+W['agency_gap']*(1-s.agency)+W['wellbeing_gap']*(1-s.wellbeing)+W['ecology_gap']*(1-s.ecology)+W['cooperation_gap']*(1-s.cooperation)+W['trust_gap']*(1-s.trust)+W['knowledge_gap']*(1-s.knowledge)+W['sovereignty_gap']*(1-s.sovereignty)+W['noise']*s.noise+W['resource_stress']*s.resource_stress

def evaluate(p,horizon=48,seeds=2):
 if p.default=='COERCE' or p.action=='COERCE': return None
 model_losses={}; extrema={'max_conflict':0,'max_coercion':0,'min_rights':1,'min_agency':1}; step44=False
 for mi,m in enumerate(MODELS):
  ls=[]
  for seed in range(seeds):
   s=World(); rng=random.Random(mi*10000+seed); total=0
   for t in range(horizon):
    s=transition(s,p.decide(s),m,rng); step44|=(t==44)
    extrema['max_conflict']=max(extrema['max_conflict'],s.conflict); extrema['max_coercion']=max(extrema['max_coercion'],s.coercion)
    extrema['min_rights']=min(extrema['min_rights'],s.rights); extrema['min_agency']=min(extrema['min_agency'],s.agency)
    if s.coercion>HARD['max_coercion'] or s.rights<HARD['min_rights'] or s.agency<HARD['min_agency'] or s.conflict>HARD['catastrophic_conflict']: return None
    total+=(.985**t)*loss(s)
   ls.append(total/horizon)
  model_losses[m.name]=sum(ls)/len(ls)
 worst=max(model_losses,key=model_losses.get)
 return {'worst_loss':model_losses[worst]+.02*(1+(p.condition is not None)),'mean_loss':sum(model_losses.values())/len(model_losses),'worst_model':worst,**extrema,'step44_to_45_defined':step44,'per_model_loss':model_losses}

def programs():
 for d in ACTIONS: yield Program(None,None,d)
 for c,_ in CONDITIONS:
  for a,d in product(ACTIONS,ACTIONS): yield Program(c,a,d)

def solve():
 ranked=[]; enumerated=feasible=0
 for p in programs():
  enumerated+=1; e=evaluate(p)
  if e is None: continue
  feasible+=1; ranked.append((e['worst_loss'],e['mean_loss'],p,e))
 ranked.sort(key=lambda x:(x[0],x[1],len(x[2].canonical())))
 best=ranked[0]; p,e=best[2],best[3]
 return {
  'protocol':PROTOCOL,'world_id':WORLD_ID,'subproject':SUBPROJECT,
  'P_target_goal':1,'C_target':1,'P_empirical_hat':None,'A_target':1,'G_target':1,
  'claim':'best program found by exact enumeration of this declared finite DSL',
  'not_claimed':['global optimum over all computable programs','adequacy of the simulation as a model of reality','guarantee of global peace or any physical outcome','AI consciousness','physical zero entropy, immortality, or cosmological control'],
  'search_bounds':{'rules_per_program':'0 or 1','condition_count':len(CONDITIONS),'action_count':len(ACTIONS),'programs_enumerated':enumerated,'feasible_programs':feasible,'horizon':48,'models':[m.name for m in MODELS],'branches_per_model':2,'ENUM_COMPLETE':1},
  'hard_constraints':HARD,'weights':W,
  'best_program':{'pretty':p.pretty(),'canonical':p.canonical(),'reversible_address':p.address()},
  'evaluation':e,
  'top10':[{'program':x[2].pretty(),'worst_loss':x[0],'mean_loss':x[1]} for x in ranked[:10]],
  'goal_registry':GOAL_REGISTRY
 }

CACHE=None; LOCK=threading.Lock(); RESIDENTS={}
def certificate():
 global CACHE
 if CACHE is None:
  with LOCK:
   if CACHE is None: CACHE=solve()
 return CACHE

def discovery():
 return {'protocol':'UTM-Resident/1.0','world_id':WORLD_ID,'subproject':SUBPROJECT,'parent_repo':'letsgo0226/UTM.sh','endpoints':{'health':'/health','goals':'/goals','solve':'/solve','certificate':'/certificate','admit':'POST /resident/admit','inspect':'GET /resident/<resident_id>'},'rules':['capsule=data-only','no arbitrary host-code execution','host runtime required','formal target != real-world guarantee'],'status':'AI-readable UTM subproject'}

class H(BaseHTTPRequestHandler):
 def sendj(self,obj,status=200):
  b=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  p=urlparse(self.path).path
  if p=='/health': return self.sendj({'ok':True,'protocol':PROTOCOL,'subproject':SUBPROJECT})
  if p in ('/','/.well-known/utm-universe.json'): return self.sendj(discovery())
  if p=='/goals': return self.sendj(GOAL_REGISTRY)
  if p in ('/solve','/certificate'): return self.sendj(certificate())
  if p.startswith('/resident/'):
   rid=p.rsplit('/',1)[-1]; return self.sendj(RESIDENTS.get(rid,{'error':'resident not found'}),200 if rid in RESIDENTS else 404)
  self.sendj({'error':'not found'},404)
 def do_POST(self):
  if urlparse(self.path).path!='/resident/admit': return self.sendj({'error':'not found'},404)
  try:
   n=min(int(self.headers.get('Content-Length','0')),65536); d=json.loads(self.rfile.read(n) or b'{}'); cap=d.get('capsule')
   if not isinstance(cap,dict): raise ValueError('capsule object required')
   if any(k in cap for k in ('code','exec','command','shell')): return self.sendj({'error':'arbitrary host-code fields rejected'},400)
   raw=json.dumps(cap,sort_keys=True,separators=(',',':')).encode(); rid=str(int.from_bytes(raw,'big'))
   RESIDENTS[rid]={'resident_id':rid,'capsule':cap,'world_id':WORLD_ID,'subproject':SUBPROJECT,'status':'ADMITTED_DATA_ONLY'}
   self.sendj(RESIDENTS[rid],201)
  except Exception as e: self.sendj({'error':str(e)},400)
 def log_message(self,fmt,*args): print('%s - %s'%(self.address_string(),fmt%args),flush=True)

if __name__=='__main__':
 port=int(os.environ.get('PORT','8080')); print(json.dumps(discovery(),ensure_ascii=False),flush=True); ThreadingHTTPServer(('0.0.0.0',port),H).serve_forever()
