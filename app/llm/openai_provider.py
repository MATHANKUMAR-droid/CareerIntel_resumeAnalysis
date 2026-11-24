class OpenAIProvider:
 def __init__(self,key,model):self.key,self.model=key,model
 def extract_json(self,prompt,schema):
  from openai import OpenAI
  import json
  r=OpenAI(api_key=self.key).chat.completions.create(model=self.model or 'gpt-4o-mini',response_format={'type':'json_object'},messages=[{'role':'user','content':prompt}])
  return json.loads(r.choices[0].message.content)
