import json, re
from pathlib import Path
import networkx as nx
DATA=Path(__file__).resolve().parents[1]/'data'/'skills.json'
ALIASES={}
GRAPH=nx.Graph()
try:
    ITEMS=json.loads(DATA.read_text(encoding='utf8'))
except Exception: ITEMS=[]
for item in ITEMS:
    name=item['canonical_name']; GRAPH.add_node(name,category=item.get('category','other'))
    for alias in [name,*item.get('aliases',[])]: ALIASES[alias.lower()]=name
    for rel in item.get('relations',[]):
        target=rel.get('target')
        GRAPH.add_node(target); GRAPH.add_edge(name,target,relation=rel.get('type','related_to'))
def canonicalize(text:str)->str|None:
    t=text.lower().strip()
    if t in ALIASES:return ALIASES[t]
    for alias,name in sorted(ALIASES.items(),key=lambda x:-len(x[0])):
        if len(alias)>2 and re.search(r'(?<![a-z0-9])'+re.escape(alias)+r'(?![a-z0-9])',t):return name
    return None
def path_between(a:str,b:str):
    if a not in GRAPH or b not in GRAPH:return []
    try:
        p=nx.shortest_path(GRAPH,a,b)
        return p if len(p)<=4 else []
    except (nx.NetworkXNoPath,nx.NodeNotFound):return []
