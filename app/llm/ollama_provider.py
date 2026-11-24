class OllamaProvider:
 def __init__(self,model):self.model=model or 'llama3.1'
 def extract_json(self,prompt,schema):
  import urllib.request,json
  req=urllib.request.Request('http://localhost:11434/api/generate',data=json.dumps({'model':self.model,'prompt':prompt,'format':'json','stream':False}).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=90) as r:return json.loads(json.loads(r.read())['response'])
